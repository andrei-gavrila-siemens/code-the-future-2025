document.addEventListener('DOMContentLoaded', () => {
  const KEYWORDS = ['paracetamol', 'aspirină', 'parasinus', 'septogal'];
  const btn        = document.getElementById('start-btn');
  const recognized = document.getElementById('recognized');
  const status     = document.getElementById('status');
  if (!btn || !recognized || !status) return console.error('UI missing');

  // Conectare WebSocket (folosind același host și port)
  const socket = io(window.location.origin, {
    transports: ['websocket'],
    secure: true
  });

  socket.on('connect', () => {
    status.textContent = 'Status: Conexiune WS OK';
  });
  socket.on('connect_error', err => {
    status.textContent = `❌ Eroare conexiune WS: ${err.message}`;
  });
  socket.on('disconnect', reason => {
    status.textContent = `⚠️ WS deconectat: ${reason}`;
  });
  socket.on('status', data => {
    status.textContent = `Status: ${data.message}`;
  });
  socket.on('result', data => {
    status.textContent = data.status === 'ok'
      ? `✓ ${data.message}`
      : `❌ ${data.message}`;
  });

  // SpeechRecognition setup
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert('Browserul nu suportă Web Speech API');
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = 'ro-RO';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  // Beep helper
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  function playBeep(freq=440, dur=200){
    const osc  = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur/1000);
    osc.start(); osc.stop(audioCtx.currentTime + dur/1000);
  }

  // Mapare erori SpeechRecognition
  const errorMessages = {
    'no-speech': 'Nu s-a detectat vorbire, încearcă din nou.',
    'audio-capture': 'Eroare microfon, verifica setările audio.',
    'not-allowed': 'Acces împiedicat: permite folosirea microfonului.',
    'service-not-allowed': 'Serviciul de recunoaștere nu este permis.',
    'network': 'Eroare de rețea, verifică conexiunea internet.',
    'bad-grammar': 'Eroare de gramatică internă.',
    'language-not-supported': 'Limba nu este suportată.'
  };

  recognition.addEventListener('start', () => {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    playBeep(800, 200);
    recognized.innerHTML = 'Medicament: <span class="font-medium">—</span>';
    status.textContent = 'Status: Ascult…';
  });
  recognition.addEventListener('end', () => playBeep(400, 200));
  recognition.addEventListener('error', e => {
    const msg = errorMessages[e.error] || `Eroare neașteptată (${e.error})`;
    status.textContent = `❌ ${msg}`;
    console.error('SpeechRecognition Error:', e.error);
    playBeep(300, 200);
  });

  btn.addEventListener('click', () => recognition.start());

  recognition.addEventListener('result', e => {
    const transcript = e.results[0][0].transcript.trim();
    recognized.innerHTML = `<strong>${transcript}</strong>`;
    const cmd = KEYWORDS.find(k => transcript.toLowerCase().includes(k));
    if (!cmd) {
      status.textContent = '❌ Medicament necunoscut';
      return;
    }
    status.textContent = 'Status: Trimit…';
    socket.emit('command', { cmd });
  });
});
