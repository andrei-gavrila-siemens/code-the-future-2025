from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

# --- Configurare Flask, CORS și Socket.IO ---
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# --- Stub-uri pentru camera și mișcare robot ---
def search_medicine_with_camera(med_name: str) -> bool:
    logging.info(f"[Camera] Căutare medicament '{med_name}'")
    return True

def initiate_robot_movement(med_name: str) -> bool:
    logging.info(f"[Robot] Inițiere mișcare pentru '{med_name}'")
    return True

# --- Handler la conectare WebSocket ---
@socketio.on('connect')
def on_connect(auth):
    logging.info(f"[SocketIO] Client conectat: {request.sid}")
    emit('status', {'message': 'Conexiune WebSocket stabilită'})

# --- Handler pentru comenzi primite prin WS ---
@socketio.on('command')
def on_command(data):
    med = data.get('cmd', '').strip().lower()
    logging.info(f"[API WS] Comandă primită: '{med}'")

    # 1) detectare cu camera
    if not search_medicine_with_camera(med):
        emit('result', {
            'status': 'not_found',
            'message': f"Medicament '{med}' NU a fost găsit"
        })
        return

    # 2) inițiere mișcare robot
    if not initiate_robot_movement(med):
        emit('result', {
            'status': 'error',
            'message': f"Medicament '{med}' găsit, dar mișcarea robotului a eșuat"
        })
        return

    # 3) succes
    emit('result', {
        'status': 'ok',
        'message': f"Medicament '{med}' găsit și robotul a pornit mișcarea"
    })

# --- Pornire server WS+HTTP ---
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
