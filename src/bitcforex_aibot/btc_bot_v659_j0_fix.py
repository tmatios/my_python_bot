#!/usr/bin/env python3
# V659-J0-FIX: signal-only J0 paper observer; fixed settings and route exclusions.
# V623-inspired paper signal observer. No imports of live trading code and no order API.
import argparse, csv, datetime as dt, json, math, os, sqlite3, statistics, time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo('Asia/Tokyo')
ROOT = Path(__file__).resolve().parent

def load_env(path):
    if not path.exists(): return
    for raw in path.read_text(encoding='utf-8-sig').splitlines():
        line=raw.strip()
        if not line or line.startswith('#'): continue
        if line.startswith('export '): line=line[7:].strip()
        if '=' not in line: continue
        k,v=line.split('=',1); k=k.strip(); v=v.strip()
        if not k.isidentifier(): continue
        if len(v)>1 and v[0] in ('"',"'") and v[-1]==v[0]: v=v[1:-1]
        os.environ.setdefault(k,v)

# Freeze the J0 parameters, irrespective of older bot.env overrides.
J0_FIXED = {
    'PAPER_LOT_BTC': 0.05,
    'PAPER_STOP_LOSS_JPY': 500,
    'PAPER_TRAIL_START_JPY': 350,
    'PAPER_TRAIL_WIDTH_JPY': 150,
    'PAPER_BREAKEVEN_TRIGGER_JPY': 300,
    'PAPER_BREAKEVEN_FLOOR_JPY': 0,
    'PAPER_DAILY_ENTRY_CAP': 10,
    'V657_ENABLE_BIG_WAVE': 1,
    'V657_ENABLE_BIG_WAVE_PRE_SMA': 0,
    'V659B_ENABLE_TREND_REACCEL': 0,
}
J0_FORBIDDEN = frozenset({('BIG_WAVE', 'LONG'), ('BB_REENTRY_V654', 'LONG')})
J0_DAILY_LOSS_LIMIT_JPY = 1750.0

def cfg(name, default, cast=float):
    if name in J0_FIXED:
        return cast(J0_FIXED[name])
    try: return cast(os.getenv(name,str(default)))
    except (ValueError,TypeError): return default

def now(): return dt.datetime.now(JST)
def session_day(t): return (t-dt.timedelta(days=1)).date() if t.hour<9 else t.date()
def close_calendar_day(r):
    stamp=dt.datetime.fromisoformat(r['exit_at'])
    if stamp.tzinfo is None: raise ValueError('exit_at must have timezone')
    return stamp.astimezone(JST).date()

def close_session(r):
    """09:00 JST boundary, attributed to realized CLOSE, not ENTRY."""
    stamp=dt.datetime.fromisoformat(r['exit_at'])
    if stamp.tzinfo is None:
        raise ValueError('exit_at must have timezone')
    return session_day(stamp.astimezone(JST))

# Every closed trade is valid, regardless of realized loss. Legacy report_status is ignored.
def yen_round(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def invalid_trade_status(r):
    return 'COUNTED'

def valid_trades(trades):
    return list(trades)

def session_closed_trades(trades, day):
    return sorted((r for r in trades if close_session(r).isoformat()==day),
                  key=lambda r:r['exit_at'])

def entry_dd_gate(trades, t):
    """Return (allowed, reason); daily loss uses ALL realized CLOSEs in JST calendar day."""
    day=t.astimezone(JST).date()
    daily_closed=[r for r in trades if close_calendar_day(r)==day]
    daily_net=sum(float(r['net_pnl_jpy']) for r in daily_closed)
    limit=max(0.0, cfg('PAPER_DAILY_LOSS_LIMIT_JPY',5000.0))
    if limit>0 and daily_net<=-limit:
        return False,(f'日次損失上限: {day.isoformat()} 全確定損益 '
                      f'{daily_net:+.2f}円 <= -{limit:.0f}円 (新規ENTRY停止)')
    # V642: no losing-streak or DD caution cooldown; only hard daily loss limit.
    return True,''

def sma(a,n): return sum(a[-n:])/n if len(a)>=n else None
def wma(a,n):
    if len(a)<n: return None
    return sum(v*i for i,v in enumerate(a[-n:],1))/(n*(n+1)/2)
def hma(a,n):
    half=n//2; sq=max(2,int(math.sqrt(n)))
    if len(a)<n+sq: return None
    diff=[]
    for i in range(sq,0,-1):
        sub=a[:len(a)-i+1]
        diff.append(2*wma(sub,half)-wma(sub,n))
    return wma(diff,sq)
def rsi(a,n=14):
    if len(a)<n+1: return 50
    ds=[a[i]-a[i-1] for i in range(len(a)-n,len(a))]
    up=sum(max(x,0) for x in ds)/n; down=sum(max(-x,0) for x in ds)/n
    return 100 if down==0 else 100-100/(1+up/down)

def read_prices(db):
    uri=f'file:{db.resolve()}?mode=ro'
    with sqlite3.connect(uri,uri=True,timeout=5) as c:
        rows=c.execute('SELECT ts,price FROM prices_crypto_cfd ORDER BY ts DESC LIMIT 15000').fetchall()
    out=[]
    for stamp,price in reversed(rows):
        try:
            t=dt.datetime.fromisoformat(stamp)
            if t.tzinfo is None: continue
            if math.isfinite(float(price)) and float(price)>0: out.append((t.astimezone(JST),float(price)))
        except (ValueError,TypeError): continue
    return out

def bars(prices, minutes):
    buckets={}
    for t,p in prices:
        epoch=int(t.timestamp()); k=epoch//(minutes*60)
        buckets[k]=(t,p)
    return [v[1] for k,v in sorted(buckets.items())]

def recent_tick_risk(prices, t, lot=0.05):
    """Observed sampling gaps and recent shock, in JPY PnL per fixed paper lot.

    This is an entry filter, NOT a guarantee of stop execution or slippage.
    """
    lookback=max(30, cfg('PAPER_SHOCK_WINDOW_SEC',180,int))
    recent=[(ts,price) for ts,price in prices if 0 <= (t-ts).total_seconds() <= lookback]
    if len(recent)<2:
        return None
    jumps=[abs(recent[i][1]-recent[i-1][1])*lot for i in range(1,len(recent))]
    excursion=(max(p for _,p in recent)-min(p for _,p in recent))*lot
    return {'max_jump_jpy':max(jumps,default=0), 'range_jpy':excursion,
            'last_move_jpy':(recent[-1][1]-recent[0][1])*lot,
            'samples':len(recent)}

def v657_tick_jump_limit(prices, risk):
    """Bounded opt-in tolerance for NORMAL sampled moves, not bad data.

    Never disable the hard cap. A wider limit is permitted only with dense
    recent samples; this is a heuristic, NOT exchange-price verification.
    """
    base=cfg('PAPER_ENTRY_MAX_TICK_JUMP_JPY',180)
    if not cfg('V657_ADAPTIVE_JUMP_ENABLE',0,int) or risk is None:
        return base
    lookback=max(30,cfg('PAPER_SHOCK_WINDOW_SEC',180,int))
    t=prices[-1][0]
    recent=[ts for ts,_ in prices if 0 <= (t-ts).total_seconds() <= lookback]
    if len(recent)<3:
        return base
    gaps=[(recent[i]-recent[i-1]).total_seconds() for i in range(1,len(recent))]
    if any(g<=0 or g>cfg('V657_MAX_SAMPLE_GAP_SEC',90) for g in gaps):
        return base
    hard=cfg('V657_ADAPTIVE_JUMP_HARD_CAP_JPY',300)
    if hard<=0:
        return base
    return max(0,min(max(base,hard),hard))

def signal(prices):
    """Return decision plus auditable route-by-route reasons for the journal."""
    a=bars(prices,5); b=bars(prices,60); c=bars(prices,15)
    if len(a)<55 or len(b)<55:
        return None, f'データ不足: 5分足={len(a)}/55本、1時間足={len(b)}/55本'
    p=a[-1]; s=sma(a,20); w=wma(a,20); prev_s=sma(a[:-1],20); prev_w=wma(a[:-1],20)
    h=hma(b,34); hp=hma(b[:-1],34); h1s=sma(b,20); h1prev=sma(b[:-1],20)
    if not all(x is not None and x>0 for x in (s,w,prev_s,prev_w,h,hp,h1s,h1prev)):
        return None,'指標不足: SMA20/WMA20/HMA34を算出できません'
    slope=(h-hp)/hp; mom1=a[-1]/a[-2]-1; mom3=a[-1]/a[-4]-1
    rs=rsi(a); stdev=statistics.pstdev(a[-20:]); upper=s+2*stdev; lower=s-2*stdev
    vol=statistics.pstdev([a[i]/a[i-1]-1 for i in range(-24,0)]) if len(a)>=25 else 0
    score_min=cfg('PAPER_SCORE_MIN',90,int)
    # Risk filter: suppress entries when 5m volatility is insufficient.
    min_vol=cfg('PAPER_ENTRY_MIN_VOL',0.0005)
    medium_min=cfg('PAPER_MEDIUM_MIN_VOL',0.00030)
    medium_max=min_vol
    medium_vol=medium_min<=vol<medium_max
    high_vol=vol>=medium_max
    # Mid-volatility entries require independent 15m confirmation and a fresh 5m impulse.
    c_s=sma(c,10); c_prev=sma(c[:-1],10)
    c_mom=c[-1]/c[-2]-1 if len(c)>1 else 0.0
    recent_range=(max(a[-7:-1])-min(a[-7:-1]))/p
    last_impulse=abs(mom1)
    # Conservative cost-aware stop risk: reject setups whose configured stop exceeds budget.
    stop_risk=cfg('PAPER_STOP_LOSS_JPY',500)+cfg('PAPER_COST_JPY_PER_TRADE',0)
    max_risk=cfg('PAPER_MAX_ENTRY_RISK_JPY',650)
    min_short_rsi=cfg('PAPER_SHORT_MIN_RSI',30.0)
    max_long_rsi=cfg('PAPER_LONG_MAX_RSI',70.0)
    # V644: reject fast spikes where a sampled STOP can be overshot.
    tick_risk=recent_tick_risk(prices,prices[-1][0])
    shock_max_jump=v657_tick_jump_limit(prices,tick_risk)
    shock_max_range=cfg('PAPER_ENTRY_MAX_3M_RANGE_JPY',450)
    chase_max=cfg('PAPER_ENTRY_MAX_3M_CHASE_JPY',220)
    candidates=[]; checks=[]
    for side,sgn in [('LONG',1),('SHORT',-1)]:
        # V642: shared risk gates for every entry route.
        risk_fail=[]
        if tick_risk is not None:
            if shock_max_jump>0 and tick_risk['max_jump_jpy']>shock_max_jump:
                risk_fail.append(f'短時間価格飛び({tick_risk["max_jump_jpy"]:.0f}>{shock_max_jump:.0f}円/0.05BTC)')
            # V656-A: 短時間急変動によるENTRY禁止のみ解除
            # 他のリスク判定は維持する
            # if shock_max_range>0 and tick_risk['range_jpy']>shock_max_range:
            #     risk_fail.append(f'短時間急変動({tick_risk["range_jpy"]:.0f}>{shock_max_range:.0f}円/0.05BTC)')
            if chase_max>0 and sgn*tick_risk['last_move_jpy']>chase_max:
                risk_fail.append(f'直近急伸急落への追随({sgn*tick_risk["last_move_jpy"]:.0f}>{chase_max:.0f}円/0.05BTC)')
        if vol < medium_min: risk_fail.append(f'低ボラ({vol*100:.4f}%<{medium_min*100:.4f}%)')
        if max_risk>0 and stop_risk>max_risk: risk_fail.append(f'想定損失過大({stop_risk:.0f}>{max_risk:.0f}円)')
        if medium_vol:
            if c_s is None or c_prev is None or not (sgn*(c[-1]-c_s)>0 and sgn*(c_s-c_prev)>0 and sgn*c_mom>0):
                risk_fail.append('中ボラ15分足方向不一致')
            if sgn*mom1<cfg('PAPER_MEDIUM_MIN_MOM1',0.00015) or sgn*mom3<cfg('PAPER_MEDIUM_MIN_MOM3',0.00025):
                risk_fail.append('中ボラ5分足再加速不足')
            if recent_range<cfg('PAPER_MEDIUM_MIN_RANGE',0.0007): risk_fail.append('中ボラ直近値幅不足')
        if side=='SHORT' and rs < min_short_rsi: risk_fail.append(f'RSI売られ過ぎ({rs:.1f}<{min_short_rsi:.1f})')
        if side=='LONG' and rs > max_long_rsi: risk_fail.append(f'RSI買われ過ぎ({rs:.1f}>{max_long_rsi:.1f})')
        # V632: 1h SMA20 and HMA34 define primary direction; 5m confirms timing.
        h1_ok=(sgn*(b[-1]-h1s)>0 and sgn*(h1s-h1prev)>0 and sgn*slope>0)
        align=sgn*(p-s)>0 and sgn*(p-w)>0 and sgn*(s-prev_s)>0 and sgn*(w-prev_w)>0
        hm_ok=sgn*slope>=-cfg('PAPER_HMA_OPPOSITE_TOLERANCE',0.00012)
        momentum=sgn*mom1>0 and sgn*mom3>0
        distance=abs(p-s)/p
        normal_score=min(100,80+min(10,abs(mom3)*18000)+min(6,abs(slope)*15000)+(4 if 38<=rs<=68 else 0))
        normal_fail=list(risk_fail)
        if not h1_ok: normal_fail.append('1時間足SMA20/HMA34トレンド不一致')
        if not align: normal_fail.append('SMA/WMA方向不一致')
        if not hm_ok: normal_fail.append('1時間HMA逆行')
        if not momentum: normal_fail.append('mom1/mom3方向不一致')
        if distance>cfg('PAPER_MAX_MA_DISTANCE',0.0024): normal_fail.append(f'MA乖離超過({distance*100:.3f}%)')
        if normal_score<score_min: normal_fail.append(f'スコア不足({normal_score:.1f}<{score_min})')
        if not normal_fail: candidates.append((normal_score,side,'NORMAL'))
        checks.append(f'{side}/NORMAL: '+('成立' if not normal_fail else '・'.join(normal_fail)))
        big_fail=list(risk_fail)
        if sgn*mom1<cfg('ACTIVE_BIG_WAVE_MIN_MOM1_PCT',0.00025): big_fail.append('mom1不足')
        if sgn*mom3<cfg('ACTIVE_BIG_WAVE_MIN_MOM3_PCT',0.00045): big_fail.append('mom3不足')
        if not h1_ok: big_fail.append('1時間足SMA20/HMA34トレンド不一致')
        if not hm_ok: big_fail.append('1時間HMA逆行')
        if vol<cfg('PAPER_BIG_WAVE_MIN_VOL',0.00025): big_fail.append('ボラ不足')
        big_score=min(100,89+abs(mom1)*20000+abs(mom3)*5000)
        if big_score<score_min: big_fail.append(f'スコア不足({big_score:.1f}<{score_min})')
        if not big_fail: candidates.append((big_score,side,'BIG_WAVE'))
        checks.append(f'{side}/BIG_WAVE: '+('成立' if not big_fail else '・'.join(big_fail)))
        recent_outside=min(a[-6:-1])<lower if sgn==1 else max(a[-6:-1])>upper
        reenter=p>lower if sgn==1 else p<upper
        dev=abs(p-s)/s; decel=sgn*mom1>0 and sgn*mom3<0
        rev_fail=list(risk_fail)
        if not h1_ok: rev_fail.append('1時間足トレンド逆行')
        if not recent_outside: rev_fail.append('直近BB外側到達なし')
        if not reenter: rev_fail.append('BB内側への回帰なし')
        if dev<cfg('ACTIVE_MEAN_REVERSION_MIN_SMA_DEV_PCT',0.003): rev_fail.append(f'SMA乖離不足({dev*100:.3f}%)')
        if not decel: rev_fail.append('モメンタム反転条件不一致')
        rev_score=min(100,90+dev*1000)
        if rev_score<score_min: rev_fail.append(f'スコア不足({rev_score:.1f}<{score_min})')
        if not rev_fail: candidates.append((rev_score,side,'MEAN_REVERSION'))
        checks.append(f'{side}/MEAN_REVERSION: '+('成立' if not rev_fail else '・'.join(rev_fail)))
        # V634: SMA20 separation as a *precursor* to a large move.
        # Use the first recovery/expansion after a narrow SMA distance, not a late chase.
        prev_gap=abs(a[-2]-prev_s)/prev_s
        current_gap=abs(p-s)/s
        wave_fail=list(risk_fail)
        if not h1_ok: wave_fail.append('1時間足トレンド不一致')
        if not momentum: wave_fail.append('短期モメンタム不一致')
        if not align: wave_fail.append('5分足MA方向不一致')
        if prev_gap>cfg('PAPER_WAVE_PRE_MAX_PREV_SMA_GAP',0.0010): wave_fail.append('予兆前のSMA乖離過大')
        if current_gap<cfg('PAPER_WAVE_PRE_MIN_SMA_GAP',0.0005): wave_fail.append('SMA乖離拡大不足')
        if current_gap<=prev_gap: wave_fail.append('SMA乖離が拡大していない')
        if current_gap>cfg('PAPER_WAVE_PRE_MAX_SMA_GAP',0.0020): wave_fail.append('SMA乖離が大きすぎる')
        if vol<cfg('PAPER_BIG_WAVE_MIN_VOL',0.00025): wave_fail.append('ボラ不足')
        # Require a pullback then renewed movement, rather than chasing an extended bar.
        # Completed prior 5m bar must have moved against the intended direction.
        if sgn*(a[-2]-a[-3])>=0: wave_fail.append('直前5分足の押し戻りなし')
        if sgn*(p-a[-2])<=0: wave_fail.append('押し戻り後の再加速なし')
        wave_score=min(100,91+current_gap*3500+abs(mom3)*2500)
        if not wave_fail: candidates.append((wave_score,side,'BIG_WAVE_PRE_SMA'))
        checks.append(f'{side}/BIG_WAVE_PRE_SMA: '+('成立' if not wave_fail else '・'.join(wave_fail)))
        # V643: independent early breakout route, without requiring a preceding pullback.
        # Use prior closed-bar range to avoid a look-ahead breakout comparison.
        early_fail=list(risk_fail)
        breakout_level=max(a[-7:-1]) if sgn==1 else min(a[-7:-1])
        if sgn*(p-breakout_level) <= cfg('PAPER_EARLY_BREAKOUT_BUFFER',0.00005)*p:
            early_fail.append('直近6本高安値ブレイクなし')
        if not align: early_fail.append('5分足SMA/WMA方向不一致')
        if not momentum: early_fail.append('短期モメンタム不一致')
        if not (h1_ok or (medium_vol and hm_ok)):
            early_fail.append('1時間足方向または許容傾き不一致')
        if current_gap>cfg('PAPER_EARLY_MAX_SMA_GAP',0.0015): early_fail.append('SMAからの追随乖離過大')
        if sgn*mom1<cfg('PAPER_EARLY_MIN_MOM1',0.00018): early_fail.append('初動勢い不足')
        early_score=min(100,90+max(0,sgn*mom1)*15000+max(0,sgn*mom3)*5000)
        if not early_fail: candidates.append((early_score,side,'EARLY_BREAKOUT'))
        checks.append(f'{side}/EARLY_BREAKOUT: '+('成立' if not early_fail else '・'.join(early_fail)))

        # V643: 15m/5m turn entry before hourly trend fully changes.
        turn_fail=list(risk_fail)
        if c_s is None or c_prev is None or not (sgn*(c[-1]-c_s)>0 and sgn*(c_s-c_prev)>0 and sgn*c_mom>0):
            turn_fail.append('15分足転換未確認')
        if not align or not momentum: turn_fail.append('5分足方向/勢い不一致')
        if sgn*slope < -cfg('V657_TURN_HMA_TOLERANCE',cfg('PAPER_HMA_OPPOSITE_TOLERANCE',0.00012)): turn_fail.append('1時間HMA逆行過大')
        if sgn*mom1<cfg('PAPER_TURN_MIN_MOM1',0.00018): turn_fail.append('転換初動不足')
        if current_gap>cfg('PAPER_TURN_MAX_SMA_GAP',0.0015): turn_fail.append('転換後の追随乖離過大')
        if not (sgn*(a[-2]-a[-3])<=0 or sgn*(p-breakout_level)>0):
            turn_fail.append('押し戻り/ブレイク未確認')
        turn_score=min(100,90+max(0,sgn*mom1)*14000+max(0,sgn*c_mom)*5000)
        if not turn_fail: candidates.append((turn_score,side,'MTF_15M_TURN'))
        checks.append(f'{side}/MTF_15M_TURN: '+('成立' if not turn_fail else '・'.join(turn_fail)))


        # V634: mean reversion after a genuine outer Bollinger excursion.
        # Compare each previous price to its own contemporaneous BB, not today's band.
        bb_fail=list(risk_fail)
        excursions=[]
        for idx in range(len(a)-6,len(a)-1):
            window=a[idx-19:idx+1]
            if len(window)<20: continue
            mid=statistics.mean(window)
            sigma=statistics.pstdev(window)
            band=(mid-2*sigma) if sgn==1 else (mid+2*sigma)
            outside=(band-a[idx])/band if sgn==1 else (a[idx]-band)/band
            excursions.append(outside)
        max_outside=max(excursions,default=-1)
        min_outside=cfg('PAPER_BB_REV_MIN_OUTSIDE_PCT',0.00015)
        if max_outside<min_outside: bb_fail.append('BB外側への乖離不足')
        # Price has to be back *inside* the currently computed band.
        if (p<=lower if sgn==1 else p>=upper): bb_fail.append('BB内側への戻りなし')
        if sgn*mom1<=0: bb_fail.append('5分足反転モメンタムなし')
        if sgn*(p-a[-2])<=0: bb_fail.append('反転足なし')
        # Keep genuine counter-trend entries possible, but reject strong opposing hourly trends.
        max_opp=cfg('PAPER_BB_REV_MAX_OPPOSITE_H1_SLOPE',0.00035)
        if sgn*slope < -max_opp: bb_fail.append('1時間足逆行が強すぎる')
        # Require separation from SMA at excursion, not necessarily after the rebound.
        recent_devs=[abs(a[i]-statistics.mean(a[i-19:i+1]))/statistics.mean(a[i-19:i+1])
                     for i in range(len(a)-6,len(a)-1)]
        if max(recent_devs,default=0)<cfg('PAPER_BB_REV_MIN_SMA_DEVIATION',0.0025):
            bb_fail.append('SMA20乖離不足')
        bb_score=min(100,91+max(0,max_outside)*6000)
        if not bb_fail: candidates.append((bb_score,side,'BB_OUTER_REVERSION'))
        checks.append(f'{side}/BB_OUTER_REVERSION: '+('成立' if not bb_fail else '・'.join(bb_fail)))
        # V649: a separate, confirmed countertrend route for fast volatility shocks.
        # The normal shock gate remains unchanged for all other routes.
        # 5m values are sampled prices (not exchange OHLC); use price direction
        # as a proxy for a reversal, and require both RSI exhaustion and BB reentry.
        shock_rev_fail=[]
        prior_rsi=rsi(a[:-1])
        rsi_threshold=cfg('PAPER_SHOCK_REV_SHORT_RSI',75.0) if sgn==-1 else cfg('PAPER_SHOCK_REV_LONG_RSI',25.0)
        if sgn==-1 and prior_rsi<rsi_threshold:
            shock_rev_fail.append(f'直前RSI過熱不足({prior_rsi:.1f}<{rsi_threshold:.1f})')
        if sgn==1 and prior_rsi>rsi_threshold:
            shock_rev_fail.append(f'直前RSI売られ過ぎ不足({prior_rsi:.1f}>{rsi_threshold:.1f})')
        if max_outside<cfg('PAPER_SHOCK_REV_MIN_BB_OUTSIDE',0.00015):
            shock_rev_fail.append('直近BB2σ外側への到達不足')
        if (p<=lower if sgn==1 else p>=upper):
            shock_rev_fail.append('BB内側への復帰なし')
        # Require 5m direction reversal and reversal momentum.
        if sgn*(p-a[-2])<=0 or sgn*mom1<=0:
            shock_rev_fail.append('5分足反転方向未確認')
        if sgn*(a[-2]-a[-3])>=0:
            shock_rev_fail.append('直前足が逆方向に伸びていない')
        if sgn*slope < -cfg('PAPER_SHOCK_REV_MAX_OPPOSITE_H1_SLOPE',0.00050):
            shock_rev_fail.append('1時間足逆行が強すぎる')
        if vol<cfg('PAPER_SHOCK_REV_MIN_VOL',0.00050):
            shock_rev_fail.append('急変動逆張り用ボラ不足')
        if max_risk>0 and stop_risk>max_risk:
            shock_rev_fail.append('想定損失過大')
        # Permit moderate shocks only. Never bypass an extreme sampled jump,
        # where the paper stop can be severely overshot.
        if tick_risk is None:
            shock_rev_fail.append('直近価格サンプル不足')
        else:
            hard_jump=cfg('PAPER_SHOCK_REV_HARD_MAX_TICK_JUMP_JPY',450.0)
            hard_range=cfg('PAPER_SHOCK_REV_HARD_MAX_3M_RANGE_JPY',900.0)
            if hard_jump>0 and tick_risk['max_jump_jpy']>hard_jump:
                shock_rev_fail.append(f'極端な価格飛び({tick_risk["max_jump_jpy"]:.0f}>{hard_jump:.0f}円)')
            if hard_range>0 and tick_risk['range_jpy']>hard_range:
                shock_rev_fail.append(f'極端な3分値幅({tick_risk["range_jpy"]:.0f}>{hard_range:.0f}円)')
        # Require a reversal away from the recent outer-band excursion,
        # rather than entering solely because RSI is overbought/oversold.
        recent_extreme=max(a[-6:-1]) if sgn==-1 else min(a[-6:-1])
        reversal_jpy=sgn*(p-recent_extreme)*cfg('PAPER_LOT_BTC',0.05)
        if reversal_jpy<cfg('PAPER_SHOCK_REV_MIN_RETRACE_JPY',80.0):
            shock_rev_fail.append('高安値からの反転幅不足')
        shock_rev_score=min(100,92+max(0,max_outside)*6000+max(0,reversal_jpy)*0.01)
        if shock_rev_score<score_min:
            shock_rev_fail.append('スコア不足')
        if not shock_rev_fail:
            candidates.append((shock_rev_score,side,'SHOCK_BB_RSI_REVERSAL'))
        checks.append(f'{side}/SHOCK_BB_RSI_REVERSAL: '+('成立' if not shock_rev_fail else '・'.join(shock_rev_fail)))
    detail=(f'価格={p:,.0f} RSI={rs:.1f} HMA傾き={slope*100:.4f}% '
            f'mom1={mom1*100:.4f}% mom3={mom3*100:.4f}% vol={vol*100:.4f}% regime={"HIGH" if high_vol else "MEDIUM" if medium_vol else "LOW"} '
            + ' | '.join(checks))
    # V656-A fix: exclude disabled routes BEFORE ranking; otherwise a disabled
    # higher-scoring candidate can mask an eligible lower-scoring route.
    disabled_routes=set()
    if not cfg('V657_ENABLE_BIG_WAVE',0,int): disabled_routes.add('BIG_WAVE')
    if not cfg('V657_ENABLE_BIG_WAVE_PRE_SMA',0,int): disabled_routes.add('BIG_WAVE_PRE_SMA')
    candidates=[item for item in candidates if item[2] not in disabled_routes]
    if not candidates: return None,detail
    score,side,route=max(candidates,key=lambda x:x[0])
    return {'side':side,'route':route,'score':round(score,1),'price':p},detail


# V656-A: V655-A original signal selection + entry-only historical quality gate.
# No order execution; EXIT, LINE, FTP, reporting and note logic are unchanged.
from datetime import timedelta

def quality_check(prices, now, *, min_60m=0.90, min_5m_minutes=3,
                  max_gap_minutes=10):
    """Return (allowed, reason, diagnostics). Missing minute = missing observation.

    Window boundaries: [now-60min, now) and [now-5min, now).
    For a current-minute decision, only earlier minute buckets are counted.
    A gap >10min since last sample rejects. Older gaps within 60m
    are reflected by coverage; no forward filling is performed.
    """
    if now.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    if not (0 < min_60m <= 1):
        raise ValueError('min_60m must be in (0, 1]')
    if not (0 <= min_5m_minutes <= 5):
        raise ValueError('min_5m_minutes must be between 0 and 5')
    if max_gap_minutes <= 0:
        raise ValueError('max_gap_minutes must be positive')
    start60 = now - timedelta(minutes=60)
    start5 = now - timedelta(minutes=5)
    minute60 = set()
    minute5 = set()
    latest = None
    for ts, price in prices:
        if ts.tzinfo is None:
            raise ValueError('price timestamps must be timezone-aware')
        if not start60 <= ts < now:
            continue
        try:
            p = float(price)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(p) or p <= 0:
            continue
        bucket = ts.replace(second=0, microsecond=0)
        minute60.add(bucket)
        if ts >= start5:
            minute5.add(bucket)
        if latest is None or ts > latest:
            latest = ts
    n60, n5 = len(minute60), len(minute5)
    coverage = n60 / 60
    gap = (now - latest).total_seconds() / 60 if latest is not None else float('inf')
    diagnostics = {'minutes_60m': n60, 'coverage_60m_pct': round(coverage*100, 2),
                   'minutes_5m': n5, 'latest_sample_age_min': round(gap, 2)}
    if gap > max_gap_minutes:
        return False, 'STALE_PRICE_OVER_10M', diagnostics
    if coverage < min_60m:
        return False, 'LOW_60M_COVERAGE', diagnostics
    if n5 < min_5m_minutes:
        return False, 'LOW_5M_COVERAGE', diagnostics
    return True, 'OK', diagnostics

def v654_candidate(prices, bot, diagnostics=None):
    def record(message):
        if diagnostics is not None: diagnostics.append(message)
    a=bot.bars(prices,5); b=bot.bars(prices,60); c=bot.bars(prices,15)
    if len(a)<55 or len(b)<55 or len(c)<12:
        record(f'共通: 足不足 5m={len(a)} 1h={len(b)} 15m={len(c)}')
        return None
    p=a[-1]; s=bot.sma(a,20); w=bot.wma(a,20)
    h=bot.hma(b,34); hp=bot.hma(b[:-1],34)
    h1s=bot.sma(b,20); h1prev=bot.sma(b[:-1],20)
    if any(v is None or v<=0 for v in (s,w,h,hp,h1s,h1prev)):
        record('共通: 指標不足')
        return None
    vol=statistics.pstdev([a[i]/a[i-1]-1 for i in range(-24,0)])
    if vol<0.00038:
        record(f'共通: 低ボラ({vol:.6f}<0.000380)')
        return None
    if bot.cfg('PAPER_STOP_LOSS_JPY',500)+bot.cfg('PAPER_COST_JPY_PER_TRADE',0)>bot.cfg('PAPER_MAX_ENTRY_RISK_JPY',650):
        record('共通: 想定損失過大')
        return None
    risk=bot.recent_tick_risk(prices,prices[-1][0])
    if risk is None:
        record('共通: 直近価格サンプル不足')
        return None
    if risk['max_jump_jpy']>v657_tick_jump_limit(prices,risk):
        record(f'共通: 短時間価格飛び({risk["max_jump_jpy"]:.1f}円)')
        return None
    # V656-A fix: the ordinary 3m-range veto was already disabled in signal().
    # Keep the tick-jump and chase filters, and the independent extreme-shock
    # safety limits in SHOCK_BB_RSI_REVERSAL, unchanged.
    mom1=a[-1]/a[-2]-1; mom3=a[-1]/a[-4]-1
    slope=(h-hp)/hp; rs=bot.rsi(a)
    gap=abs(p-s)/p
    out=[]
    for side,sgn in (('LONG',1),('SHORT',-1)):
        fail=[]
        if sgn*risk['last_move_jpy']>bot.cfg('PAPER_ENTRY_MAX_3M_CHASE_JPY',220):
            fail.append('追随制限')
        if side=='LONG' and rs>bot.cfg('PAPER_LONG_MAX_RSI',70):
            fail.append('RSI買われ過ぎ')
        if side=='SHORT' and rs<bot.cfg('PAPER_SHORT_MIN_RSI',30):
            fail.append('RSI売られ過ぎ')
        # BB reentry: genuine prior excursion, reversal confirmed, avoid strongly opposing 1h trend.
        excursion=False
        for i in range(len(a)-8,len(a)-1):
            win=a[i-19:i+1]
            if len(win)<20:continue
            mid=statistics.mean(win); sd=statistics.pstdev(win)
            if sgn==1 and a[i]<mid-2*sd:excursion=True
            if sgn==-1 and a[i]>mid+2*sd:excursion=True
        sd=statistics.pstdev(a[-20:]); lower=s-2*sd; upper=s+2*sd
        reentry=(p>lower if sgn==1 else p<upper)
        # Strict reversal requires 5m impulse in reversal direction and 1h not strongly opposed.
        if not excursion: fail.append('BB逸脱なし')
        if not reentry: fail.append('BB内復帰なし')
        if not sgn*mom1>0.00006: fail.append('mom1反転不足')
        if not sgn*(p-a[-2])>0: fail.append('反転足なし')
        if not sgn*slope>-0.00018: fail.append('1時間HMA逆行')
        if not gap<0.0022: fail.append('MA乖離超過')
        if not vol>=0.00040: fail.append('BB用ボラ不足')
        if not sgn*(a[-2]-a[-3])<0: fail.append('直前足逆行なし')
        record(f'{side}/BB_REENTRY_V654: '+('成立' if not fail else '・'.join(fail)))
        if not fail:
            out.append((91,side,'BB_REENTRY_V654'))
        # Trend restart: 1h SMA20 + HMA slope agree; recent dip and fresh 5m recovery.
        hourly=(sgn*(b[-1]-h1s)>0 and sgn*(h1s-h1prev)>0 and sgn*slope>0)
        recovered=(sgn*(p-s)>0 and sgn*(p-w)>0)
        prior_dip=(sgn*(a[-2]-a[-3])<0 or sgn*(a[-3]-a[-4])<0)
        fresh=(sgn*mom1>0.00013 and sgn*mom3>0.00020)
        if (hourly and recovered and prior_dip and fresh and 0.00040<=vol
            and gap<0.0012 and sgn*(p-a[-2])>0):
            out.append((92,side,'TREND_REACCEL_V654'))
    # V655-A: disabled route must not mask an eligible BB reentry.
    out=[item for item in out if item[2] != 'TREND_REACCEL_V654']
    if not out:return None
    score,side,route=max(out,key=lambda x:x[0])
    return {'side':side,'route':route,'score':score,'price':p}

def v656a_signal(prices, decision_time):
    # Gate applies to every route. Use only observations strictly before decision_time.
    allowed, reason, diag = quality_check(prices, decision_time)
    if not allowed:
        return None, f'V657 ENTRY見送り: {reason} {diag}'
    sig, detail = signal(prices)
    # V655-A: disable original BIG_WAVE routes; retain original route priority.
    if sig and ((sig['route']=='BIG_WAVE' and not cfg('V657_ENABLE_BIG_WAVE',0,int)) or
                (sig['route']=='BIG_WAVE_PRE_SMA' and not cfg('V657_ENABLE_BIG_WAVE_PRE_SMA',0,int))):
        sig = None
    bb_diag=[]
    extra = v654_candidate(prices, __import__(__name__), bb_diag)
    # V655-A: TREND_REACCEL_V654 disabled.
    if extra and extra['route'] == 'TREND_REACCEL_V654':
        extra = None
    if not sig:
        sig = extra
    # Match J0 replay: reject a selected forbidden route, do NOT re-rank.
    if sig and (sig['route'], sig['side']) in J0_FORBIDDEN:
        bb_diag.append('J0_ROUTE_BLOCK '+sig['route']+' '+sig['side'])
        sig = None
    return sig, f'V659-J0-FIX quality={diag} | {detail} | [BB_DIAG] '+ ' | '.join(bb_diag)

def line_send(message):
    token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN','').strip()
    recipients=[x.strip() for x in os.getenv('PAPER_LINE_USER_IDS',os.getenv('LINE_USER_ID','')).split(',') if x.strip()]
    if not token or not recipients:
        print('LINE未送信: PAPER_LINE_USER_IDS/LINE_USER_ID または TOKEN が未設定'); return
    import urllib.request
    payload=json.dumps({'to':recipients[0], 'messages':[{'type':'text','text':message[:4900]}]}).encode()
    for uid in recipients:
        payload=json.dumps({'to':uid,'messages':[{'type':'text','text':message[:4900]}]}).encode()
        req=urllib.request.Request('https://api.line.me/v2/bot/message/push',payload,{'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=12) as res: print('LINE送信:',res.status)
        except Exception as e: print('LINE送信失敗:',str(e)[:200])

def write_reports(state,folder):
    folder.mkdir(parents=True,exist_ok=True)
    records=sorted(valid_trades(state.get('trades',[])),key=lambda r:r['exit_at'])
    with (folder/'paper_trade_history.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['entry_at','exit_at','side','route','score','entry_price','exit_price','lot_btc','net_pnl_jpy','reason'])
        for r in records: w.writerow([r.get(k,'') for k in ['entry_at','exit_at','side','route','score','entry_price','exit_price','lot_btc','net_pnl_jpy','reason']])
    # Export every closed trade; state.json is left intact.
    with (folder/'paper_trade_audit.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f)
        fields=['entry_at','exit_at','side','route','score','entry_price','exit_price','lot_btc','net_pnl_jpy','reason']
        w.writerow(fields+['report_status'])
        for r in records:
            w.writerow([r.get(k,'') for k in fields]+[invalid_trade_status(r)])
    for name,group in [('daily', lambda r:close_session(r).isoformat()),
                       ('weekly',lambda r:close_session(r).strftime('%G-W%V')),
                       ('monthly',lambda r:close_session(r).strftime('%Y-%m'))]:
        totals={}
        for r in records:
            key=group(r);v=totals.setdefault(key,[0,0.0]);v[0]+=1;v[1]+=float(r['net_pnl_jpy'])
        with (folder/f'paper_{name}_report.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f);w.writerow(['period','trades','net_pnl_jpy'])
            for k,v in sorted(totals.items()):w.writerow([k,v[0],yen_round(v[1])])


# WordPress-compatible virtual-trade exports. Never import live trading code.
WP_FILES = ('daily_trade_history.csv', 'daily_report.csv', 'weekly_report.csv', 'monthly_report.csv')

def wp_report_trades(state):
    """Reporting only: combine V651 historical closes with V656-A closes.

    Never change the live position, entry counts, risk gates or LINE reports.
    Missing/invalid legacy history is not silently treated as zero.
    """
    merged = list(valid_trades(state.get('trades', [])))
    if os.getenv('PAPER_LEGACY_HISTORY_ENABLE', '0') != '1':
        return merged
    legacy_path = Path(os.getenv('PAPER_LEGACY_REPORT_STATE', str(ROOT / 'paper_v623' / 'state.json')))
    if not legacy_path.is_file():
        print(f'[WP_HISTORY_WARNING] 旧履歴なし: {legacy_path}', flush=True)
        return merged
    try:
        legacy_state = json.loads(legacy_path.read_text(encoding='utf-8'))
        legacy = valid_trades(legacy_state.get('trades', []))
    except (OSError, ValueError, TypeError) as exc:
        print(f'[WP_HISTORY_WARNING] 旧履歴読み込み失敗: {exc}', flush=True)
        return merged
    def identity(r):
        return (str(r.get('entry_at', '')), str(r.get('exit_at', '')),
                str(r.get('side', '')), str(r.get('entry_price', '')),
                str(r.get('exit_price', '')))
    seen = {identity(r) for r in merged}
    added = 0
    for r in legacy:
        key = identity(r)
        if key not in seen:
            merged.append(r)
            seen.add(key)
            added += 1
    print(f'[WP_HISTORY] 旧履歴={len(legacy)}件、追加={added}件、統合={len(merged)}件', flush=True)
    return merged


def write_wp_reports(state, folder, at=None):
    folder.mkdir(parents=True, exist_ok=True)
    # WP reports use calendar days (00:00 JST), independently of the 09:00 ENTRY session.
    report_date=(at or now()).astimezone(JST).date()
    today=report_date.isoformat()
    yesterday=(report_date-dt.timedelta(days=1)).isoformat()
    trades=sorted(wp_report_trades(state),key=lambda r:r['exit_at'])
    rows=[];daily={};running=0.
    for r in trades:
        entry=dt.datetime.fromisoformat(r['entry_at']).astimezone(JST)
        close=dt.datetime.fromisoformat(r['exit_at']).astimezone(JST)
        day=close_calendar_day(r).isoformat()
        net=float(r['net_pnl_jpy'])
        cost=float(cfg('PAPER_COST_JPY_PER_TRADE',0))
        gross=net+cost
        bucket=daily.setdefault(day,{'gross':0.,'net':0.,'count':0})
        bucket['gross']+=gross;bucket['net']+=net;bucket['count']+=1
        if day!=today: continue
        running+=net
        score=float(r.get('score',0))
        band='90-100' if score>=90 else '80-89' if score>=80 else 'under-80'
        rows.append([len(rows)+1,score,day,entry.strftime('%Y-%m-%d %H:%M:%S'),
            close.strftime('%Y-%m-%d %H:%M:%S'),yen_round(gross),yen_round(cost),
            yen_round(net),yen_round(running),r['side'],round(float(r['entry_price'])),
            round(float(r['exit_price'])),f"{float(r['lot_btc']):.8f}",r.get('reason',''),
            'PAPER_'+r.get('route',''),band])
    def save(name,header,body):
        with (folder/name).open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.writer(f);writer.writerow(header);writer.writerows(body)
    # Append a visible total row after today's closed-trade details.
    if rows:
        total_gross=yen_round(daily[today]['gross'])
        total_cost=yen_round(daily[today]['gross']-daily[today]['net'])
        total_net=yen_round(daily[today]['net'])
        rows.append(['合計','',today,'','',total_gross,total_cost,total_net,total_net,
                     '','','','','','',''])
    save('daily_trade_history.csv',
        ['No','ENTRYスコア','取引日(09:00起点)','ENTRY時刻','CLOSE時刻',
         '実現損益(JPY)','固定スプレッドコスト(JPY)','純損益(JPY)',
         '当日累計純損益(JPY)','売買','ENTRY価格(JPY)','CLOSE価格(JPY)',
         '数量(BTC)','CLOSE理由','戦略','スコア帯'],rows)
    header=['日付','実現損益（JPY）','純損益（JPY）','取引回数','集計ソース']
    # Daily/weekly/monthly share exactly the same per-calendar-day trade buckets.
    # Weekly: previous 7 finalized days; monthly: 1st through yesterday.
    # Monetary totals sum the displayed, rounded daily values so shared days match.
    def calendar_dates(first, last):
        if first > last:
            return []
        return [(first + dt.timedelta(days=i)).isoformat()
                for i in range((last-first).days+1)]

    prev = report_date - dt.timedelta(days=1)
    periods = {
        'daily': [today],
        'weekly': calendar_dates(report_date-dt.timedelta(days=7), prev),
        'monthly': calendar_dates(report_date.replace(day=1), prev),
    }
    for kind, selected in periods.items():
        body=[]
        for d in selected:
            x=daily.get(d)
            if x is None:
                # A missing trade is not proof that a historical day had zero trades.
                body.append([d,'','','','no_data_or_no_trades'])
            else:
                body.append([d,yen_round(x['gross']),yen_round(x['net']),x['count'],
                             'state_trades'])
        body.append(['合計',sum(int(r[1]) for r in body if r[1]!=''),
                     sum(int(r[2]) for r in body if r[2]!=''),
                     sum(int(r[3]) for r in body if r[3]!=''),
                     'partial_if_missing_days' if any(r[1]=='' for r in body) else 'total'])
        save(kind+'_report.csv',header,body)

# Back up original remote files locally before the first replacement.
# Backup directory is persistent and must be preserved across deployments.
def ftp_upload_reports(folder):
    import ftplib, io
    host=os.getenv('PNL_FTP_HOST','').strip()
    user=os.getenv('PNL_FTP_USER','').strip()
    password=os.getenv('PNL_FTP_PASSWORD','')
    remote=os.getenv('PNL_FTP_REMOTE_DIR','').strip()
    if not all((host,user,password,remote)) or remote in ('.','/') or '..' in remote.split('/'):
        print('FTP未実行: 設定不足または転送先が不正',flush=True);return False
    backup=ROOT/'paper_v656a'/'wp_remote_backup_before_paper'
    tls=os.getenv('PNL_FTP_TLS','0').strip().lower() in ('1','true','yes','on')
    conn=None
    try:
        conn=ftplib.FTP_TLS(timeout=20) if tls else ftplib.FTP(timeout=20)
        conn.connect(host,21);conn.login(user,password)
        if tls:conn.prot_p()
        conn.cwd(remote)
        backup.mkdir(parents=True,exist_ok=True)
        for name in WP_FILES:
            path=folder/name
            if not path.is_file():raise FileNotFoundError(str(path))
            marker=backup/(name+'.checked')
            if not marker.exists():
                original=bytearray()
                try:
                    conn.retrbinary('RETR '+name,original.extend)
                except ftplib.error_perm as e:
                    if not str(e).startswith('550'):raise
                    print('FTP元ファイルなし:',name,flush=True)
                else:
                    (backup/name).write_bytes(original)
                    print('FTP元ファイルをローカル保存:',backup/name,flush=True)
                marker.write_text('verified',encoding='utf-8')
            temp='.'+name+'.paper_uploading'
            with path.open('rb') as f:conn.storbinary('STOR '+temp,f)
            try:
                conn.rename(temp,name)
            except ftplib.error_perm:
                # Backup exists, so overwrite directly if FTP server cannot rename over target.
                with path.open('rb') as f:conn.storbinary('STOR '+name,f)
                try:conn.delete(temp)
                except ftplib.all_errors:pass
            print('WordPress仮想CSV送信成功:',name,flush=True)
        return True
    except Exception as e:
        print('WordPress仮想CSV送信失敗:',type(e).__name__,str(e)[:160],flush=True)
        return False
    finally:
        if conn:
            try:conn.quit()
            except Exception:conn.close()


# LINE trade messages use the previous bot's field names; prices are estimates.
def line_entry_message(sig, pos):
    price=float(pos['entry_price']); lot=float(pos['lot_btc'])
    side=pos['side']; score=float(sig['score'])
    label='UPWARD_PRESSURE' if side=='LONG' else 'DOWNWARD_PRESSURE'
    stop=cfg('PAPER_STOP_LOSS_JPY',500)
    trail_start=cfg('PAPER_TRAIL_START_JPY',350)
    trail_width=cfg('PAPER_TRAIL_WIDTH_JPY',150)
    sl_price=price + (-1 if side=='LONG' else 1)*stop/lot
    return '\n'.join([
        '【売買通知】',label,'','■ 売買',
        f'- 新規エントリー: {side} / 市場価格 {price:,.0f}円 → 約定想定 {price:,.0f}円 [PAPER_{sig["route"]} / SIGNAL]',
        f'- ロット: {lot:.8f} BTC',
        f'- ENTRYスコア: {score:.1f}点 ({"90-100" if score>=90 else "80-89"})',
        f'- 疑似SL: {sl_price:,.0f}円 (-{stop:.0f}円、価格飛びで超過あり)',
        f'- Trailing: +{trail_start:.0f}円開始 / 戻り{trail_width:.0f}円',
        f'- 5分足SMA/WMA理由: {sig["route"]}',
        '',f'理由: 条件成立 ({sig["route"]})'])

def line_close_message(pos, closed, trades):
    day=close_session(closed)
    daily=sum(float(r['net_pnl_jpy']) for r in valid_trades(trades) if
              close_session(r)==day)
    cost=cfg('PAPER_COST_JPY_PER_TRADE',0)
    net=float(closed['net_pnl_jpy'])
    score=float(pos.get('score',0))
    return '\n'.join([
        '【BTC/JPY CLOSE】',
        f'- CLOSE: {pos["side"]} {float(pos["entry_price"]):,.0f}円 → {float(closed["exit_price"]):,.0f}円',
        f'- ENTRYスコア: {score:.1f}点 ({"90-100" if score>=90 else "80-89"})',
        f'- 仮想損益: {yen_round(net):+,}円',
        '- 集計扱い: 有効',
        f'- ENTRY固定スプレッド: -{cost:.0f}円',
        f'- 本日累計損益: {yen_round(daily):+,}円',
        f'- 理由: {closed["reason"]}'])

def line_daily_message(day, trades):
    records=[r for r in valid_trades(trades) if close_session(r).isoformat()==day]
    count=len(records); net=sum(float(r['net_pnl_jpy']) for r in records)
    wins=sum(float(r['net_pnl_jpy'])>0 for r in records)
    losses=sum(float(r['net_pnl_jpy'])<0 for r in records)
    return '\n'.join(['【BTC/JPY 本日の損益】',f'取引日: {day}',
        f'取引回数: {count}回',f'勝ち: {wins}回 / 負け: {losses}回',
        f'通常集計損益: {yen_round(net):+,}円'])

def exit_5m_signal(prices, pos, current_time):
    """Technical EXIT from completed 5-minute bars only; hard risk exits are independent."""
    cutoff=int(current_time.timestamp())//300
    completed=[(t,p) for t,p in prices if int(t.timestamp())//300 < cutoff]
    a=bars(completed,5)
    if len(a)<24:
        return None
    s=sma(a,20); w=wma(a,20)
    ps=sma(a[:-1],20); pw=wma(a[:-1],20)
    if any(v is None for v in (s,w,ps,pw)):
        return None
    side=1 if pos['side']=='LONG' else -1
    # Both 5m momentum reversal and 5m moving-average deterioration required.
    mom1=(a[-1]-a[-2])*side
    mom2=(a[-1]-a[-3])*side
    ma_weak=(a[-1]-s)*side < 0 and (a[-1]-w)*side < 0
    ma_falling=(s-ps)*side < 0 and (w-pw)*side < 0
    if mom1 < 0 and mom2 < 0 and ma_weak and ma_falling:
        return '5M_TREND_REVERSAL'
    return None

def step(db,statefile,folder,dry_run=False):
    t=now(); prices=read_prices(db)
    if not prices: print('価格データなし');return
    latest,p=prices[-1]; age=(t-latest).total_seconds()
    if age< -120 or age>cfg('PAPER_MAX_PRICE_AGE_SEC',180,int):
        print(f'停止: 価格データが古い/未来です latest={latest.isoformat()} age={age:.0f}秒 DB={db} now={t.isoformat()}。価格収集を確認',flush=True);return
    state=json.loads(statefile.read_text()) if statefile.exists() else {'trades':[],'position':None,'entries':{},'last_bar':None,'last_report':None}
    original_trade_count=len(state.get('trades',[]))
    original_report=state.get('last_report')
    pos=state.get('position'); key=session_day(t).isoformat();lot=0.05  # V632: fixed paper lot
    report_due=(t.hour==0 and state.get('last_report')!=key)
    if pos:
        side=1 if pos['side']=='LONG' else -1
        pnl=(p-pos['entry_price'])*pos['lot_btc']*side - cfg('PAPER_COST_JPY_PER_TRADE',0)
        pos['peak_pnl']=max(pos.get('peak_pnl',pnl),pnl)
        held=(t-dt.datetime.fromisoformat(pos['entry_at'])).total_seconds()/60
        reason=None
        if t.hour==0:reason='24:00強制CLOSE'
        elif pnl<=-cfg('PAPER_STOP_LOSS_JPY',500):reason='STOP'
        elif (pos['peak_pnl']>=cfg('PAPER_BREAKEVEN_TRIGGER_JPY',300)
              and pnl<=cfg('PAPER_BREAKEVEN_FLOOR_JPY',0)):
            reason='BREAKEVEN'
        elif pos['peak_pnl']>=cfg('PAPER_TRAIL_START_JPY',350) and pnl<=pos['peak_pnl']-cfg('PAPER_TRAIL_WIDTH_JPY',150):reason='TRAIL'
        elif held>=cfg('PAPER_MAX_HOLD_MIN',90):reason='MAX_HOLD'
        elif held>=max(5,cfg('PAPER_5M_EXIT_MIN_HOLD_MIN',10,int)):
            # Technical EXIT uses completed 5m bars, not the hourly ENTRY trend.
            # Avoid a technical close on a loss unless a hard STOP fires.
            if pnl>=cfg('PAPER_5M_EXIT_MIN_PNL_JPY',0):
                reason=exit_5m_signal(prices,pos,t)
        if reason:
            closed={**pos,'exit_at':t.isoformat(),'exit_price':p,'net_pnl_jpy':round(pnl,2),'reason':reason}
            closed['report_status']=invalid_trade_status(closed)
            state['trades'].append(closed);state['position']=None
            print('仮想CLOSE',closed)
            if not dry_run:
                line_send(line_close_message(pos,closed,state['trades']))
    elif 9<=t.hour<24:
        cap=cfg('PAPER_DAILY_ENTRY_CAP',10,int)
        count=sum(session_day(dt.datetime.fromisoformat(r['entry_at']).astimezone(JST)).isoformat()==key for r in state.get('trades',[]))
        if cap>0 and count>=cap:
            print(f'[ENTRY_CAP制限] {key} {count}/{cap}',flush=True)
            dd_ok,dd_reason=False,'日次ENTRY上限'
        else:
            dd_ok,dd_reason=entry_dd_gate(state['trades'],t)
            # J0 backtest additionally gates realized PnL by ENTRY session.
            # Preserve the existing entry_dd_gate as a separate safety gate.
            j0_realized = sum(float(r['net_pnl_jpy']) for r in state.get('trades', [])
                if session_day(dt.datetime.fromisoformat(r['entry_at']).astimezone(JST)) == session_day(t))
            if j0_realized <= -J0_DAILY_LOSS_LIMIT_JPY:
                dd_ok = False
                dd_reason = f'J0日次損失制限 {j0_realized:+.2f} <= -{J0_DAILY_LOSS_LIMIT_JPY:.0f}円'
        if not dd_ok:
            print('[ENTRY_DD制限]',t.isoformat(),dd_reason,flush=True)
        else:
            # One evaluation per five-minute bucket, regardless of collector minute.
            bar=latest.replace(minute=(latest.minute//5)*5,second=0,microsecond=0).isoformat()
            if state.get('last_bar')!=bar:
                state['last_bar']=bar
                sig,reason=v656a_signal(prices,t)
                print(f'[ENTRY_{"成立" if sig else "不成立"}] {t.isoformat()} '+
                      (f'{sig["side"]} {sig["route"]} score={sig["score"]} ' if sig else '')+reason,flush=True)
                if sig:
                    pos={'entry_at':t.isoformat(),'side':sig['side'],'route':sig['route'],'score':sig['score'],'entry_price':p,'lot_btc':lot,'peak_pnl':0}
                    state['position']=pos;state['entries'][key]=state['entries'].get(key,0)+1
                    if not dry_run:line_send(line_entry_message(sig,pos))
    if report_due:
        report_day=(t-dt.timedelta(days=1)).date().isoformat()
        day=session_closed_trades(valid_trades(state['trades']),report_day)
        total=sum(r['net_pnl_jpy'] for r in day)
        actual_day=session_closed_trades(state['trades'],report_day)
        print('日次報告:',report_day,len(day),yen_round(total))
        if not dry_run:line_send(line_daily_message(report_day,state["trades"]))
        state['last_report']=key
    if not dry_run:
        statefile.parent.mkdir(parents=True,exist_ok=True)
        tmp=statefile.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2));tmp.replace(statefile)
        write_reports(state,folder)

        # WordPress CSVは取引履歴変更時、日付変更時、
        # 日次報告更新時、CSV欠損時のみ再生成する。
        wp_day = t.astimezone(JST).date().isoformat()
        wp_files_missing = any(
            not (folder / name).is_file() for name in WP_FILES
        )
        wp_update_due = (
            state.get('last_wp_csv_day') != wp_day
            or len(state.get('trades', [])) != original_trade_count
            or state.get('last_report') != original_report
            or wp_files_missing
        )

        if wp_update_due:
            write_wp_reports(state,folder,at=t)
            state['last_wp_csv_day'] = wp_day
            tmp=statefile.with_suffix('.tmp')
            tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2))
            tmp.replace(statefile)
        # FTP reports are generated with today's trades excluded from weekly/monthly.
        # Upload once on each JST calendar date (including after restart), as well
        # as after CLOSE or midnight reporting. Record the date only on success.
        if os.getenv('PNL_FTP_ENABLE','0').strip().lower() in ('1','true','yes','on'):
            ftp_day=t.astimezone(JST).date().isoformat()
            upload_due=(state.get('last_wp_ftp_day')!=ftp_day or
                        len(state.get('trades',[]))!=original_trade_count or
                        state.get('last_report')!=original_report)
            if upload_due and ftp_upload_reports(folder):
                state['last_wp_ftp_day']=ftp_day
                tmp=statefile.with_suffix('.tmp')
                tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2))
                tmp.replace(statefile)
    else:print('DRY RUN: LINE送信・状態保存なし')


# ---- note membership code management (ported from original; no order APIs) ----
def note_settings():
    return {
        'fixed': os.getenv('NOTE_REDEEM_CODE','').strip(),
        'days': max(1,cfg('NOTE_REDEEM_DAYS',30,int)),
        'limit': cfg('NOTE_REDEEM_LIMIT_PER_MONTH',1,int),
        'auto': os.getenv('NOTE_AUTO_GENERATE_CODE','1').lower() in ('1','true','yes','on'),
        'prefix': os.getenv('NOTE_CODE_PREFIX','AI').strip().upper() or 'AI',
        'bytes': max(4,min(16,cfg('NOTE_CODE_BYTES',5,int))),
    }

def note_schema(con):
    con.execute("""CREATE TABLE IF NOT EXISTS note_codes (
        ym TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, generated_at TEXT NOT NULL,
        broadcast_at TEXT, broadcast_count INTEGER DEFAULT 0, updated_at TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS note_redeem_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL,
        ym TEXT NOT NULL, code TEXT NOT NULL, redeemed_at TEXT NOT NULL,
        status TEXT NOT NULL, current_period_end TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_note_redeem_log_user_ym ON note_redeem_log(user_id,ym)")
    con.execute("""CREATE TABLE IF NOT EXISTS subscriptions (
        user_id TEXT PRIMARY KEY, status TEXT NOT NULL, customer_id TEXT,
        subscription_id TEXT, current_period_end TEXT, updated_at TEXT NOT NULL)""")
    cols={r[1] for r in con.execute('PRAGMA table_info(subscriptions)')}
    if 'last_redeem_ym' not in cols:
        con.execute('ALTER TABLE subscriptions ADD COLUMN last_redeem_ym TEXT')
    if 'last_redeem_at' not in cols:
        con.execute('ALTER TABLE subscriptions ADD COLUMN last_redeem_at TEXT')

def note_code(db, ym=None, create=True):
    import secrets
    ym=ym or now().strftime('%Y-%m')
    if not __import__('re').fullmatch(r'\d{4}-(0[1-9]|1[0-2])',ym):
        raise ValueError('ym must be YYYY-MM')
    conf=note_settings()
    with sqlite3.connect(db,timeout=15) as con:
        note_schema(con)
        row=con.execute('SELECT code FROM note_codes WHERE ym=?',(ym,)).fetchone()
        if row: return row[0]
        if not create: return None
        for _ in range(8):
            token=secrets.token_urlsafe(conf['bytes']).replace('-','').replace('_','').upper()[:10]
            code=f"{conf['prefix']}{ym.replace('-','')}-{token}"
            try:
                con.execute("""INSERT INTO note_codes
                    (ym,code,generated_at,broadcast_at,broadcast_count,updated_at)
                    VALUES (?,?,?,NULL,0,?)""",(ym,code,now().isoformat(),now().isoformat()))
                return code
            except sqlite3.IntegrityError:
                row=con.execute('SELECT code FROM note_codes WHERE ym=?',(ym,)).fetchone()
                if row: return row[0]
        raise RuntimeError('note code generation collision')

def note_redeem(db,user_id,code):
    user_id=user_id.strip();code=code.strip()
    if not user_id or not code: return False,'ユーザーIDまたは合言葉が空です',None
    t=now();ym=t.strftime('%Y-%m');conf=note_settings()
    allowed=set()
    if conf['fixed']: allowed.add(conf['fixed'])
    if conf['auto']: allowed.add(note_code(db,ym))
    with sqlite3.connect(db,timeout=15) as con:
        note_schema(con)
        con.execute('BEGIN IMMEDIATE')
        def log(status,end=None):
            con.execute("""INSERT INTO note_redeem_log
                (user_id,ym,code,redeemed_at,status,current_period_end)
                VALUES (?,?,?,?,?,?)""",(user_id,ym,code,t.isoformat(),status,end))
        if not allowed or code not in allowed:
            log('wrong_code')
            return False,('合言葉が違います' if allowed else '合言葉が未設定です'),None
        row=con.execute("""SELECT status,current_period_end,last_redeem_ym
            FROM subscriptions WHERE user_id=?""",(user_id,)).fetchone()
        if conf['limit']==1 and row and row[2]==ym:
            log('already_redeemed',row[1])
            return True,'今月はすでに反映済みです',row[1]
        base=t
        if row and row[1]:
            try:
                prev=dt.datetime.fromisoformat(row[1])
                if prev.tzinfo is None: prev=prev.replace(tzinfo=JST)
                if prev>base:base=prev
            except ValueError:pass
        end=(base+dt.timedelta(days=conf['days'])).isoformat()
        con.execute("""INSERT INTO subscriptions
            (user_id,status,customer_id,subscription_id,current_period_end,updated_at,last_redeem_ym,last_redeem_at)
            VALUES (?,'active',NULL,NULL,?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
              status=excluded.status,current_period_end=excluded.current_period_end,
              updated_at=excluded.updated_at,last_redeem_ym=excluded.last_redeem_ym,
              last_redeem_at=excluded.last_redeem_at""",
            (user_id,end,t.isoformat(),ym,t.isoformat()))
        log('redeemed',end)
        return True,'課金を反映しました。有効期限: '+end[:16],end

def note_recipients(db, admins=False):
    ids=set(x.strip() for x in os.getenv('NOTE_ADMIN_USER_IDS','').split(',') if x.strip()) if admins else set()
    with sqlite3.connect(db,timeout=15) as con:
        cols={r[1] for r in con.execute('PRAGMA table_info(users)')}
        if 'user_id' not in cols:return sorted(ids)
        filters=[]
        if 'disabled' in cols:filters.append('COALESCE(disabled,0)=0')
        if 'canceled_at' in cols:filters.append("(canceled_at IS NULL OR canceled_at='')")
        if admins:
            if 'is_admin' not in cols:return sorted(ids)
            filters.append('COALESCE(is_admin,0)=1')
        sql='SELECT user_id FROM users'+(' WHERE '+' AND '.join(filters) if filters else '')
        ids.update(str(r[0]) for r in con.execute(sql) if r[0])
    return sorted(ids)

def note_send_to(recipients,message):
    import urllib.request
    token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN','').strip()
    if not token:raise RuntimeError('LINE_CHANNEL_ACCESS_TOKEN missing')
    sent=0
    for uid in recipients:
        payload=json.dumps({'to':uid,'messages':[{'type':'text','text':message[:4900]}]}).encode()
        req=urllib.request.Request('https://api.line.me/v2/bot/message/push',payload,
            {'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=15) as response:
                if response.status==200:sent+=1
        except Exception as e:
            print('note LINE送信失敗:',type(e).__name__,flush=True)
    return sent

def note_broadcast(db,ym=None,admin_only=False,force=False):
    ym=ym or now().strftime('%Y-%m')
    code=note_code(db,ym)
    with sqlite3.connect(db,timeout=15) as con:
        note_schema(con)
        row=con.execute('SELECT broadcast_at FROM note_codes WHERE ym=?',(ym,)).fetchone()
        if not admin_only and row and row[0] and not force:
            print('note: 今月は送信済みです');return True
    users=note_recipients(db,admins=admin_only)
    if not users:
        print('note: 送信対象がありません');return False
    if admin_only:
        msg=f'【管理者用】今月のnote合言葉\n対象月: {ym}\n合言葉: {code}'
    else:
        msg=(f'【noteメンバー合言葉】\n{code}\n\n'
            'この合言葉をこのLINEに送信すると、メンバー期間が延長されます。\n'
            f'有効期限：送信日から {note_settings()["days"]} 日\n'
            '※合言葉は月ごとに変更されます。\n'
            '※月1回まで（運用設定）')
    sent=note_send_to(users,msg)
    print(f'note LINE送信: {sent}/{len(users)}')
    if not admin_only and sent==len(users):
        with sqlite3.connect(db,timeout=15) as con:
            con.execute("""UPDATE note_codes SET broadcast_at=?,
                broadcast_count=COALESCE(broadcast_count,0)+?,updated_at=?
                WHERE ym=?""",(now().isoformat(),sent,now().isoformat(),ym))
    return sent==len(users)

def main():
    ap=argparse.ArgumentParser(description='Signal-only paper bot: NEVER submits orders')
    ap.add_argument('--env',default=str(ROOT/'bot.env'));ap.add_argument('--db',default=str(ROOT/'line_users.db'))
    ap.add_argument('--state',default=str(ROOT/'paper_v656a/state.json'))
    ap.add_argument('--output',default=str(ROOT/'paper_v656a'))
    ap.add_argument('--once',action='store_true');ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--ftp-test',action='store_true',help='Upload existing paper CSV files only; no signal or LINE')
    ap.add_argument('--note-code',action='store_true',help='Show/create this month note code (admin only)')
    ap.add_argument('--note-redeem',nargs=2,metavar=('USER_ID','CODE'),help='Validate note code and extend subscription')
    ap.add_argument('--note-monthly-auto',action='store_true',help='Broadcast this month note code once')
    ap.add_argument('--note-admin-notify',action='store_true',help='Send note code to admins')
    ap.add_argument('--note-force',action='store_true',help='Force repeat broadcast')
    ap.add_argument('--note-ym',default=None,help='Target YYYY-MM for code/broadcast')
    args=ap.parse_args();load_env(Path(args.env));db=Path(args.db);state=Path(args.state);out=Path(args.output)
    if args.note_code:
        print('NOTE_REDEEM_CODE='+note_code(db,args.note_ym));return
    if args.note_redeem:
        ok,msg,end=note_redeem(db,*args.note_redeem)
        print(msg)
        if not ok:raise SystemExit(1)
        return
    if args.note_monthly_auto or args.note_admin_notify:
        ok=note_broadcast(db,args.note_ym,admin_only=args.note_admin_notify,force=args.note_force)
        if not ok:raise SystemExit(1)
        return
    if args.ftp_test:
        if not out.is_dir() or not all((out/name).is_file() for name in WP_FILES):
            print('FTPテスト中止: WordPress用CSVがありません');return
        ftp_upload_reports(out);return
    if args.once or args.dry_run:step(db,state,out,args.dry_run);return
    print('Signal-only observer started. No trading API used.',flush=True)
    while True:
        try:step(db,state,out)
        except Exception as e:print('ERROR:',repr(e),flush=True)
        # V644: default 5s sampling for earlier paper STOP detection; actual
        # recorded tick gaps still determine achievable paper CLOSE price.
        time.sleep(max(2,cfg('PAPER_POLL_SEC',5,int)))
if __name__=='__main__':main()
