from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
MISSION_FILE = 'mission.json'

# Главная страница с формой для 10 шагов
@app.route('/')
def index():
    return render_template('index.html')

# Сохранение миссии
@app.route('/save_mission', methods=['POST'])
def save_mission():
    data = request.json
    mission = {"mission": []}
    for i in range(1, 11):
        step = {
            "step": i,
            "depth": float(data[f'depth_{i}']),
            "yaw": float(data[f'yaw_{i}']),
            "hold_time": int(data[f'time_{i}'])
        }
        mission["mission"].append(step)
    
    with open(MISSION_FILE, 'w') as f:
        json.dump(mission, f, indent=2)
    
    return jsonify({"status": "success", "file": MISSION_FILE})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)