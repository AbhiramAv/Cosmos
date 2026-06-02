let DATA=null; let chartMode='tokens';
const departments=[
  ['CEO','Cosmos CEO','routes work, enforces permissions, reviews outputs','ceo'],
  ['Operations','Task Manager · Cron Manager · Admin Assistant','daily execution and admin',''],
  ['Knowledge','Obsidian Librarian · Memory Curator · Daily Log','memory, notes, decisions',''],
  ['Research','Quick Researcher · Scraper · Source Validator','public research and synthesis',''],
  ['Engineering','Coding · Debugging · GitHub · Supabase','code and infrastructure',''],
  ['Life OS','Habit · Reflection · Goal Tracker','personal operating systems',''],
  ['Observability','Usage · Cost · Failure Monitor','spend, failures, dashboards','']
];
function fmt(n){ if(n===null||n===undefined) return '—'; n=Number(n); if(!isFinite(n)) return '—'; if(Math.abs(n)>=1e9) return (n/1e9).toFixed(1)+'B'; if(Math.abs(n)>=1e6) return (n/1e6).toFixed(1)+'M'; if(Math.abs(n)>=1e3) return (n/1e3).toFixed(1)+'K'; return String(Math.round(n)); }
function money(n){return n? '$'+Number(n).toFixed(4): '$0';}
function dur(s){s=Number(s||0);const h=Math.floor(s/3600),m=Math.floor((s%3600)/60); if(h) return `${h}h ${m}m`; return `${m}m`;}
function pct(n){return n===null||n===undefined?'—':Number(n).toFixed(1)+'%';}
async function load(){
  const res=await fetch('./data/live.json?ts='+Date.now());
  DATA=await res.json(); render();
}
function render(){
  const d=DATA, s=d.current_session, t=d.totals;
  document.getElementById('liveStatus').textContent='Live metrics online';
  document.getElementById('lastUpdated').textContent=`Updated ${new Date(d.generated_at).toLocaleString()} · refreshes automatically every 20 seconds`;
  document.getElementById('sessionTitle').textContent=s.title||s.id||'Current session';
  document.getElementById('sessionMeta').innerHTML=`${s.provider} / ${s.model}<br>${s.source} · ${dur(s.duration_seconds)} active<br>${s.id}`;
  const kpis=[
    ['Context used',fmt(s.context_tokens_used),`${pct(s.context_pct_estimate)} of estimated ${fmt(s.context_limit_estimate)}`],
    ['Cache read',fmt(s.cache_read_tokens),'current session cached tokens'],
    ['API calls',fmt(s.api_call_count),'current session model calls'],
    ['24h tokens',fmt(t.last_24h.input_tokens+t.last_24h.output_tokens+t.last_24h.reasoning_tokens),`${fmt(t.last_24h.tool_call_count)} tool calls`],
    ['All sessions',fmt(t.session_count),`${fmt(t.all.message_count)} messages · ${fmt(t.all.tool_call_count)} tools`]
  ];
  document.getElementById('kpis').innerHTML=kpis.map(x=>`<div class="kpi"><label>${x[0]}</label><strong>${x[1]}</strong><span>${x[2]}</span></div>`).join('');
  drawGauge('contextGauge', s.context_pct_estimate||0);
  document.getElementById('contextPct').textContent=pct(s.context_pct_estimate);
  document.getElementById('contextLegend').innerHTML=`
    <div class="mini-stat"><b>${fmt(s.input_tokens)}</b><span>input tokens</span></div>
    <div class="mini-stat"><b>${fmt(s.output_tokens)}</b><span>output tokens</span></div>
    <div class="mini-stat"><b>${fmt(s.reasoning_tokens)}</b><span>reasoning tokens</span></div>
    <div class="mini-stat"><b>${fmt(s.cache_read_tokens)}</b><span>cache read tokens</span></div>`;
  document.getElementById('quotaCards').innerHTML=d.quota.map(q=>{
    const p=q.pct==null?0:q.pct, used=q.used==null?'not connected':fmt(q.used), lim=q.limit==null?'no hard limit visible':fmt(q.limit);
    const warn=q.pct==null?'warn':'';
    return `<div class="quota-card"><div class="quota-top"><b>${q.provider}</b><span class="source-badge ${warn}">${q.unit}</span></div><div class="quota-value">${used}</div><span>limit: ${lim}</span><div class="bar"><i style="width:${Math.min(100,p)}%"></i></div><p class="muted">reset: ${q.reset_in}</p><span>${q.source}</span></div>`
  }).join('');
  drawBars('dailyChart', d.series.daily, chartMode);
  drawPulse('pulseChart', d.series.hourly_activity);
  renderModels(d.by_model);
  renderHealth(d);
  renderAgents();
  renderCron(d.cron);
  renderQuality(d);
}
function drawGauge(id,value){
  const c=document.getElementById(id),ctx=c.getContext('2d'),w=c.width,h=c.height;ctx.clearRect(0,0,w,h);const cx=w/2,cy=190,r=145,start=Math.PI,end=0;
  ctx.lineWidth=22;ctx.lineCap='round';ctx.strokeStyle='rgba(255,255,255,.08)';ctx.beginPath();ctx.arc(cx,cy,r,start,end);ctx.stroke();
  const grad=ctx.createLinearGradient(50,0,w-50,0);grad.addColorStop(0,'#7170ff');grad.addColorStop(.55,'#22d3ee');grad.addColorStop(1,value>75?'#fb7185':'#10b981');ctx.strokeStyle=grad;ctx.beginPath();ctx.arc(cx,cy,r,start,start+(end-start)*(Math.min(value,100)/100));ctx.stroke();
  for(let i=0;i<=10;i++){const a=start+(end-start)*i/10;const x1=cx+Math.cos(a)*(r-22),y1=cy+Math.sin(a)*(r-22),x2=cx+Math.cos(a)*(r-8),y2=cy+Math.sin(a)*(r-8);ctx.strokeStyle='rgba(255,255,255,.18)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
}
function drawBars(id,rows,key){
  const c=document.getElementById(id),ctx=c.getContext('2d'),w=c.clientWidth*devicePixelRatio,h=c.height*devicePixelRatio;c.width=w;c.height=h;ctx.clearRect(0,0,w,h);const pad=42*devicePixelRatio;const vals=rows.map(r=>r[key]||0),max=Math.max(...vals,1);ctx.font=`${12*devicePixelRatio}px JetBrains Mono`;ctx.fillStyle='#8a8f98';ctx.strokeStyle='rgba(255,255,255,.06)';
  for(let i=0;i<4;i++){let y=pad+(h-pad*2)*i/3;ctx.beginPath();ctx.moveTo(pad,y);ctx.lineTo(w-pad,y);ctx.stroke();}
  const bw=(w-pad*2)/rows.length*.62;rows.forEach((r,i)=>{const x=pad+(w-pad*2)*(i+.5)/rows.length-bw/2;const bh=(h-pad*2)*(r[key]||0)/max;const y=h-pad-bh;const g=ctx.createLinearGradient(0,y,0,h-pad);g.addColorStop(0,'#22d3ee');g.addColorStop(1,'#5e6ad2');ctx.fillStyle=g;roundRect(ctx,x,y,bw,bh,8*devicePixelRatio,true);ctx.fillStyle='#8a8f98';ctx.textAlign='center';ctx.fillText(r.label,x+bw/2,h-pad+22*devicePixelRatio);});
  ctx.fillStyle='#d0d6e0';ctx.textAlign='left';ctx.fillText(`${key}: max ${fmt(max)}`,pad,22*devicePixelRatio);
}
function drawPulse(id,rows){
  const c=document.getElementById(id),ctx=c.getContext('2d'),w=c.clientWidth*devicePixelRatio,h=c.height*devicePixelRatio;c.width=w;c.height=h;ctx.clearRect(0,0,w,h);const pad=30*devicePixelRatio,max=Math.max(...rows.map(r=>r.messages+r.tools),1);ctx.strokeStyle='#7170ff';ctx.lineWidth=3*devicePixelRatio;ctx.beginPath();rows.forEach((r,i)=>{const x=pad+(w-pad*2)*i/(rows.length-1);const y=h-pad-(h-pad*2)*(r.messages+r.tools)/max;if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);});ctx.stroke();ctx.fillStyle='rgba(113,112,255,.12)';ctx.lineTo(w-pad,h-pad);ctx.lineTo(pad,h-pad);ctx.closePath();ctx.fill();ctx.fillStyle='#8a8f98';ctx.font=`${12*devicePixelRatio}px JetBrains Mono`;ctx.fillText('messages + tools',pad,20*devicePixelRatio);}
function roundRect(ctx,x,y,w,h,r,fill){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);if(fill)ctx.fill();}
function renderModels(rows){document.getElementById('modelTable').innerHTML=`<div class="model-row header"><span>Provider/model</span><span>Sessions</span><span>Tokens</span><span>Cache</span><span>Cost</span></div>`+rows.map(r=>`<div class="model-row"><span><b>${r.provider}</b><br><span class="muted mono">${r.model}</span></span><span>${fmt(r.sessions)}</span><span>${fmt(r.tokens)}</span><span>${fmt(r.cache)}</span><span>${money(r.cost)}</span></div>`).join('');}
function renderHealth(d){const p=d.processes;const disk=d.disk;document.getElementById('healthList').innerHTML=[['Dashboard server',`${p.dashboard_server} process(es)`],['Localtunnel',`${p.localtunnel} process(es)`],['Git',d.git.status.replaceAll('\n','<br>')],['Last commit',d.git.last_commit],['Disk used',`${pct(disk.pct)} · ${fmt(disk.free)}B free`]].map(x=>`<div class="health-item"><b>${x[0]}</b><span>${x[1]}</span></div>`).join('');}
function renderAgents(){document.getElementById('agentMap').innerHTML=departments.map(a=>`<div class="agent-card ${a[3]}"><div class="micro">${a[0]}</div><b>${a[1]}</b><p class="muted">${a[2]}</p><span>${a[3]?'orchestrator':'department'}</span></div>`).join('');}
function renderCron(rows){document.getElementById('cronList').innerHTML=rows.map(c=>`<div class="cron-item"><div><b>${c.name}</b><br><span>${c.schedule} · ${c.state} · last ${c.last_status||'pending'}</span></div><span class="source-badge ${c.enabled?'':'warn'}">${c.enabled?'on':'off'}</span></div>`).join('');}
function renderQuality(d){document.getElementById('qualityList').innerHTML=d.data_quality.map(q=>`<div class="quality-item"><b>Telemetry note</b><span>${q}</span></div>`).join('')+Object.entries(d.providers).map(([k,v])=>`<div class="quality-item"><b>${k} credentials</b><span class="${v?'green':'yellow'}">${v?'present':'not found locally'}</span></div>`).join('');}
document.addEventListener('click',e=>{if(e.target.matches('.tabs button')){document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('active'));e.target.classList.add('active');chartMode=e.target.dataset.chart;render();}});
load().catch(e=>{document.getElementById('liveStatus').textContent='Failed: '+e.message});setInterval(load,20000);addEventListener('resize',()=>DATA&&render());
