import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Activity, AlertTriangle, BarChart3, Bot, Brain, CalendarClock, CheckCircle2, ChevronRight, CircleDollarSign, Clock3, Cloud, Code2, Cpu, Database, GitBranch, Gauge, HardDrive, KeyRound, KanbanSquare, Link2, Network, Orbit, RefreshCcw, Server, ShieldCheck, Sparkles, TerminalSquare, TimerReset, Workflow, Zap } from 'lucide-react'
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, PolarAngleAxis, RadialBar, RadialBarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import './styles.css'

const COLORS = ['#00e5ff', '#7c3cff', '#ff4fd8', '#ffb020', '#3cff9b', '#ff6b6b']

function compact(n) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return 'unknown'
  const num = Number(n)
  if (Math.abs(num) >= 1e9) return `${(num / 1e9).toFixed(1)}B`
  if (Math.abs(num) >= 1e6) return `${(num / 1e6).toFixed(1)}M`
  if (Math.abs(num) >= 1e3) return `${(num / 1e3).toFixed(1)}K`
  return String(Math.round(num))
}
function bytes(n) {
  if (n === null || n === undefined) return 'unknown'
  const units = ['B','KB','MB','GB','TB']; let v=Number(n), i=0
  while (v >= 1024 && i < units.length-1) { v/=1024; i++ }
  return `${v.toFixed(i ? 1 : 0)} ${units[i]}`
}
function pct(n) { return n === null || n === undefined ? 'unknown' : `${Number(n).toFixed(1)}%` }
function money(n) { return n ? `$${Number(n).toFixed(3)}` : '$0.000' }
function duration(sec) { sec=Number(sec||0); if(sec<60)return`${sec}s`; const h=Math.floor(sec/3600),m=Math.floor((sec%3600)/60); return h?`${h}h ${m}m`:`${m}m` }
function since(epoch) { if(!epoch)return'unknown'; const s=Math.max(0,Math.floor(Date.now()/1000-epoch)); if(s<60)return`${s}s ago`; if(s<3600)return`${Math.floor(s/60)}m ago`; return`${Math.floor(s/3600)}h ago` }
function fmtDate(s) { if(!s)return'unknown'; try { return new Date(s).toLocaleString([], { month:'short', day:'numeric', hour:'numeric', minute:'2-digit' }) } catch { return s } }
function valueWithUnit(v, unit) { return unit === 'bytes' ? bytes(v) : `${compact(v)} ${unit || ''}`.trim() }

function useLiveData() {
  const [data, setData] = useState(null), [error, setError] = useState(null)
  useEffect(() => {
    let alive = true
    async function load() {
      try { const res = await fetch(`/data/live.json?t=${Date.now()}`); if(!res.ok) throw new Error(`${res.status} ${res.statusText}`); const json=await res.json(); if(alive){setData(json); setError(null)} }
      catch(e){ if(alive) setError(e.message) }
    }
    load(); const id=setInterval(load, 20000); return()=>{alive=false; clearInterval(id)}
  }, [])
  return { data, error }
}

function App(){ const {data,error}=useLiveData(); if(!data) return <div className="boot"><Orbit className="spin"/><span>Loading real Cosmos telemetry…</span>{error&&<small>{error}</small>}</div>; return <Dashboard data={data} error={error}/> }

function Dashboard({data,error}) {
  const cs=data.current_session||{}, daily=data.series?.daily||[], hourly=data.series?.hourly_activity||[]
  const context=data.capacities?.find(c=>c.label==='Current session context') || {}
  const storage=data.capacities?.find(c=>c.label==='/opt/data storage') || {}
  const openai=data.openai||{}
  const total7=(data.totals?.last_7d?.input_tokens||0)+(data.totals?.last_7d?.output_tokens||0)+(data.totals?.last_7d?.reasoning_tokens||0)
  return <main className="shell">
    <TopNav data={data}/>
    <section className="hero-grid compact-hero">
      <div className="hero-card glass">
        <div className="eyebrow"><Sparkles size={14}/> REAL DATA ONLY</div>
        <h1>CEO Agent Command Center</h1>
        <p>No more placeholder workflow cards. This view now shows the CEO session, assigned sub-agents, cron jobs, OpenAI/Codex usage from sessions, capacity math, and Kanban work pulled from local Cosmos/Hermes state.</p>
        <div className="hero-actions"><a className="btn primary" href="/data/live.json" target="_blank">Inspect live JSON <ChevronRight size={16}/></a><button className="btn ghost" onClick={()=>location.reload()}><RefreshCcw size={16}/> Refresh</button></div>
      </div>
      <LiveSession cs={cs}/>
    </section>

    <section className="kpi-grid">
      <Kpi icon={Brain} label="CEO context used" value={pct(context.pct)} sub={`${valueWithUnit(context.used, context.unit)} used · ${valueWithUnit(context.remaining, context.unit)} left of ${valueWithUnit(context.limit, context.unit)}`} tone="cyan"/>
      <Kpi icon={CircleDollarSign} label="OpenAI/Codex this week" value={compact(openai.weekly_observed_tokens)} sub={`${openai.weekly_observed_sessions||0} sessions · weekly cap/reset not connected`} tone="violet"/>
      <Kpi icon={Clock3} label="Cron jobs" value={compact(data.cron?.length||0)} sub={`${(data.cron||[]).filter(c=>c.enabled).length} enabled · ${(data.cron||[]).filter(c=>c.last_status==='ok').length} last ok`} tone="green"/>
      <Kpi icon={HardDrive} label="Storage" value={pct(storage.pct)} sub={`${bytes(storage.used)} used · ${bytes(storage.remaining)} free of ${bytes(storage.limit)}`} tone="pink"/>
    </section>

    <section className="dashboard-grid">
      <Panel className="span-4" title="Current Session: used vs left" icon={Gauge}><CapacityCard cap={context}/><div className="split-stats"><span>Input <b>{compact(cs.input_tokens)}</b></span><span>Output <b>{compact(cs.output_tokens)}</b></span><span>Reasoning <b>{compact(cs.reasoning_tokens)}</b></span></div></Panel>
      <Panel className="span-8" title="OpenAI/Codex + provider usage from sessions" icon={CircleDollarSign}><ProviderUsage rows={data.provider_usage||[]} openai={openai}/></Panel>

      <Panel className="span-8" title="Usage history: actual local sessions" icon={BarChart3}><UsageChart daily={daily}/></Panel>
      <Panel className="span-4" title="24h message/tool pulse" icon={Activity}><PulseChart hourly={hourly}/></Panel>

      <Panel className="span-12" title="CEO + sub-agents: assigned vs unassigned" icon={Bot}><AgentRoster agents={data.agent_roster||[]}/></Panel>
      <Panel className="span-12" title="Kanban board: current assigned work" icon={KanbanSquare}><KanbanBoard kanban={data.kanban}/></Panel>
      <Panel className="span-12" title="Cron registry: every job, purpose, next run" icon={Clock3}><CronTable cron={data.cron||[]}/></Panel>

      <Panel className="span-6" title="Capacity math across system" icon={Cpu}><CapacityList capacities={data.capacities||[]}/></Panel>
      <Panel className="span-6" title="System health / source-of-truth" icon={Server}><HealthGrid data={data}/></Panel>
      <Panel className="span-12" title="Data quality notes" icon={ShieldCheck}><div className="note-list">{(data.data_quality||[]).map((n,i)=><div className="note" key={i}>{n}</div>)}</div></Panel>
    </section>
    <footer className="footer-note"><span>Generated {since(data.generated_at_epoch)} · source: local Hermes/Cosmos telemetry</span>{error&&<span className="warn"><AlertTriangle size={14}/> {error}</span>}</footer>
  </main>
}

function TopNav({data}){return <header className="topnav"><div className="brand"><div className="logo"><Orbit size={20}/></div><div><b>Cosmos</b><span>CEO OS</span></div></div><nav><a href="#agents">Agents</a><a href="#kanban">Kanban</a><a href="#cron">Cron</a><a href="/data/live.json">JSON</a></nav><div className="live-pill"><span/> Live · {since(data.generated_at_epoch)}</div></header>}
function LiveSession({cs}){return <div className="live-card glass"><div className="card-head"><span>CEO/current session</span><Activity size={18}/></div><h2>{cs.title||cs.model||'No active session'}</h2><p>{cs.model||'model unknown'} · {cs.provider||'provider unknown'} · {duration(cs.duration_seconds)}</p><div className="live-stack"><MetricLine label="Context used" value={`${compact(cs.context_tokens_used)} / ${compact(cs.context_limit_estimate)}`}/><MetricLine label="Context left" value={compact(cs.context_remaining_estimate)}/><MetricLine label="Messages / tools" value={`${compact(cs.message_count)} / ${compact(cs.tool_call_count)}`}/><MetricLine label="API calls" value={compact(cs.api_call_count)}/></div></div>}
function Kpi({icon:Icon,label,value,sub,tone}){return <article className={`kpi ${tone}`}><Icon size={21}/><span>{label}</span><b>{value}</b><small>{sub}</small></article>}
function Panel({title,icon:Icon,children,className=''}){return <section className={`panel ${className}`}><div className="panel-title"><div><Icon size={18}/><h3>{title}</h3></div></div>{children}</section>}
function MetricLine({label,value}){return <div className="metric-line"><span>{label}</span><b>{value}</b></div>}
function Empty({text}){return <div className="empty">{text}</div>}
function ChartTip({active,payload,label}){if(!active||!payload?.length)return null; return <div className="tip"><b>{label}</b>{payload.map((p,i)=><span key={i}>{p.name}: {compact(p.value)}</span>)}</div>}
function CapacityCard({cap}){return <div className="capacity-card"><div className="gauge-wrap"><ResponsiveContainer width="100%" height={210}><RadialBarChart cx="50%" cy="58%" innerRadius="62%" outerRadius="95%" barSize={15} data={[{name:'used',value:cap.pct||0,fill:'#00e5ff'}]} startAngle={210} endAngle={-30}><PolarAngleAxis type="number" domain={[0,100]} tick={false}/><RadialBar dataKey="value" cornerRadius={30} background={{fill:'rgba(255,255,255,.07)'}}/></RadialBarChart></ResponsiveContainer><div className="gauge-center"><b>{pct(cap.pct)}</b><span>{valueWithUnit(cap.used, cap.unit)} used</span></div></div><MetricLine label="Total" value={valueWithUnit(cap.limit, cap.unit)}/><MetricLine label="Remaining" value={valueWithUnit(cap.remaining, cap.unit)}/><p className="source">{cap.source}</p></div>}
function ProviderUsage({rows,openai}){return <div className="provider-wrap"><div className="openai-box"><b>OpenAI/Codex populated now</b><span>{compact(openai.weekly_observed_tokens)} tokens observed this week across {openai.weekly_observed_sessions||0} sessions.</span><small>{openai.reset_in}</small></div><div className="provider-table">{rows.map((p,i)=><div className="provider-row" key={i}><div><b>{p.model}</b><span>{p.provider} · {p.cost_status||'cost status unknown'}</span></div><span>{compact(p.tokens)} tokens</span><span>{compact(p.cache)} cache</span><span>{money(p.estimated_cost_usd)}</span></div>)}{!rows.length&&<Empty text="No provider sessions recorded yet."/>}</div></div>}
function UsageChart({daily}){return <ResponsiveContainer width="100%" height={310}><AreaChart data={daily} margin={{left:-20,right:10,top:20,bottom:0}}><defs><linearGradient id="tokenFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#00e5ff" stopOpacity=".55"/><stop offset="100%" stopColor="#00e5ff" stopOpacity="0"/></linearGradient><linearGradient id="cacheFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#7c3cff" stopOpacity=".38"/><stop offset="100%" stopColor="#7c3cff" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/><XAxis dataKey="label" tickLine={false} axisLine={false} stroke="rgba(255,255,255,.42)" fontSize={12}/><YAxis tickFormatter={compact} tickLine={false} axisLine={false} stroke="rgba(255,255,255,.42)" fontSize={12}/><Tooltip content={<ChartTip/>}/><Area type="monotone" dataKey="cache" stroke="#7c3cff" fill="url(#cacheFill)" strokeWidth={2} name="Cache read"/><Area type="monotone" dataKey="tokens" stroke="#00e5ff" fill="url(#tokenFill)" strokeWidth={3} name="Tokens"/></AreaChart></ResponsiveContainer>}
function PulseChart({hourly}){return <ResponsiveContainer width="100%" height={270}><BarChart data={hourly} margin={{left:-20,right:8,top:10,bottom:0}}><CartesianGrid stroke="rgba(255,255,255,.07)" vertical={false}/><XAxis dataKey="hour" interval="preserveStartEnd" minTickGap={18} tickLine={false} axisLine={false} stroke="rgba(255,255,255,.38)" fontSize={11}/><YAxis tickFormatter={compact} tickLine={false} axisLine={false} stroke="rgba(255,255,255,.38)" fontSize={11}/><Tooltip content={<ChartTip/>}/><Bar dataKey="messages" radius={[8,8,0,0]} name="Messages">{hourly.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}</Bar><Bar dataKey="tools" radius={[8,8,0,0]} name="Tools" fill="#3cff9b"/></BarChart></ResponsiveContainer>}
function AgentRoster({agents}){return <div id="agents" className="agent-roster">{agents.map((a,i)=><article className={`agent-row ${a.status}`} key={i}><div className="agent-icon">{i===0?<Brain size={22}/>:<Bot size={22}/>}</div><div><h4>{a.name}</h4><p>{a.responsibility}</p><small>Assigned work: {a.assigned_work}</small>{a.session_id&&<small>Session: {a.session_id}</small>}</div><b>{a.status}</b></article>)}</div>}
function KanbanBoard({kanban={}}){const cols=kanban.columns||{}; const labels=[['todo','To do'],['running','Doing'],['blocked','Blocked'],['completed','Done']]; return <div id="kanban"><p className="source">{kanban.source}</p><div className="kanban-grid">{labels.map(([key,label])=><div className="kanban-col" key={key}><div className="kanban-head"><b>{label}</b><span>{kanban.stats?.[key]||0}</span></div>{(cols[key]||[]).map(card=><div className="kanban-card" key={card.id}><b>{card.title}</b><span>{card.assignee} · priority {card.priority}</span><small>{card.summary||'No summary yet'}</small></div>)}{!(cols[key]||[]).length&&<div className="kanban-empty">No cards</div>}</div>)}</div></div>}
function CronTable({cron}){return <div id="cron" className="cron-table">{cron.map(c=><article className="cron-row" key={c.id}><div><b>{c.name}</b><span>{c.purpose||'script-only job'}</span></div><div><label>Schedule</label><strong>{c.schedule}</strong></div><div><label>Last</label><strong>{c.last_status||'unknown'} · {fmtDate(c.last_run_at)}</strong></div><div><label>Next</label><strong>{fmtDate(c.next_run_at)}</strong></div><div><label>Script</label><strong>{c.script||'agent prompt'}</strong></div><i className={c.enabled?'ok':'off'}>{c.enabled?'enabled':'disabled'}</i></article>)}{!cron.length&&<Empty text="No cron jobs registered."/>}</div>}
function CapacityList({capacities}){return <div className="capacity-list">{capacities.map((c,i)=><div className="capacity-row" key={i}><div><b>{c.label}</b><span>{c.source}</span></div><div className="quota-meter"><i style={{width:`${c.pct??0}%`}}/></div><small>{valueWithUnit(c.used,c.unit)} used · {valueWithUnit(c.remaining,c.unit)} remaining · {valueWithUnit(c.limit,c.unit)} total</small></div>)}</div>}
function HealthGrid({data}){const items=[['Dashboard server',data.processes?.dashboard_server?'running':'not detected',Cloud],['Public tunnel',data.processes?.localtunnel?'running':'not detected',Link2],['Git',data.git?.last_commit||data.git?.status||'unknown',GitBranch],['Disk',`${bytes(data.disk?.used)} / ${bytes(data.disk?.total)} (${pct(data.disk?.pct)})`,HardDrive],['Kanban source',data.kanban?.source||'unknown',KanbanSquare],['Live JSON','/data/live.json',Database]]; return <div className="health-grid">{items.map(([k,v,Icon])=><div className="health" key={k}><Icon size={18}/><span>{k}</span><b>{v}</b></div>)}</div>}

createRoot(document.getElementById('root')).render(<App />)
