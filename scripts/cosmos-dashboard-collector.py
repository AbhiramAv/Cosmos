#!/usr/bin/env python3
import json, os, sqlite3, time, datetime, subprocess, shutil
from pathlib import Path

ROOT = Path('/opt/data/Cosmos')
OUT = ROOT / 'dashboard' / 'data' / 'live.json'
STATE_DB = Path('/opt/data/state.db')
CRON_JOBS = Path('/opt/data/cron/jobs.json')
CONFIG = Path('/opt/data/config.yaml')
LOGS = Path('/opt/data/logs')


def iso(ts):
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(float(ts), datetime.timezone.utc).isoformat()


def run(cmd, cwd=None):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True, timeout=8)
        return {'ok': p.returncode == 0, 'out': p.stdout.strip(), 'err': p.stderr.strip(), 'code': p.returncode}
    except Exception as e:
        return {'ok': False, 'out': '', 'err': str(e), 'code': -1}


def next_utc_midnight(now):
    dt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
    nxt = (dt + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return nxt.timestamp()


def next_month_start(now):
    dt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
    if dt.month == 12:
        nxt = datetime.datetime(dt.year + 1, 1, 1, tzinfo=datetime.timezone.utc)
    else:
        nxt = datetime.datetime(dt.year, dt.month + 1, 1, tzinfo=datetime.timezone.utc)
    return nxt.timestamp()


def human_delta(seconds):
    seconds=max(0,int(seconds))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if d: return f'{d}d {h}h'
    if h: return f'{h}h {m}m'
    if m: return f'{m}m {s}s'
    return f'{s}s'


def read_sessions():
    if not STATE_DB.exists():
        return [], []
    con = sqlite3.connect(str(STATE_DB))
    con.row_factory = sqlite3.Row
    sessions = [dict(r) for r in con.execute('select * from sessions order by started_at desc')]
    messages = [dict(r) for r in con.execute('select role, tool_name, timestamp, token_count from messages order by timestamp desc limit 500')]
    con.close()
    return sessions, messages


def sums(rows):
    keys=['input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','reasoning_tokens','message_count','tool_call_count','api_call_count']
    return {k:int(sum((r.get(k) or 0) for r in rows)) for k in keys}


def build():
    now=time.time()
    sessions, messages = read_sessions()
    current = next((s for s in sessions if not s.get('ended_at')), sessions[0] if sessions else None)
    since_24=now-86400
    since_7=now-7*86400
    rows_24=[s for s in sessions if (s.get('started_at') or 0) >= since_24]
    rows_7=[s for s in sessions if (s.get('started_at') or 0) >= since_7]
    totals=sums(sessions); totals24=sums(rows_24); totals7=sums(rows_7)

    current_tokens = 0
    current_ctx_limit = 400000  # heuristic until provider exposes exact limit
    if current:
        current_tokens = int((current.get('input_tokens') or 0)+(current.get('output_tokens') or 0)+(current.get('reasoning_tokens') or 0))
    context_pct = min(100, round(current_tokens/current_ctx_limit*100, 1)) if current_ctx_limit else None

    # daily series, last 7 UTC days
    daily=[]
    for i in range(6,-1,-1):
        d=(datetime.datetime.fromtimestamp(now, datetime.timezone.utc)-datetime.timedelta(days=i)).date()
        start=datetime.datetime(d.year,d.month,d.day,tzinfo=datetime.timezone.utc).timestamp()
        end=start+86400
        rs=[s for s in sessions if start <= (s.get('started_at') or 0) < end]
        sm=sums(rs)
        daily.append({'date': d.isoformat(), 'label': d.strftime('%b %d'), 'tokens': sm['input_tokens']+sm['output_tokens']+sm['reasoning_tokens'], 'cache': sm['cache_read_tokens'], 'tools': sm['tool_call_count'], 'sessions': len(rs)})

    by_model=[]
    grouped={}
    for s in sessions:
        key=(s.get('billing_provider') or 'unknown', s.get('model') or 'unknown')
        grouped.setdefault(key, []).append(s)
    for (provider, model), rs in grouped.items():
        sm=sums(rs)
        by_model.append({'provider':provider,'model':model,'sessions':len(rs),'tokens':sm['input_tokens']+sm['output_tokens']+sm['reasoning_tokens'],'cache':sm['cache_read_tokens'],'api_calls':sm['api_call_count'],'cost':sum((r.get('estimated_cost_usd') or 0) for r in rs)})
    by_model.sort(key=lambda x:x['tokens'], reverse=True)

    # current session timeline by messages (last 24h, hourly counts)
    hourly=[]
    for i in range(23,-1,-1):
        end=now-i*3600
        start=end-3600
        msg_count=sum(1 for m in messages if start <= (m.get('timestamp') or 0) < end)
        tools=sum(1 for m in messages if start <= (m.get('timestamp') or 0) < end and m.get('role')=='tool')
        hourly.append({'hour': datetime.datetime.fromtimestamp(start, datetime.timezone.utc).strftime('%H:%M'), 'messages': msg_count, 'tools': tools})

    # cron jobs
    cron=[]
    if CRON_JOBS.exists():
        try:
            data=json.loads(CRON_JOBS.read_text())
            for j in data.get('jobs',[]):
                cron.append({'id':j.get('id'), 'name':j.get('name'), 'enabled':j.get('enabled'), 'state':j.get('state'), 'schedule':j.get('schedule_display'), 'last_run_at':j.get('last_run_at'), 'next_run_at':j.get('next_run_at'), 'last_status':j.get('last_status'), 'completed':(j.get('repeat') or {}).get('completed')})
        except Exception as e:
            cron.append({'name':'cron read failed','state':str(e)})

    # git
    status=run('git status --short --branch', cwd=str(ROOT))
    log=run('git log -1 --oneline', cwd=str(ROOT))

    # logs/errors rough counts
    log_stats=[]
    for name in ['gateway.log','agent.log','errors.log']:
        p=LOGS/name
        if p.exists():
            try:
                txt=p.read_text(errors='ignore')[-200000:]
                log_stats.append({'name':name,'size':p.stat().st_size,'errors':txt.lower().count('error'),'warnings':txt.lower().count('warn')})
            except Exception as e:
                log_stats.append({'name':name,'error':str(e)})

    # auth/provider visibility without secrets
    env_keys=[]
    env=Path('/opt/data/.env')
    if env.exists():
        for line in env.read_text(errors='ignore').splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k=line.split('=',1)[0].strip()
                if k:
                    env_keys.append(k)
    provider_key_presence={
        'openrouter': any('OPENROUTER' in k for k in env_keys),
        'openai': any(k in env_keys for k in ['OPENAI_API_KEY','VOICE_TOOLS_OPENAI_KEY']),
        'anthropic': any('ANTHROPIC' in k for k in env_keys),
        'telegram': any('TELEGRAM' in k for k in env_keys),
    }

    reset_daily=next_utc_midnight(now)
    reset_month=next_month_start(now)
    quota=[
        {'provider':'OpenAI Codex / ChatGPT', 'model': current.get('model') if current else 'unknown', 'used': current_tokens, 'limit': current_ctx_limit, 'unit':'context tokens', 'pct': context_pct, 'reset_at': None, 'reset_in':'not exposed by provider', 'source':'real Hermes session tokens + heuristic context limit'},
        {'provider':'Hermes daily local window', 'model':'all', 'used': totals24['input_tokens']+totals24['output_tokens']+totals24['reasoning_tokens'], 'limit': None, 'unit':'tokens observed in last 24h', 'pct': None, 'reset_at': iso(reset_daily), 'reset_in': human_delta(reset_daily-now), 'source':'computed from local session DB'},
        {'provider':'OpenRouter budget', 'model':'all OpenRouter models', 'used': 0, 'limit': 20, 'unit':'USD budget configured by Ram', 'pct': 0, 'reset_at': iso(reset_month), 'reset_in': human_delta(reset_month-now), 'source':'budget known; live OpenRouter key/API not connected'},
        {'provider':'Claude / Anthropic', 'model':'all Claude models', 'used': None, 'limit': None, 'unit':'provider quota', 'pct': None, 'reset_at': None, 'reset_in':'not connected', 'source':'no Anthropic key/quota API found locally'},
    ]

    disk=shutil.disk_usage('/opt/data')
    procs={
        'dashboard_server': run("pgrep -f 'python3 -m http.server 8787' | wc -l")['out'],
        'localtunnel': run("pgrep -f 'localtunnel --port 8787' | wc -l")['out'],
    }

    payload={
        'generated_at': iso(now),
        'generated_at_epoch': now,
        'current_session': {
            'id': current.get('id') if current else None,
            'title': current.get('title') if current else None,
            'source': current.get('source') if current else None,
            'model': current.get('model') if current else None,
            'provider': current.get('billing_provider') if current else None,
            'started_at': iso(current.get('started_at')) if current else None,
            'ended_at': iso(current.get('ended_at')) if current and current.get('ended_at') else None,
            'duration_seconds': int((current.get('ended_at') or now) - (current.get('started_at') or now)) if current else 0,
            'input_tokens': int(current.get('input_tokens') or 0) if current else 0,
            'output_tokens': int(current.get('output_tokens') or 0) if current else 0,
            'reasoning_tokens': int(current.get('reasoning_tokens') or 0) if current else 0,
            'cache_read_tokens': int(current.get('cache_read_tokens') or 0) if current else 0,
            'message_count': int(current.get('message_count') or 0) if current else 0,
            'tool_call_count': int(current.get('tool_call_count') or 0) if current else 0,
            'api_call_count': int(current.get('api_call_count') or 0) if current else 0,
            'context_tokens_used': current_tokens,
            'context_limit_estimate': current_ctx_limit,
            'context_pct_estimate': context_pct,
            'cost_status': current.get('cost_status') if current else None,
            'estimated_cost_usd': current.get('estimated_cost_usd') if current else None,
        },
        'totals': {'all':totals, 'last_24h':totals24, 'last_7d':totals7, 'session_count':len(sessions)},
        'series': {'daily':daily, 'hourly_activity':hourly},
        'by_model':by_model,
        'quota': quota,
        'cron': cron,
        'git': {'status':status['out'], 'last_commit':log['out'], 'clean': status['ok'] and ('\n' not in status['out'].strip() and status['out'].startswith('##'))},
        'logs': log_stats,
        'providers': provider_key_presence,
        'processes': procs,
        'disk': {'total':disk.total,'used':disk.used,'free':disk.free,'pct':round(disk.used/disk.total*100,1)},
        'data_quality': [
            'Token, session, cron, git, process, and log numbers come from local Hermes/Cosmos files.',
            'Provider reset/quota timers require provider quota APIs or browser/OAuth integrations; unavailable sources are labeled instead of guessed.',
            'Context limit is a heuristic until Hermes/provider exposes exact gpt-5.5 limit.'
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp=OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(OUT)
    return payload

if __name__ == '__main__':
    p=build()
    print(f"live metrics written {OUT} at {p['generated_at']}")
