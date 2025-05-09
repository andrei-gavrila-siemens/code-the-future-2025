import threading
import speech_recognition as sr

def listen_background(callback):
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=1)

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        
    def listen_loop():
        while True:
            with mic as source:
                print("Ascult activ...")
                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=7)
                    text = recognizer.recognize_google(audio, language="ro-RO").strip().lower()
                    if text:
                        callback(text)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"[Eroare]: {e}")
                    
    threading.Thread(target=listen_loop, daemon=True).start()

def print_text(text):
    print(f"Am auzit: {text}")

listen_background(print_text)

while True:
    pass
