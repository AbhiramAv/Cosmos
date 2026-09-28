/* Cosmos HQ dashboard — renders company.json, refreshes every 60s. */
const ISSUE_URL =
  "https://github.com/AbhiramAv/Cosmos/issues/new" +
  "?labels=" + encodeURIComponent("task") +
  "&title=" + encodeURIComponent("[Task] ") +
  "&body=" + encodeURIComponent(
    "Describe the task for the CEO:\n\n- What should be done:\n- Any deadline:\n- Anything the agents should know:\n\n(The CEO will route this to the right department and agents.)"
  );

const COLUMNS = [
  ["queued", "Queued"],
  ["assigned", "Assigned"],
  ["in_progress", "In progress"],
  ["in_review", "In review"],
  ["blocked", "Blocked"],
  ["done", "Done"],
];

const el = (id) => document.getElementById(id);

function initials(name) {
  return name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}
function timeAgo(iso) {
  const s = Math.max(1, Math.round((Date.now() - new Date(iso).getTime()) / 1000));
  if (s < 60) return s + "s ago";
  const m = Math.round(s / 60);
  if (m < 60) return m + "m ago";
  const h = Math.round(m / 60);
  if (h < 24) return h + "h ago";
  return Math.round(h / 24) + "d ago";
}
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function renderCEO(ceo) {
  el("ceo").innerHTML =
    `<div class="avatar">${initials(ceo.name)}</div>
     <div class="who">
       <h3>${esc(ceo.name)}</h3>
       <p class="role">Chief executive · routes work, reviews output, reports to Ram</p>
       <span class="pill ${esc(ceo.status)}">${esc(ceo.status.replace("_", " "))}</span>
       ${ceo.current_task ? `<p class="now">Now: <b>${esc(ceo.current_task)}</b></p>` : ""}
     </div>`;
}

function renderDepartments(depts) {
  el("departments").innerHTML = depts.map((d) => {
    const working = d.agents.filter((a) => a.status === "working").length;
    const cards = d.agents.map((a) => `
      <div class="agent-card">
        <div class="avatar agent-avatar">${initials(a.name)}</div>
        <div class="who">
          <h3>${esc(a.name)}</h3>
          <p class="role">${esc(a.role)}</p>
          <span class="pill ${esc(a.status)}">${esc(a.status)}</span>
          ${a.current_task ? `<p class="now">Now: <b>${esc(a.current_task)}</b></p>` : ""}
        </div>
      </div>`).join("");
    return `<div class="dept">
      <div class="dept-head"><h3>${esc(d.name)}</h3>
      <span class="count">${working}/${d.agents.length} working</span></div>
      <div class="agents-grid">${cards}</div>
    </div>`;
  }).join("");
}

function renderTasks(tasks) {
  el("kanban").innerHTML = COLUMNS.map(([key, label]) => {
    const items = tasks.filter((t) => t.status === key);
    const cards = items.map((t) => `
      <div class="task">
        <h5>${esc(t.title)}</h5>
        <p class="chain">${t.chain.map((c, i) =>
          i === t.chain.length - 1 ? `<b>${esc(c)}</b>` : esc(c)).join(" → ")}</p>
        <div class="bar"><i style="width:${t.progress || 0}%"></i></div>
        <div class="task-meta">
          <span>${esc(t.assignee || "")}</span>
          <span>${t.progress || 0}% · ${timeAgo(t.updated_at)}</span>
        </div>
      </div>`).join("");
    return `<div class="col"><h4>${label} <span class="n">${items.length}</span></h4>
      ${cards || `<p class="empty">—</p>`}</div>`;
  }).join("");
}

function renderFeed(id, items) {
  el(id).innerHTML = items.slice(0, 30).map((n) => `
    <li class="${n.kind ? "kind-" + esc(n.kind) : ""}">
      <time>${timeAgo(n.at)}</time>${esc(n.text)}
    </li>`).join("") || `<li>Nothing yet.</li>`;
}

async function load() {
  try {
    const res = await fetch("company.json", { cache: "no-store" });
    const s = await res.json();
    el("updated").textContent = "updated " + timeAgo(s.updated_at);
    renderCEO(s.ceo);
    renderDepartments(s.departments);
    renderTasks(s.tasks || []);
    renderFeed("activity", s.activity || []);
    renderFeed("notifications", s.notifications || []);
  } catch (e) {
    el("updated").textContent = "couldn't load data";
  }
}

el("new-task").href = ISSUE_URL;
load();
setInterval(load, 60000);
