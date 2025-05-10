from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import logging
import CRNN
import CameraFoto as cf
from PIL import Image
import inputARDU as ia

# — Configurare Flask + SocketIO —
app = Flask(__name__, static_folder='../frontend', template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins='*')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')



# — Servește frontend-ul —
@app.route('/')
def index():
    return render_template('index.html')

# — WebSocket handlers —
@socketio.on('connect')
def handle_connect():
    logging.info(f"Client conectat: {request.sid}")
    emit('status', {'message': 'Conexiune WebSocket OK'})

@socketio.on('command')
def handle_command(data):
    cmd = data.get('cmd', '').strip().lower()
    logging.info(f"Comandă primită: {cmd}")
    cf.take_photo('photo.jpg', 2000, 640, 480)
    cf.rotate('photo.jpg')
    img = Image.open('photo.jpg')
    text = CRNN.imgToText('photo.jpg', langs=['ro', 'en'])
    print(text)
    commanda = CRNN.getIndice(text, cmd)
    print(f"Comanda: {commanda}")
    ia.trimiteComanda(str(commanda)
    )

# — Stub-uri de demo —
def search_medicine_with_camera(med_name: str) -> bool:
    logging.info(f"[Camera] Căutare medicament: {med_name}")
    return True

def initiate_robot_movement(med_name: str) -> bool:
    logging.info(f"[Robot] Mișcare robot pentru: {commanda}")
    return True

    if not search_medicine_with_camera(cmd):
        return emit('result', {
            'status': 'not_found',
            'message': f"Medicament ‘{cmd}’ NU a fost găsit"
        })

    if not initiate_robot_movement(cmd):
        return emit('result', {
            'status': 'error',
            'message': f"Med ‘{cmd}’ găsit, dar mișcare eșuată"
        })

    emit('result', {
        'status': 'ok',
        'message': f"Medicament ‘{cmd}’ găsit și robot în mișcare"
    })

# — Pornire HTTPS + SocketIO —
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        ssl_context=('../cert.pem', '../key.pem')
    )
