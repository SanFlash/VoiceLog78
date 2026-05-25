// ─── Global utilities ────────────────────────────────────────────────
function statusBadge(status) {
  const map = {
    'Created': 'badge-created',
    'Recording': 'badge-recording',
    'Uploaded': 'badge-uploaded',
    'In Progress': 'badge-in-progress',
    'Completed': 'badge-completed',
    'Error': 'badge-error',
  };
  const cls = map[status] || 'badge-created';
  return `<span class="badge ${cls}">${status}</span>`;
}

function formatDateTime(str) {
  return str;
}
