import json
import paho.mqtt.client as mqtt

BROKER = "192.168.1.100"  # IP роутера / брокера
TOPIC = "auv/control"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)


def send_command(pitch, roll, yaw):
    msg = {
        "pitch": pitch,
        "roll": roll,
        "yaw": yaw
    }
    client.publish(TOPIC, json.dumps(msg))
