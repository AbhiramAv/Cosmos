import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  Brain,
  CalendarClock,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Cloud,
  Code2,
  Cpu,
  Database,
  GitBranch,
  Gauge,
  HardDrive,
  KeyRound,
  LayoutDashboard,
  Link2,
  Lock,
  Network,
  Orbit,
  RefreshCcw,
  Server,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  TimerReset,
  Workflow,
  Zap
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts'
import './styles.css'

const LIVE_URL = `/data/live.json?t=${Date.now()}`
const COLORS = ['#00e5ff', '#7c3cff', '#ff4fd8', '#ffb020', '#3cff9b', '#ff6b6b']

const departments = [
  { name: 'CEO Core', icon: Brain, tone: 'cyan', desc: 'Routing, memory, permissions, final review' },
  { name: 'Operations', icon: Workflow, tone: 'violet', desc: 'Tasks, cron, reminders, admin execution' },
  { name: 'Knowledge', icon: Database, tone: 'green', desc: 'Obsidian, memory, artifacts, daily logs' },
  { name: 'Research', icon: Network, tone: 'amber', desc: 'Web, references, scout lanes, validation' },
  { name: 'Engineering', icon: Code2, tone: 'pink', desc: 'Codex/Claude Code, tests, GitHub, deploys' },
  { name: 'Observability', icon: Gauge, tone: 'blue', desc: 'Usage, cost, quotas, failures, telemetry' }
]

function compact(n) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return '—'
  const num = Number(n)
  if (Math.abs(num) >= 1e9) return `${(num / 1e9).toFixed(1)}B`
  if (Math.abs(num) >= 1e6) return `${(num / 1e6).toFixed(1)}M`
  if (Math.abs(num) >= 1e3) return `${(num / 1e3).toFixed(1)}K`
  return String(Math.round(num))
}
function pct(n) { return `${Number(n || 0).toFixed(1)}%` }
function money(n) { return n ? `$${Number(n).toFixed(3)}` : '$0.000' }
function since(epoch) {
  if (!epoch) return '—'
  const sec = Math.max(0, Math.floor(Date.now()/1000 - epoch))
  if (sec < 60) return `${sec}s ago`
  if (sec < 3600) return `${Math.floor(sec/60)}m ago`
  return `${Math.floor(sec/3600)}h ago`
}
function duration(sec) {
  sec = Number(sec || 0)
  if (sec < 60) return `${sec}s`
  const h = Math.floor(sec/3600), m = Math.floor((sec%3600)/60)
  return h ? `${h}h ${m}m` : `${m}m`
}

function useLiveData() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [tick, setTick] = useState(0)
  useEffect(() => {
    let alive = true
    async function load() {
      try {
        const res = await fetch(`/data/live.json?t=${Date.now()}`)
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
        const json = await res.json()
        if (alive) { setData(json); setError(null) }
      } catch (e) {
        if (alive) setError(e.message)
      }
    }
    load()
    const id = setInterval(() => { setTick(v => v + 1); load() }, 20000)
    return () => { alive = false; clearInterval(id) }
  }, [])
  return { data, error, tick }
}

function App() {
  const { data, error } = useLiveData()
  if (!data) return <div className="boot"><Orbit className="spin"/> <span>Booting Cosmos Mission Control…</span>{error && <small>{error}</small>}</div>
  return <Dashboard data={data} error={error} />
}

function Dashboard({ data, error }) {
  const cs = data.current_session || {}
  const totals = data.totals || {}
  const t24 = totals.last_24h || {}
  const t7 = totals.last_7d || {}
  const quota = data.quotas || []
  const providers = data.providers || []
  const daily = data.series?.daily || []
  const hourly = data.series?.hourly_activity || []
  const contextPct = Math.min(100, Number(cs.context_pct_estimate || 0))
  const effectiveTokens = (cs.input_tokens || 0) + (cs.output_tokens || 0) + (cs.reasoning_tokens || 0)
  const totalTokens7 = (t7.input_tokens || 0) + (t7.output_tokens || 0) + (t7.reasoning_tokens || 0)
  const liveHealth = data.health || {}

  return <main className="shell">
    <TopNav data={data}/>
    <section className="hero-grid">
      <div className="hero-card glass">
        <div className="eyebrow"><Sparkles size={14}/> LIVE AGENTIC OS</div>
        <h1>Cosmos Mission Control</h1>
        <p>Real-time Hermes usage, model pressure, workflows, reset visibility, and agent operations — designed for iPad, phone, and desktop.</p>
        <div className="hero-actions">
          <a className="btn primary" href="/data/live.json" target="_blank">Open live JSON <ChevronRight size={16}/></a>
          <button className="btn ghost" onClick={() => location.reload()}><RefreshCcw size={16}/> Refresh</button>
        </div>
      </div>
      <LiveNow cs={cs} data={data}/>
    </section>

    <section className="kpi-grid">
      <Kpi icon={Gauge} label="Session Context" value={pct(contextPct)} sub={`${compact(cs.context_tokens_used)} / ${compact(cs.context_limit_estimate)} est.`} tone="cyan"/>
      <Kpi icon={Zap} label="Current Session" value={compact(effectiveTokens)} sub={`${compact(cs.cache_read_tokens)} cache read`} tone="violet"/>
      <Kpi icon={TerminalSquare} label="Tool Calls" value={compact(cs.tool_call_count)} sub={`${compact(cs.api_call_count)} API calls`} tone="green"/>
      <Kpi icon={CalendarClock} label="7d Tokens" value={compact(totalTokens7)} sub={`${compact(t7.tool_call_count)} tools · ${compact(totals.session_count)} sessions`} tone="pink"/>
    </section>

    <section className="dashboard-grid">
      <Panel className="span-8" title="Usage Command Graph" icon={BarChart3} action={<Segmented/>}>
        <ResponsiveContainer width="100%" height={310}>
          <AreaChart data={daily} margin={{ left: -20, right: 10, top: 20, bottom: 0 }}>
            <defs>
              <linearGradient id="tokenFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#00e5ff" stopOpacity=".55"/><stop offset="100%" stopColor="#00e5ff" stopOpacity="0"/></linearGradient>
              <linearGradient id="cacheFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#7c3cff" stopOpacity=".38"/><stop offset="100%" stopColor="#7c3cff" stopOpacity="0"/></linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/>
            <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="rgba(255,255,255,.42)" fontSize={12}/>
            <YAxis tickFormatter={compact} tickLine={false} axisLine={false} stroke="rgba(255,255,255,.42)" fontSize={12}/>
            <Tooltip content={<ChartTip/>}/>
            <Area type="monotone" dataKey="cache" stroke="#7c3cff" fill="url(#cacheFill)" strokeWidth={2} name="Cache read"/>
            <Area type="monotone" dataKey="tokens" stroke="#00e5ff" fill="url(#tokenFill)" strokeWidth={3} name="Input+output+reasoning"/>
          </AreaChart>
        </ResponsiveContainer>
      </Panel>

      <Panel className="span-4" title="Context Pressure" icon={Cpu}>
        <div className="gauge-wrap">
          <ResponsiveContainer width="100%" height={220}>
            <RadialBarChart cx="50%" cy="58%" innerRadius="62%" outerRadius="95%" barSize={15} data={[{name:'context', value: contextPct, fill:'#00e5ff'}]} startAngle={210} endAngle={-30}>
              <PolarAngleAxis type="number" domain={[0,100]} tick={false}/>
              <RadialBar dataKey="value" cornerRadius={30} background={{ fill: 'rgba(255,255,255,.07)' }}/>
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="gauge-center"><b>{pct(contextPct)}</b><span>of estimated context</span></div>
        </div>
        <div className="split-stats">
          <span>Input <b>{compact(cs.input_tokens)}</b></span>
          <span>Output <b>{compact(cs.output_tokens)}</b></span>
          <span>Reasoning <b>{compact(cs.reasoning_tokens)}</b></span>
        </div>
      </Panel>

      <Panel className="span-5" title="Model Quotas & Reset Visibility" icon={TimerReset}>
        <div className="quota-list">
          {quota.map((q, i) => <div className="quota-row" key={q.provider || i}>
            <div><strong>{q.provider}</strong><span>{q.status || 'not connected'}</span></div>
            <div className="quota-meter"><i style={{width:`${q.percent_known ? q.percent_known : 18}%`}}/></div>
            <small>{q.reset || q.reset_status || 'Provider reset source not connected'}</small>
          </div>)}
          {!quota.length && <Empty text="No provider quota APIs connected yet."/>}
        </div>
      </Panel>

      <Panel className="span-7" title="24h Activity Pulse" icon={Activity}>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={hourly} margin={{ left: -20, right: 8, top: 10, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,.07)" vertical={false}/>
            <XAxis dataKey="hour" interval="preserveStartEnd" minTickGap={18} tickLine={false} axisLine={false} stroke="rgba(255,255,255,.38)" fontSize={11}/>
            <YAxis tickFormatter={compact} tickLine={false} axisLine={false} stroke="rgba(255,255,255,.38)" fontSize={11}/>
            <Tooltip content={<ChartTip/>}/>
            <Bar dataKey="tokens" radius={[8,8,0,0]} name="Tokens">
              {hourly.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]}/>) }
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel className="span-6" title="Agent Company / Pantheon" icon={Bot}>
        <div className="agent-grid">
          {departments.map((d) => <div className={`agent-card ${d.tone}`} key={d.name}>
            <d.icon size={22}/><div><b>{d.name}</b><span>{d.desc}</span></div>
          </div>)}
        </div>
      </Panel>

      <Panel className="span-6" title="Provider / Model Usage" icon={CircleDollarSign}>
        <div className="provider-table">
          {providers.map((p, i) => <div className="provider-row" key={i}>
            <div><b>{p.model || p.provider}</b><span>{p.provider || 'provider'}</span></div>
            <span>{compact(p.tokens)} tokens</span>
            <span>{compact(p.sessions)} sessions</span>
            <span>{money(p.cost_usd)}</span>
          </div>)}
          {!providers.length && <Empty text="Provider rollup will appear after sessions are recorded."/>}
        </div>
      </Panel>

      <Panel className="span-4" title="System Health" icon={Server}>
        <HealthGrid health={liveHealth} git={data.git} disk={data.disk}/>
      </Panel>

      <Panel className="span-4" title="Cron Registry" icon={Clock3}>
        <div className="cron-list">
          {(data.cron || []).map((c, i) => <div className="cron" key={i}><CheckCircle2 size={16}/><div><b>{c.name}</b><span>{c.schedule || c.next_run_at || 'scheduled'}</span></div></div>)}
        </div>
      </Panel>

      <Panel className="span-4" title="Secrets Boundary" icon={ShieldCheck}>
        <div className="secret-grid">
          {(data.credentials || []).map((c, i) => <div className="secret" key={i}><KeyRound size={16}/><span>{c.name || c}</span></div>)}
          {!(data.credentials||[]).length && <Empty text="No exposed secret values. Key names only."/>}
        </div>
      </Panel>
    </section>

    <footer className="footer-note">
      <span>Generated {since(data.generated_at_epoch)} · source: real local telemetry</span>
      {error && <span className="warn"><AlertTriangle size={14}/> {error}</span>}
    </footer>
  </main>
}

function TopNav({ data }) {
  return <header className="topnav">
    <div className="brand"><div className="logo"><Orbit size={20}/></div><div><b>Cosmos</b><span>Agentic OS</span></div></div>
    <nav><a href="#">Mission</a><a href="#">Usage</a><a href="#">Agents</a><a href="#">Cron</a></nav>
    <div className="live-pill"><span/> Live · {since(data.generated_at_epoch)}</div>
  </header>
}
function LiveNow({ cs, data }) {
  return <div className="live-card glass">
    <div className="card-head"><span>Current Session</span><Activity size={18}/></div>
    <h2>{cs.model || 'Unknown model'}</h2>
    <p>{cs.provider || 'provider'} · {cs.source || 'source'} · {duration(cs.duration_seconds)}</p>
    <div className="live-stack">
      <MetricLine label="Messages" value={compact(cs.message_count)}/>
      <MetricLine label="API calls" value={compact(cs.api_call_count)}/>
      <MetricLine label="Tools" value={compact(cs.tool_call_count)}/>
      <MetricLine label="Cost status" value={cs.cost_status || 'unknown'}/>
    </div>
  </div>
}
function Kpi({ icon: Icon, label, value, sub, tone }) { return <article className={`kpi ${tone}`}><Icon size={21}/><span>{label}</span><b>{value}</b><small>{sub}</small></article> }
function Panel({ title, icon: Icon, children, className='', action }) { return <section className={`panel ${className}`}><div className="panel-title"><div><Icon size={18}/><h3>{title}</h3></div>{action}</div>{children}</section> }
function MetricLine({ label, value }) { return <div className="metric-line"><span>{label}</span><b>{value}</b></div> }
function Segmented() { return <div className="seg"><button>Tokens</button><button>Cache</button><button>Tools</button></div> }
function Empty({ text }) { return <div className="empty">{text}</div> }
function ChartTip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return <div className="tip"><b>{label}</b>{payload.map((p,i)=><span key={i}>{p.name}: {compact(p.value)}</span>)}</div>
}
function HealthGrid({ health={}, git={}, disk={} }) {
  const items = [
    ['Dashboard', health.dashboard_server || health.server || 'running', Cloud],
    ['Tunnel', health.localtunnel || 'active', Link2],
    ['Git', git?.status || git?.branch || 'synced', GitBranch],
    ['Disk', disk?.pct ? pct(disk.pct) : 'ok', HardDrive]
  ]
  return <div className="health-grid">{items.map(([k,v,Icon]) => <div className="health" key={k}><Icon size={18}/><span>{k}</span><b>{v}</b></div>)}</div>
}

createRoot(document.getElementById('root')).render(<App />)
