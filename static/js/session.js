// ─── Dashboard Session Management ────────────────────────────────────
let sessions = [];

async function loadSessions() {
  try {
    const res = await fetch('/sessions/');
    sessions = await res.json();
    renderSessions(sessions);
    updateStats(sessions);
  } catch (e) {
    document.getElementById('sessionsTable').innerHTML =
      `<tr><td colspan="6" class="empty-state"><div class="icon">⚠️</div><div>Failed to load sessions</div></td></tr>`;
  }
}

function updateStats(sessions) {
  document.getElementById('statTotal').textContent = sessions.length;
  document.getElementById('statCompleted').textContent = sessions.filter(s => s.status === 'Completed').length;
  document.getElementById('statProcessing').textContent = sessions.filter(s => s.status === 'In Progress' || s.status === 'Uploaded').length;
  document.getElementById('statCreated').textContent = sessions.filter(s => s.status === 'Created').length;
}

function renderSessions(sessions) {
  const tbody = document.getElementById('sessionsTable');
  if (!sessions.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state"><div class="icon">🎙️</div><div>No sessions yet. Create your first one!</div></td></tr>`;
    return;
  }
  tbody.innerHTML = sessions.map(s => `
    <tr>
      <td>
        <div style="font-weight:600;">${s.session_name}</div>
        ${s.notes ? `<div class="text-muted text-xs mt-1 truncate" style="max-width:200px;">${s.notes}</div>` : ''}
      </td>
      <td>${s.interviewer}</td>
      <td style="color:var(--text-sub);font-size:0.82rem;">${s.time}</td>
      <td>${statusBadge(s.status)}</td>
      <td style="color:var(--text-muted);font-size:0.82rem;">${s.created_at}</td>
      <td>
        <div class="flex gap-2">
          <a href="/session/${s.id}" class="btn btn-outline btn-sm">View</a>
          ${s.status === 'Completed'
            ? `<a href="/transcript/${s.id}" class="btn btn-primary btn-sm" onclick="openTranscriptForSession(event,${s.id})">Transcript</a>`
            : `<a href="/app-view" class="btn btn-outline btn-sm">Record</a>`}
        </div>
      </td>
    </tr>
  `).join('');
}

async function openTranscriptForSession(e, sessionId) {
  e.preventDefault();
  // Find recording for session
  const res = await fetch(`/sessions/${sessionId}`);
  // Navigate to latest recording transcript
  window.location.href = `/transcript/${sessionId}`;
}

// Modal
function openModal() {
  const modal = document.getElementById('createModal');
  modal.style.display = 'flex';
  // Default time to now+30min
  const d = new Date(Date.now() + 30 * 60000);
  d.setSeconds(0);
  document.getElementById('sessionTime').value = d.toISOString().slice(0, 16);
}

function closeModal() {
  document.getElementById('createModal').style.display = 'none';
}

document.getElementById('openCreateModal')?.addEventListener('click', openModal);
document.getElementById('createModal')?.addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});

document.getElementById('createForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('createBtn');
  btn.innerHTML = '<span class="spinner"></span> Creating...';
  btn.disabled = true;

  try {
    const res = await fetch('/sessions/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        session_name: document.getElementById('sessionName').value,
        interviewer: document.getElementById('interviewer').value,
        time: document.getElementById('sessionTime').value,
        notes: document.getElementById('notes').value,
      })
    });
    const data = await res.json();
    if (data.success) {
      closeModal();
      document.getElementById('createForm').reset();
      await loadSessions();
    }
  } catch (e) {
    console.error(e);
  } finally {
    btn.innerHTML = 'Create Session'; btn.disabled = false;
  }
});

// Init
loadSessions();
// Auto-refresh every 10s to pick up status updates
setInterval(loadSessions, 10000);
