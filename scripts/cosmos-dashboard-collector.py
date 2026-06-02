#!/usr/bin/env python3
import json, os, re, sqlite3, time, datetime, subprocess, shutil
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



def line_count(path):
    try:
        with open(path, 'rb') as f:
            return sum(1 for _ in f)
    except Exception:
        return None


def tail_text(path, max_bytes=120_000):
    try:
        p=Path(path)
        if not p.exists(): return ''
        with p.open('rb') as f:
            if p.stat().st_size > max_bytes:
                f.seek(-max_bytes, os.SEEK_END)
            return f.read().decode('utf-8','ignore')
    except Exception:
        return ''


def read_log_summary(now):
    logs=[]
    for p in sorted(LOGS.rglob('*.log')):
        try:
            st=p.stat(); txt=tail_text(p)
            logs.append({
                'name': str(p.relative_to(LOGS)), 'path': str(p), 'size': st.st_size,
                'updated_at': iso(st.st_mtime), 'age_seconds': int(now-st.st_mtime),
                'errors': sum(txt.lower().count(x) for x in ['error','traceback','exception','failed']),
                'warnings': txt.lower().count('warning'),
                'lines': line_count(p),
                'tail': txt[-360:]
            })
        except Exception:
            pass
    logs.sort(key=lambda x:(x['errors'], -x['age_seconds']), reverse=True)
    return {'logs': logs[:20], 'error_total': sum(x['errors'] for x in logs), 'warning_total': sum(x['warnings'] for x in logs), 'stale': [x for x in logs if x['age_seconds'] > 3600][:10]}


def env_key_names():
    keys=[]
    for env_file in [Path('/opt/data/.env'), Path('/opt/data/Cosmos/.env')]:
        if env_file.exists():
            try:
                for line in env_file.read_text(errors='ignore').splitlines():
                    line=line.strip()
                    if not line or line.startswith('#') or '=' not in line: continue
                    keys.append(line.split('=',1)[0].strip())
            except Exception:
                pass
    keys.extend(os.environ.keys())
    return sorted(set(k for k in keys if k))



def read_session_timing(sessions, current_view, now):
    ended = [s for s in sessions if s.get('ended_at')]
    last_ended = max(ended, key=lambda s: s.get('ended_at') or 0) if ended else None
    started = current_view.get('started_at')
    started_epoch = None
    try:
        if started:
            started_epoch = datetime.datetime.fromisoformat(started.replace('Z','+00:00')).timestamp()
    except Exception:
        started_epoch = None
    age_seconds = int(now - started_epoch) if started_epoch else current_view.get('duration_seconds')
    context_pct = current_view.get('context_pct_estimate')
    # Hermes compression/new-session resets are local context lifecycle, not provider quota resets.
    if context_pct is None:
        reset_status = 'unknown'
    elif context_pct >= 85:
        reset_status = 'near context limit; start /new soon or expect compression pressure'
    elif context_pct >= 50:
        reset_status = 'compression zone; context may compact before a hard reset'
    else:
        reset_status = 'healthy; context reset only when a new session starts'
    return {
        'current_started_at': current_view.get('started_at'),
        'current_started_epoch': started_epoch,
        'current_age_seconds': age_seconds,
        'current_ends_at': current_view.get('ended_at'),
        'current_end_reason': None,
        'last_ended_at': iso(last_ended.get('ended_at')) if last_ended else None,
        'last_ended_epoch': last_ended.get('ended_at') if last_ended else None,
        'last_end_reason': last_ended.get('end_reason') if last_ended else None,
        'last_session_title': last_ended.get('title') if last_ended else None,
        'local_context_reset_status': reset_status,
        'local_context_reset_source': 'Hermes session start/end from /opt/data/state.db; reset is local context lifecycle, separate from Codex provider quota.'
    }


def read_codex_reset(now):
    # Codex does not expose a normal quota endpoint locally. The most reliable
    # signal we have is the backend's 429 payload, which includes resets_at.
    events=[]
    pattern=re.compile(r"usage_limit_reached.*?'resets_at':\s*(\d+).*?'resets_in_seconds':\s*(\d+)")
    alt=re.compile(r'"type"\s*:\s*"usage_limit_reached".*?"resets_at"\s*:\s*(\d+).*?"resets_in_seconds"\s*:\s*(\d+)')
    for p in sorted(LOGS.glob('*.log')):
        txt=tail_text(p, max_bytes=400_000)
        for m in list(pattern.finditer(txt)) + list(alt.finditer(txt)):
            line_start=txt.rfind('\n', 0, m.start())+1
            line_end=txt.find('\n', m.end())
            if line_end < 0: line_end=len(txt)
            line=txt[line_start:line_end]
            ts_match=re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            observed=None
            if ts_match:
                try:
                    observed=datetime.datetime.strptime(ts_match.group(1), '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
                except Exception:
                    observed=None
            resets_at=float(m.group(1)); resets_in=int(m.group(2))
            events.append({'observed_at': iso(observed) if observed else None, 'observed_epoch': observed, 'resets_at': iso(resets_at), 'resets_at_epoch': resets_at, 'resets_in_seconds_reported': resets_in, 'source': str(p)})
    events.sort(key=lambda e: e.get('observed_epoch') or 0, reverse=True)
    latest=events[0] if events else None
    active = bool(latest and latest['resets_at_epoch'] > now)
    if latest:
        seconds_until=int(latest['resets_at_epoch']-now)
        status='rate limited now' if active else 'last observed reset has passed; next provider reset unknown until Codex returns another limit payload'
    else:
        seconds_until=None
        status='no Codex limit/reset payload found in local logs yet'
    return {
        'provider': 'openai-codex',
        'status': status,
        'is_rate_limited_now': active,
        'latest_resets_at': latest.get('resets_at') if latest else None,
        'latest_resets_at_epoch': latest.get('resets_at_epoch') if latest else None,
        'seconds_until_reset': max(0, seconds_until) if seconds_until is not None else None,
        'last_limit_observed_at': latest.get('observed_at') if latest else None,
        'last_limit_observed_epoch': latest.get('observed_epoch') if latest else None,
        'recent_limit_events': events[:6],
        'source': 'Parsed from Codex HTTP 429 usage_limit_reached errors in /opt/data/logs/errors.log. Codex quota cap/reset is not otherwise exposed locally.'
    }

def read_connections():
    keys=env_key_names()
    def has_any(parts): return any(any(part.upper() in k.upper() for part in parts) for k in keys)
    rows=[
        ('Telegram control surface', True, 'Already connected: current DM control channel'),
        ('GitHub source-of-truth', (ROOT/'.git').exists(), 'Local Cosmos git repo + deploy-key push path'),
        ('Obsidian vault', bool(os.environ.get('OBSIDIAN_VAULT_PATH')) or any(Path(p).exists() for p in ['/opt/data/Obsidian','/opt/data/Obsidian Vault','/opt/data/vault','/opt/data/Documents/Obsidian Vault']), 'Needs vault path if not detected'),
        ('Supabase backend/vector store', has_any(['SUPABASE']), 'Needs URL + service role/key if desired'),
        ('Google Workspace', has_any(['GOOGLE','GWS']), 'Needs OAuth/client setup if desired'),
        ('Notion', has_any(['NOTION']), 'Needs Notion token/database IDs if desired'),
        ('Linear', has_any(['LINEAR']), 'Needs Linear API key/team IDs if desired'),
        ('OpenRouter quota', has_any(['OPENROUTER']), 'Could add credits/quota endpoint if key exists'),
        ('Anthropic/Claude quota', has_any(['ANTHROPIC','CLAUDE']), 'Quota/reset integration not connected'),
        ('OpenAI/Codex quota', has_any(['OPENAI','CODEX']), 'Local usage visible; provider cap/reset not exposed yet'),
    ]
    return [{'name':n,'connected':bool(c),'status':'connected' if c else 'missing','note':note} for n,c,note in rows]


def read_obsidian(now):
    candidates=[]
    if os.environ.get('OBSIDIAN_VAULT_PATH'): candidates.append(Path(os.environ['OBSIDIAN_VAULT_PATH']))
    candidates += [Path('/opt/data/Obsidian'), Path('/opt/data/Obsidian Vault'), Path('/opt/data/vault'), Path('/opt/data/Documents/Obsidian Vault')]
    vault=next((p for p in candidates if p.exists() and p.is_dir()), None)
    if not vault:
        return {'connected': False, 'path': None, 'note_count': 0, 'recent_notes': [], 'status': 'missing vault path', 'question': 'What is the absolute Obsidian vault path on this machine or should I create /opt/data/Obsidian Vault?'}
    notes=sorted(vault.rglob('*.md'), key=lambda x:x.stat().st_mtime, reverse=True)
    recent=[]
    for n in notes[:12]:
        st=n.stat()
        recent.append({'name': n.stem, 'path': str(n), 'relative_path': str(n.relative_to(vault)), 'updated_at': iso(st.st_mtime), 'age_seconds': int(now-st.st_mtime), 'size': st.st_size})
    return {'connected': True, 'path': str(vault), 'note_count': len(notes), 'recent_notes': recent, 'status': 'connected'}


def read_repo_activity(now):
    changed=run('git status --porcelain', cwd=str(ROOT))['out'].splitlines()
    branches=run('git branch --show-current', cwd=str(ROOT))['out']
    remote=run('git remote get-url origin', cwd=str(ROOT))['out']
    commits=[]
    out=run('git log --pretty=format:%h%x09%ct%x09%s -8', cwd=str(ROOT))['out']
    for line in out.splitlines():
        parts=line.split('\t',2)
        if len(parts)==3:
            commits.append({'sha':parts[0], 'timestamp':iso(float(parts[1])), 'age_seconds':int(now-float(parts[1])), 'subject':parts[2]})
    return {'branch': branches, 'remote': remote, 'changed_files': changed[:25], 'dirty_count': len(changed), 'recent_commits': commits}


def read_tool_usage(messages):
    counts={}
    for m in messages:
        name=m.get('tool_name')
        if name: counts[name]=counts.get(name,0)+1
    return [{'tool':k,'count':v} for k,v in sorted(counts.items(), key=lambda x:x[1], reverse=True)[:18]]

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
    public_url_path = ROOT / 'dashboard' / 'public-url.txt'
    public_url = public_url_path.read_text().strip() if public_url_path.exists() else None
    procs={
        'dashboard_server': int(run("pgrep -f '[p]ython3 -m http.server 8787' | wc -l")['out'] or 0),
        'cloudflared': int(run("pgrep -f '[c]loudflared.*8787' | wc -l")['out'] or 0),
        'localtunnel': int(run("pgrep -f '[l]ocaltunnel --port 8787' | wc -l")['out'] or 0),
        'public_url': public_url,
    }
    logs=read_log_summary(now)
    connections=read_connections()
    obsidian=read_obsidian(now)
    repo_activity=read_repo_activity(now)
    tool_usage=read_tool_usage(messages)
    session_timing=read_session_timing(sessions, current_view, now)
    codex_reset=read_codex_reset(now)

    capacities=[
        capacity(current_view.get('context_tokens_used'), current_view.get('context_limit_estimate'), 'context tokens', 'Current session context', 'real current-session tokens; context limit is a conservative estimate'),
        capacity(totals7['input_tokens']+totals7['output_tokens']+totals7['reasoning_tokens'], None, 'tokens', 'All providers: last 7 days', 'observed local Hermes sessions; no fixed provider limit attached'),
        capacity(sum(session_tokens(s) for s in openai_7), None, 'tokens', 'OpenAI/Codex observed weekly usage', 'real local sessions tagged OpenAI/Codex; provider weekly limit/reset not exposed locally'),
        capacity(disk.used, disk.total, 'bytes', '/opt/data storage', 'real OS disk usage'),
    ]

    payload={
        'generated_at': iso(now), 'generated_at_epoch': now,
        'current_session': current_view,
        'session_timing': session_timing,
        'codex_reset': codex_reset,
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
        'logs': logs,
        'connections': connections,
        'obsidian': obsidian,
        'repo_activity': repo_activity,
        'tool_usage': tool_usage,
        'disk': {'total':disk.total,'used':disk.used,'free':disk.free,'pct':round(disk.used/disk.total*100,1)},
        'data_quality': [
            'Static workflow placeholders removed; dashboard now renders cron, agent, provider, kanban, storage, and session data from live local sources.',
            'OpenAI/Codex usage is populated from Hermes sessions now. Actual OpenAI weekly cap/reset is not available locally yet, so it is labeled unknown instead of guessed.',
            'Kanban board is wired to /opt/data/kanban.db; it will show cards as soon as tasks exist.',
            'New easy-track sources: Obsidian readiness, log/error counts, repo activity, connection readiness, and tool usage.',
            'Session start/end times come from the Hermes SQLite session store; Codex reset time is parsed from real 429 usage_limit_reached payloads when available.'
        ]
    }
    serialized=json.dumps(payload, indent=2)
    for target in [OUT, ROOT / 'dashboard' / 'dist' / 'data' / 'live.json']:
        target.parent.mkdir(parents=True, exist_ok=True)
        # Use a per-process temp path so concurrent collector/watchdog runs do not
        # steal each other's shared live.tmp before os.replace().
        tmp=target.with_name(f'{target.stem}.{os.getpid()}.{time.time_ns()}.tmp')
        tmp.write_text(serialized)
        tmp.replace(target)
    return payload

if __name__ == '__main__':
    build()
