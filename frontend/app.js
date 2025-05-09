document.addEventListener('DOMContentLoaded', () => {
    // 1. Comenzi permise
    const KEYWORDS = ['paracetamol', 'aspirină', 'parasinus', 'septogal'];
  
    // 2. Elementele UI
    const btn        = document.getElementById('start-btn');
    const recognized = document.getElementById('recognized');
    const status     = document.getElementById('status');
    if (!btn || !recognized || !status) {
      console.error('Elemente UI lipsă:', { btn, recognized, status });
      return;
    }
  
    // 3. Conexiune Socket.IO
    const socket = io('http://172.31.5.254:5000');
  
    socket.on('connect', () => {
      console.log('✅ WebSocket conectat:', socket.id);
      status.textContent = 'Status: Conexiune WebSocket stabilită';
    });
  
    socket.on('status', data => {
      console.log('🔔 WS status:', data.message);
      status.textContent = `Status: ${data.message}`;
    });
  
    socket.on('result', data => {
      console.log('📩 WS result:', data);
      if (data.status === 'ok') {
        status.textContent = `✓ ${data.message}`;
      } else {
        status.textContent = `❌ ${data.message}`;
      }
    });
  
    // 4. Inițializare Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Browserul nu suportă Web Speech API');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'ro-RO';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
  
    // 5. Beep-uri cu Web Audio API
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq = 440, dur = 200, vol = 5) {
      const osc  = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(vol, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(
        0.001,
        audioCtx.currentTime + dur/1000
      );
      osc.start(audioCtx.currentTime);
      osc.stop(audioCtx.currentTime + dur/1000);
    }
  
    // 6. Evenimente SpeechRecognition
    recognition.addEventListener('start', () => {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      playBeep(800, 200, 5);
      recognized.innerHTML = 'Medicament recunoscut: <span class="font-medium">—</span>';
      status.textContent = 'Status: Ascult…';
      console.log('🎤 SpeechRecognition start');
    });
  
    recognition.addEventListener('speechstart', () => console.log('🗣️ speechstart'));
    recognition.addEventListener('speechend',   () => console.log('✋ speechend'));
  
    recognition.addEventListener('error', e => {
      console.error('❌ SR Error:', e.error);
      status.textContent = `Status: Eroare (${e.error})`;
      playBeep(300, 200, 5);
    });
  
    recognition.addEventListener('end', () => {
      console.log('🏁 SpeechRecognition end');
      playBeep(400, 200, 5);
    });
  
    // 7. Start recognition la click
    btn.addEventListener('click', () => recognition.start());
  
    // 8. Procesare rezultat și trimitere prin WebSocket
    recognition.addEventListener('result', e => {
      const transcript = e.results[0][0].transcript.trim();
      console.log('📝 Transcript:', transcript);
  
      recognized.innerHTML = `Medicament recunoscut: <strong>${transcript}</strong>`;
      status.textContent   = 'Status: Trimit WS…';
  
      // verificăm keyword
      const cmd = KEYWORDS.find(k => transcript.toLowerCase().includes(k));
      if (!cmd) {
        status.textContent = '❌ Medicament necunoscut';
        return;
      }
      // trimitem comanda
      socket.emit('command', { cmd });
    });
  });
  