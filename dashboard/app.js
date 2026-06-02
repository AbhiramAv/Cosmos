async function loadData() {
  const res = await fetch('./data/cosmos.json');
  const data = await res.json();
  render(data);
}

function el(tag, cls, html) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (html) node.innerHTML = html;
  return node;
}

function render(data) {
  document.getElementById('systemStatus').innerHTML = data.status.map(item => `
    <div class="integration">
      <strong>${item.label}</strong>
      <p><span class="${item.class}">${item.value}</span></p>
    </div>
  `).join('');

  document.getElementById('missionsList').innerHTML = data.missions.map(m => `
    <div class="mission">
      <strong>${m.title}</strong>
      <p>${m.description}</p>
      <div class="progress"><span style="width:${m.progress}%"></span></div>
      <span class="badge">${m.status} · ${m.progress}%</span>
    </div>
  `).join('');

  document.getElementById('queueList').innerHTML = data.queue.map(t => `
    <div class="task">
      <strong>${t.title}</strong>
      <p>${t.owner} · ${t.status}</p>
      <span class="badge">${t.priority}</span>
    </div>
  `).join('');

  const departments = data.departments.map(dep => `
    <div class="card">
      <strong>${dep.name}</strong>
      <p>${dep.purpose}</p>
      <span class="badge">${dep.agents.length} agents</span>
      ${dep.agents.map(a => `<p>• ${a}</p>`).join('')}
    </div>
  `).join('');
  document.getElementById('orgChart').innerHTML = `
    <div class="card ceo-card">
      <p class="eyebrow">CEO</p>
      <h2>Cosmos CEO</h2>
      <p>Routes work, manages permissions, supervises subagents, tracks memory, and reports verified outcomes to Ram.</p>
      <span class="badge">orchestrator</span>
    </div>
    ${departments}
  `;

  document.getElementById('dreamList').innerHTML = data.dreams.map(d => `
    <div class="dream"><strong>${d.title}</strong><p>${d.note}</p><span class="badge">${d.type}</span></div>
  `).join('');

  document.getElementById('usageList').innerHTML = data.usage.map(u => `
    <div class="metric"><strong>${u.value}</strong><p>${u.label}</p><span class="badge">${u.note}</span></div>
  `).join('');

  document.getElementById('integrationsList').innerHTML = data.integrations.map(i => `
    <div class="integration"><strong>${i.name}</strong><p><span class="${i.class}">${i.status}</span> · ${i.note}</p></div>
  `).join('');

  document.getElementById('artifactList').innerHTML = data.artifacts.map(a => `
    <div class="artifact"><strong>${a.title}</strong><p>${a.description}</p><span class="badge">${a.type}</span></div>
  `).join('');

  document.getElementById('cronList').innerHTML = data.cron.map(c => `
    <div class="cron"><strong>${c.name}</strong><p>${c.schedule}</p><span class="badge">${c.status}</span></div>
  `).join('');
}

loadData().catch(err => {
  document.body.innerHTML = `<pre style="padding: 24px; color: #fb7185">Dashboard load failed: ${err.message}</pre>`;
});
