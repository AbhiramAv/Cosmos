#!/usr/bin/env python3
import json, os, sqlite3, time, datetime, subprocess, shutil
from pathlib import Path

ROOT = Path('/opt/data/Cosmos')
OUT = ROOT / 'dashboard' / 'data' / 'live.json'
STATE_DB = Path('/opt/data/state.db')
KANBAN_DB = Path('/opt/data/kanban.db')
CRON_JOBS = Path('/opt/data/cron/jobs.json')
LOGS = Path('/opt/data/logs')
CTX_LIMIT_ESTIMATE = 400_000


def iso(ts):
    if not ts:
        return None
    if isinstance(ts, str):
        return ts
    return datetime.datetime.fromtimestamp(float(ts), datetime.timezone.utc).isoformat()


def human_delta(seconds):
    seconds = max(0, int(seconds or 0))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if d: return f'{d}d {h}h'
    if h: return f'{h}h {m}m'
    if m: return f'{m}m {s}s'
    return f'{s}s'


def run(cmd, cwd=None):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True, timeout=8)
        return {'ok': p.returncode == 0, 'out': p.stdout.strip(), 'err': p.stderr.strip(), 'code': p.returncode}
    except Exception as e:
        return {'ok': False, 'out': '', 'err': str(e), 'code': -1}


def capacity(used, limit, unit, label, source):
    used = int(used or 0) if used is not None else None
    limit = int(limit or 0) if limit else None
    remaining = None if used is None or limit is None else max(0, limit - used)
    pct = None if used is None or not limit else round(min(100, used / limit * 100), 1)
    return {'label': label, 'used': used, 'limit': limit, 'remaining': remaining, 'pct': pct, 'unit': unit, 'source': source}


def read_sessions():
    if not STATE_DB.exists():
        return [], []
    con = sqlite3.connect(str(STATE_DB)); con.row_factory = sqlite3.Row
    sessions = [dict(r) for r in con.execute('select * from sessions order by started_at desc')]
    messages = [dict(r) for r in con.execute('select role, tool_name, timestamp, token_count, session_id from messages order by timestamp desc limit 1000')]
    con.close()
    return sessions, messages


def sums(rows):
    keys = ['input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','reasoning_tokens','message_count','tool_call_count','api_call_count']
    return {k: int(sum((r.get(k) or 0) for r in rows)) for k in keys}


def session_tokens(s):
    return int((s.get('input_tokens') or 0) + (s.get('output_tokens') or 0) + (s.get('reasoning_tokens') or 0))


def session_view(s, now):
    tokens = session_tokens(s)
    return {
        'id': s.get('id'), 'title': s.get('title'), 'source': s.get('source'),
        'model': s.get('model'), 'provider': s.get('billing_provider'),
        'parent_session_id': s.get('parent_session_id'),
        'started_at': iso(s.get('started_at')), 'ended_at': iso(s.get('ended_at')) if s.get('ended_at') else None,
        'duration_seconds': int((s.get('ended_at') or now) - (s.get('started_at') or now)),
        'input_tokens': int(s.get('input_tokens') or 0), 'output_tokens': int(s.get('output_tokens') or 0),
        'reasoning_tokens': int(s.get('reasoning_tokens') or 0), 'cache_read_tokens': int(s.get('cache_read_tokens') or 0),
        'message_count': int(s.get('message_count') or 0), 'tool_call_count': int(s.get('tool_call_count') or 0),
        'api_call_count': int(s.get('api_call_count') or 0), 'context_tokens_used': tokens,
        'context_limit_estimate': CTX_LIMIT_ESTIMATE, 'context_remaining_estimate': max(0, CTX_LIMIT_ESTIMATE - tokens),
        'context_pct_estimate': round(min(100, tokens/CTX_LIMIT_ESTIMATE*100), 1),
        'cost_status': s.get('cost_status'), 'estimated_cost_usd': s.get('estimated_cost_usd'),
    }


def read_cron():
    cron=[]
    if not CRON_JOBS.exists():
        return cron
    try:
        data=json.loads(CRON_JOBS.read_text())
        for j in data.get('jobs',[]):
            repeat=j.get('repeat') or {}
            origin=j.get('origin') or {}
            cron.append({
                'id':j.get('id'), 'name':j.get('name') or j.get('id'), 'enabled':bool(j.get('enabled')),
                'state':j.get('state'), 'schedule':j.get('schedule_display') or (j.get('schedule') or {}).get('display'),
                'script':j.get('script'), 'no_agent':j.get('no_agent'), 'deliver':j.get('deliver'),
                'last_run_at':j.get('last_run_at'), 'next_run_at':j.get('next_run_at'), 'last_status':j.get('last_status'),
                'last_error':j.get('last_error'), 'completed':repeat.get('completed'), 'target': origin.get('chat_name') or j.get('deliver'),
                'purpose': (j.get('prompt') or '').strip()[:220]
            })
    except Exception as e:
        cron.append({'name':'cron read failed','state':str(e), 'enabled': False})
    return cron


def read_kanban(now):
    columns = {k: [] for k in ['todo','running','blocked','completed','archived']}
    stats = {k: 0 for k in columns}
    if not KANBAN_DB.exists():
        return {'columns': columns, 'stats': stats, 'source': 'kanban.db not found'}
    try:
        con=sqlite3.connect(str(KANBAN_DB)); con.row_factory=sqlite3.Row
        rows=[dict(r) for r in con.execute('select id,title,body,assignee,status,priority,created_at,started_at,completed_at,workspace_kind,workspace_path,current_step_key,skills,session_id,last_heartbeat_at,result,last_failure_error from tasks order by priority desc, created_at desc')]
        for r in rows:
            status=(r.get('status') or 'todo').lower()
            col = 'completed' if status in ['done','complete','completed'] else 'running' if status in ['running','claimed','in_progress'] else 'blocked' if status == 'blocked' else 'archived' if status == 'archived' else 'todo'
            stats[col]+=1
            if len(columns[col]) < 10:
                columns[col].append({
                    'id': r.get('id'), 'title': r.get('title'), 'assignee': r.get('assignee') or 'unassigned',
                    'status': r.get('status'), 'priority': r.get('priority'), 'created_at': iso(r.get('created_at')),
                    'started_at': iso(r.get('started_at')), 'completed_at': iso(r.get('completed_at')),
                    'last_heartbeat_at': iso(r.get('last_heartbeat_at')), 'heartbeat_age': human_delta(now-r.get('last_heartbeat_at')) if r.get('last_heartbeat_at') else None,
                    'step': r.get('current_step_key'), 'skills': r.get('skills'), 'session_id': r.get('session_id'),
                    'summary': (r.get('result') or r.get('last_failure_error') or r.get('body') or '')[:180]
                })
        con.close()
        return {'columns': columns, 'stats': stats, 'source': 'real /opt/data/kanban.db'}
    except Exception as e:
        return {'columns': columns, 'stats': stats, 'source': f'kanban read failed: {e}'}


def build_agent_roster(sessions, kanban, now):
    active = [s for s in sessions if not s.get('ended_at')]
    root = [s for s in active if not s.get('parent_session_id')]
    children = [s for s in active if s.get('parent_session_id')]
    running_cards = kanban.get('columns',{}).get('running',[])
    roles = [
        ('CEO Orchestrator','Routes Ram requests, owns final answer, starts/monitors specialists', root[0] if root else None, 'assigned' if root else 'idle'),
        ('Coding Agent','Code/build/test work via tools or coding CLIs', None, 'unassigned'),
        ('Research Agent','Web/research synthesis and source validation', None, 'unassigned'),
        ('Ops/Cron Agent','Scheduled jobs, watchdogs, sync, monitoring', None, 'assigned' if running_cards else 'idle'),
        ('Knowledge Agent','Memory, Obsidian/Cosmos source-of-truth updates', None, 'unassigned'),
    ]
    roster=[]
    for name, responsibility, sess, status in roles:
        roster.append({
            'name': name, 'responsibility': responsibility, 'status': status,
            'assigned_work': sess.get('title') if sess else ('Kanban running cards' if name=='Ops/Cron Agent' and running_cards else 'No active work assigned'),
            'session_id': sess.get('id') if sess else None,
            'model': sess.get('model') if sess else None,
        })
    for s in children[:8]:
        roster.append({'name':'Sub-agent session', 'responsibility':'Delegated specialist work', 'status':'active', 'assigned_work':s.get('title') or s.get('id'), 'session_id':s.get('id'), 'model':s.get('model'), 'parent_session_id':s.get('parent_session_id')})
    return roster


def build():
    now=time.time()
    sessions, messages = read_sessions()
    current = next((s for s in sessions if not s.get('ended_at')), sessions[0] if sessions else None)
    current_view = session_view(current, now) if current else {}
    since_24=now-86400; since_7=now-7*86400
    rows_24=[s for s in sessions if (s.get('started_at') or 0) >= since_24]
    rows_7=[s for s in sessions if (s.get('started_at') or 0) >= since_7]
    totals=sums(sessions); totals24=sums(rows_24); totals7=sums(rows_7)

    daily=[]
    for i in range(6,-1,-1):
        d=(datetime.datetime.fromtimestamp(now, datetime.timezone.utc)-datetime.timedelta(days=i)).date()
        start=datetime.datetime(d.year,d.month,d.day,tzinfo=datetime.timezone.utc).timestamp(); end=start+86400
        rs=[s for s in sessions if start <= (s.get('started_at') or 0) < end]
        sm=sums(rs)
        daily.append({'date': d.isoformat(), 'label': d.strftime('%b %d'), 'tokens': sm['input_tokens']+sm['output_tokens']+sm['reasoning_tokens'], 'cache': sm['cache_read_tokens'], 'tools': sm['tool_call_count'], 'sessions': len(rs)})

    hourly=[]
    for i in range(23,-1,-1):
        end=now-i*3600; start=end-3600
        bucket=[m for m in messages if start <= (m.get('timestamp') or 0) < end]
        hourly.append({'hour': datetime.datetime.fromtimestamp(start, datetime.timezone.utc).strftime('%H:%M'), 'messages': len(bucket), 'tools': sum(1 for m in bucket if m.get('role')=='tool'), 'tokens': sum((m.get('token_count') or 0) for m in bucket)})

    provider_usage=[]; grouped={}
    for s in sessions:
        key=(s.get('billing_provider') or 'unknown', s.get('model') or 'unknown')
        grouped.setdefault(key, []).append(s)
    for (provider, model), rs in grouped.items():
        sm=sums(rs)
        provider_usage.append({'provider':provider,'model':model,'sessions':len(rs),'tokens':sm['input_tokens']+sm['output_tokens']+sm['reasoning_tokens'],'cache':sm['cache_read_tokens'],'api_calls':sm['api_call_count'],'estimated_cost_usd':round(sum((r.get('estimated_cost_usd') or 0) for r in rs),4),'cost_status': next((r.get('cost_status') for r in rs if r.get('cost_status')), None)})
    provider_usage.sort(key=lambda x:x['tokens'], reverse=True)
    openai_rows=[s for s in sessions if 'openai' in (s.get('billing_provider') or '').lower() or 'codex' in (s.get('billing_provider') or '').lower()]
    openai_7=[s for s in rows_7 if s in openai_rows]

    cron=read_cron()
    kanban=read_kanban(now)
    disk=shutil.disk_usage('/opt/data')
    status=run('git status --short --branch', cwd=str(ROOT)); log=run('git log -1 --oneline', cwd=str(ROOT))
    procs={'dashboard_server': int(run("pgrep -f 'python3 -m http.server 8787' | wc -l")['out'] or 0), 'localtunnel': int(run("pgrep -f 'localtunnel --port 8787' | wc -l")['out'] or 0)}

    capacities=[
        capacity(current_view.get('context_tokens_used'), current_view.get('context_limit_estimate'), 'context tokens', 'Current session context', 'real current-session tokens; context limit is a conservative estimate'),
        capacity(totals7['input_tokens']+totals7['output_tokens']+totals7['reasoning_tokens'], None, 'tokens', 'All providers: last 7 days', 'observed local Hermes sessions; no fixed provider limit attached'),
        capacity(sum(session_tokens(s) for s in openai_7), None, 'tokens', 'OpenAI/Codex observed weekly usage', 'real local sessions tagged OpenAI/Codex; provider weekly limit/reset not exposed locally'),
        capacity(disk.used, disk.total, 'bytes', '/opt/data storage', 'real OS disk usage'),
    ]

    payload={
        'generated_at': iso(now), 'generated_at_epoch': now,
        'current_session': current_view,
        'active_sessions': [session_view(s, now) for s in sessions if not s.get('ended_at')][:12],
        'recent_sessions': [session_view(s, now) for s in sessions[:12]],
        'totals': {'all':totals, 'last_24h':totals24, 'last_7d':totals7, 'session_count':len(sessions)},
        'series': {'daily':daily, 'hourly_activity':hourly},
        'provider_usage': provider_usage,
        'openai': {'observed_sessions': len(openai_rows), 'weekly_observed_sessions': len(openai_7), 'weekly_observed_tokens': sum(session_tokens(s) for s in openai_7), 'weekly_limit': None, 'reset_at': None, 'reset_in': 'OpenAI weekly/message reset is not exposed by local Hermes telemetry yet', 'source': 'populated from local session DB billing_provider/model fields'},
        'quota_panels': [
            {'provider':'OpenAI/Codex','used':sum(session_tokens(s) for s in openai_7),'limit':None,'remaining':None,'pct':None,'unit':'tokens observed this week','reset_in':'not connected','source':'real local usage; provider quota API/browser integration needed for actual weekly cap'},
            {'provider':'Current session context','used':current_view.get('context_tokens_used'), 'limit': current_view.get('context_limit_estimate'), 'remaining': current_view.get('context_remaining_estimate'), 'pct': current_view.get('context_pct_estimate'), 'unit':'context tokens', 'reset_in':'new session resets context', 'source':'real session token usage + estimated context window'},
            {'provider':'OpenRouter','used':None,'limit':None,'remaining':None,'pct':None,'unit':'credits/messages','reset_in':'waiting for key/details from Ram','source':'not connected'},
            {'provider':'Claude/Anthropic','used':None,'limit':None,'remaining':None,'pct':None,'unit':'messages/tokens','reset_in':'waiting for key/details from Ram','source':'not connected'},
        ],
        'capacities': capacities,
        'cron': cron,
        'kanban': kanban,
        'agent_roster': build_agent_roster(sessions, kanban, now),
        'git': {'status':status['out'], 'last_commit':log['out'], 'clean': status['ok'] and ('\n' not in status['out'].strip() and status['out'].startswith('##'))},
        'processes': procs,
        'disk': {'total':disk.total,'used':disk.used,'free':disk.free,'pct':round(disk.used/disk.total*100,1)},
        'data_quality': [
            'Static workflow placeholders removed; dashboard now renders cron, agent, provider, kanban, storage, and session data from live local sources.',
            'OpenAI/Codex usage is populated from Hermes sessions now. Actual OpenAI weekly cap/reset is not available locally yet, so it is labeled unknown instead of guessed.',
            'Kanban board is wired to /opt/data/kanban.db; it will show cards as soon as tasks exist.'
        ]
    }
    serialized=json.dumps(payload, indent=2)
    for target in [OUT, ROOT / 'dashboard' / 'dist' / 'data' / 'live.json']:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp=target.with_suffix('.tmp'); tmp.write_text(serialized); tmp.replace(target)
    return payload

if __name__ == '__main__':
    build()
