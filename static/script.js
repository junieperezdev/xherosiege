const priorityLabel = { high: 'High', med: 'Medium', low: 'Low' };

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

function renderKPIs(kpis) {
  const row = document.getElementById('kpiRow');
  row.innerHTML = kpis.map(k => `
    <div class="kpi">
      <div class="label">${k.label}</div>
      <div class="value">${k.value}</div>
      <div class="delta ${k.trend}">${k.trend === 'up' ? '▲' : k.trend === 'down' ? '▼' : '—'} ${k.delta}</div>
    </div>
  `).join('');
}

function renderCalendar(today, days) {
  const row = document.getElementById('weekRow');
  row.innerHTML = days.map(d => `
    <div class="day ${d.day === today ? 'today' : ''}">
      <div class="dname">${d.day}</div>
      <div class="dnum">${d.date}</div>
      ${d.events.map(ev => `
        <div class="ev ${ev.team}"><span class="t">${ev.time}</span>${ev.title}</div>
      `).join('')}
    </div>
  `).join('');
}

function renderTeams(teams) {
  const list = document.getElementById('teamList');
  const statusText = { ontrack: 'On track', atrisk: 'At risk', blocked: 'Blocked' };
  list.innerHTML = teams.map(t => `
    <div class="team">
      <div class="head">
        <h3>${t.name}</h3>
        <span class="status-pill ${t.status}">${statusText[t.status] || t.status}</span>
      </div>
      <div class="focus">${t.focus}</div>
      <div class="capacity"><div style="width:${t.capacity}%"></div></div>
      <div class="capline"><span>Capacity</span><span>${t.capacity}% · ${t.headcount} people</span></div>
    </div>
  `).join('');
}

async function loadTasks() {
  const tasks = await fetchJSON('/api/tasks');
  const list = document.getElementById('taskList');
  const doneCount = tasks.filter(t => t.done).length;

  list.innerHTML = tasks.map(t => `
    <div class="task ${t.done ? 'done' : ''}">
      <input type="checkbox" ${t.done ? 'checked' : ''} data-id="${t.id}">
      <span class="title">${t.title}</span>
      <span class="owner">${t.owner}</span>
      <span class="prio ${t.priority}">${priorityLabel[t.priority] || t.priority}</span>
      <button class="remove" data-id="${t.id}" title="Remove task">✕</button>
    </div>
  `).join('');

  document.getElementById('taskProgress').textContent = `${doneCount} of ${tasks.length} done`;
  document.getElementById('taskCountTag').textContent = tasks.length - doneCount;

  list.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', async (e) => {
      const id = e.target.getAttribute('data-id');
      await fetchJSON(`/api/tasks/${id}/toggle`, { method: 'POST' });
      loadTasks();
    });
  });

  list.querySelectorAll('.remove').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.getAttribute('data-id');
      await fetchJSON(`/api/tasks/${id}`, { method: 'DELETE' });
      loadTasks();
    });
  });
}

async function init() {
  const overview = await fetchJSON('/api/overview');

  document.getElementById('todayDate').textContent = overview.today_label;
  document.getElementById('companyStats').textContent =
    `${overview.company.stats.projects} active projects · ${overview.company.stats.teams} teams · ${overview.company.stats.people} people`;

  renderKPIs(overview.kpis);
  renderCalendar(overview.today, overview.calendar);
  renderTeams(overview.teams);
  await loadTasks();
}

document.getElementById('addTaskForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const titleInput = document.getElementById('newTaskTitle');
  const priority = document.getElementById('newTaskPriority').value;
  const title = titleInput.value.trim();
  if (!title) return;

  await fetchJSON('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, priority, owner: 'You' }),
  });

  titleInput.value = '';
  loadTasks();
});

// Theme toggle
const themeBtn = document.getElementById('themeToggle');
function applyTheme(mode) {
  if (mode) {
    document.documentElement.setAttribute('data-theme', mode);
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  themeBtn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? 'Switch to light' : 'Switch to dark';
}
const storedTheme = localStorage.getItem('northfield-theme');
if (storedTheme) applyTheme(storedTheme);
themeBtn.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem('northfield-theme', next);
});

init();
