from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import paho.mqtt.client as mqtt

app = Flask(__name__)
socketio = SocketIO(app)
MISSION_FILE = 'mission.json'

MQTT_BROKER = "localhost"  # Ваш брокер
MQTT_PORT = 1883
TELEMETRY_TOPIC = "auv/telemetry"
CONTROL_TOPIC = "auv/control"

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

def on_telemetry(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    socketio.emit('telemetry', data)  # Отправка в WebSocket

mqtt_client.subscribe(TELEMETRY_TOPIC)
mqtt_client.on_message = on_telemetry

@app.route('/')
def index():
    return render_template('index.html')  # Создайте index.html с <script src="/script.js"></script> и div id="telemetry"

@app.route('/save_mission', methods=['POST'])
def save_mission():
    data = request.json
    mission = {"mission": []}
    for i in range(1, 11):
        step = {
            "step": i,
            "depth": float(data.get(f'depth_{i}', 0)),
            "yaw": float(data.get(f'yaw_{i}', 0)),
            "hold_time": int(data.get(f'time_{i}', 30))
        }
        mission["mission"].append(step)
    
    with open(MISSION_FILE, 'w') as f:
        json.dump(mission, f, indent=2)
    
    return jsonify({"status": "success"})

@app.route('/api/play', methods=['POST'])
def play():
    mqtt_client.publish(CONTROL_TOPIC, "start")
    return jsonify({"status": "started"})

@app.route('/api/stop', methods=['POST'])
def stop():
    mqtt_client.publish(CONTROL_TOPIC, "stop")
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)