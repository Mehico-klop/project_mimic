import json
import time
from mqtt_client import send_command


def play_sequence(file_path):
    with open(file_path) as f:
        sequence = json.load(f)

    for step in sequence:
        pitch, roll, yaw, delay = step
        send_command(pitch, roll, yaw)
        time.sleep(delay / 1000.0)
