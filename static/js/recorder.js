// ─── App View Recorder ───────────────────────────────────────────────
let mediaRecorder = null;
let audioChunks = [];
let timerInterval = null;
let elapsedSeconds = 0;
let waveformAnimFrame = null;
let analyser = null;
let audioCtx = null;
let selectedSessionId = null;
let isRecording = false;
let currentRecordingId = null;

// ─── Auth ─────────────────────────────────────────────────────────────
async function appLogin() {
  const email = document.getElementById('appEmail').value;
  const password = document.getElementById('appPassword').value;
  try {
    const res = await fetch('/auth/login-app', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email, password})
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('appLoginScreen').style.display = 'none';
      document.getElementById('appMainScreen').style.display = 'flex';
      document.getElementById('appMainScreen').style.flexDirection = 'column';
      loadAppSessions();
    } else {
      document.getElementById('appLoginError').style.display = 'block';
      document.getElementById('appLoginError').textContent = data.message || 'Login failed';
    }
  } catch (e) {
    document.getElementById('appLoginError').style.display = 'block';
    document.getElementById('appLoginError').textContent = 'Network error';
  }
}

function appLogout() {
  window.location.href = '/auth/logout';
}

// ─── Sessions ─────────────────────────────────────────────────────────
async function loadAppSessions() {
  try {
    const res = await fetch('/sessions/');
    const sessions = await res.json();
    renderAppSessions(sessions);
  } catch (e) {
    document.getElementById('appSessionList').innerHTML =
      '<div style="color:var(--text-muted);font-size:0.78rem;">Failed to load</div>';
  }
}

function renderAppSessions(sessions) {
  const el = document.getElementById('appSessionList');
  if (!sessions.length) {
    el.innerHTML = '<div style="color:var(--text-muted);font-size:0.78rem;text-align:center;padding:1rem;">No sessions yet</div>';
    return;
  }
  el.innerHTML = sessions.slice(0, 5).map(s => `
    <div class="phone-session-item${s.id === selectedSessionId ? ' selected' : ''}" onclick="selectSession(${s.id}, '${escHtml(s.session_name)}')">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
        <div>
          <div style="font-size:0.85rem;font-weight:600;">${escHtml(s.session_name)}</div>
          <div style="font-size:0.72rem;color:var(--text-muted);">${s.interviewer}</div>
        </div>
        <span class="badge badge-${statusClass(s.status)}" style="font-size:0.62rem;">${s.status}</span>
      </div>
    </div>
  `).join('');
}

function escHtml(str) { return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function statusClass(s) { return s.toLowerCase().replace(' ', '-'); }

function selectSession(id, name) {
  selectedSessionId = id;
  document.getElementById('activeSessionName').textContent = name;
  document.getElementById('recordingArea').style.display = 'flex';
  document.getElementById('recordingArea').style.flexDirection = 'column';
  document.getElementById('uploadResult').style.display = 'none';
  document.getElementById('uploadProgress').style.display = 'none';
  loadAppSessions(); // refresh highlight
}

// ─── New Session (App) ─────────────────────────────────────────────────
function showNewSessionModal() {
  const d = new Date(Date.now() + 30 * 60000);
  d.setSeconds(0);
  document.getElementById('appSessionTime').value = d.toISOString().slice(0, 16);
  document.getElementById('appNewSessionModal').style.display = 'flex';
}
function closeAppModal() {
  document.getElementById('appNewSessionModal').style.display = 'none';
}
async function createAppSession() {
  const name = document.getElementById('appSessionName').value.trim();
  const interviewer = document.getElementById('appInterviewer').value.trim();
  const time = document.getElementById('appSessionTime').value;
  if (!name || !interviewer) return alert('Please fill in all fields');

  const res = await fetch('/sessions/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({session_name: name, interviewer, time, notes: ''})
  });
  const data = await res.json();
  if (data.success) {
    closeAppModal();
    document.getElementById('appSessionName').value = '';
    document.getElementById('appInterviewer').value = '';
    selectSession(data.session.id, data.session.session_name);
    loadAppSessions();
  }
}

// ─── Recording ────────────────────────────────────────────────────────
async function toggleRecording() {
  if (!selectedSessionId) {
    alert('Please select a session first');
    return;
  }
  if (!isRecording) {
    await startRecording();
  } else {
    stopRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    
    // Setup audio context for waveform
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);

    // Setup recorder
    const mimeType = getSupportedMimeType();
    mediaRecorder = new MediaRecorder(stream, {mimeType});
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      cancelAnimationFrame(waveformAnimFrame);
      await uploadRecording();
    };

    mediaRecorder.start(1000); // collect every 1s
    isRecording = true;

    // Update UI
    const btn = document.getElementById('recordBtn');
    btn.className = 'record-btn recording';
    btn.textContent = '⏹️';
    document.getElementById('recStatus').textContent = 'Recording...';

    // Start timer
    elapsedSeconds = 0;
    timerInterval = setInterval(() => {
      elapsedSeconds++;
      const m = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
      const s = (elapsedSeconds % 60).toString().padStart(2, '0');
      document.getElementById('recTimer').textContent = `${m}:${s}`;
    }, 1000);

    // Start waveform
    drawWaveform();

    // Update session status
    await fetch(`/sessions/${selectedSessionId}/status`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status: 'Recording'})
    });

  } catch (e) {
    alert('Microphone access denied: ' + e.message);
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    clearInterval(timerInterval);
    isRecording = false;
    mediaRecorder.stop();

    const btn = document.getElementById('recordBtn');
    btn.className = 'record-btn idle';
    btn.textContent = '🎙️';
    document.getElementById('recStatus').textContent = 'Uploading...';
  }
}

async function uploadRecording() {
  document.getElementById('uploadProgress').style.display = 'block';
  animateProgress();

  const blob = new Blob(audioChunks, {type: getSupportedMimeType()});
  const formData = new FormData();
  formData.append('audio', blob, 'recording.webm');
  formData.append('session_id', selectedSessionId);

  try {
    const res = await fetch('/record/upload', {method: 'POST', body: formData});
    const data = await res.json();

    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('recStatus').textContent = 'Processing...';

    if (data.success) {
      currentRecordingId = data.recording_id;
      document.getElementById('uploadResult').style.display = 'block';
      document.getElementById('recordingIdDisplay').textContent = `Recording ID: ${data.recording_id} · Processing in background`;
      document.getElementById('recStatus').textContent = 'Uploaded! Processing...';
      loadAppSessions();
    }
  } catch (e) {
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('recStatus').textContent = 'Upload failed';
    console.error(e);
  }
}

function animateProgress() {
  let pct = 10;
  const bar = document.getElementById('progressBar');
  const interval = setInterval(() => {
    pct = Math.min(pct + Math.random() * 8, 90);
    bar.style.width = pct + '%';
    if (pct >= 90) clearInterval(interval);
  }, 300);
}

// ─── Waveform ──────────────────────────────────────────────────────────
function drawWaveform() {
  const canvas = document.getElementById('waveformCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const bufLen = analyser ? analyser.frequencyBinCount : 128;
  const dataArray = new Uint8Array(bufLen);

  function draw() {
    waveformAnimFrame = requestAnimationFrame(draw);
    if (analyser) analyser.getByteTimeDomainData(dataArray);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 2;
    ctx.strokeStyle = '#00e5cc';
    ctx.shadowBlur = 8;
    ctx.shadowColor = '#00e5cc';
    ctx.beginPath();

    const sliceWidth = canvas.width / bufLen;
    let x = 0;
    for (let i = 0; i < bufLen; i++) {
      const v = analyser ? (dataArray[i] / 128.0) : (0.5 + 0.1 * Math.sin(Date.now() / 200 + i * 0.3));
      const y = v * canvas.height / 2;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      x += sliceWidth;
    }
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
  }
  draw();
}

// ─── Helpers ──────────────────────────────────────────────────────────
function getSupportedMimeType() {
  const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
  for (const t of types) {
    if (MediaRecorder.isTypeSupported(t)) return t;
  }
  return '';
}

// Draw idle waveform on load
window.addEventListener('load', () => {
  const canvas = document.getElementById('waveformCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(0,229,204,0.3)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
  }
});
