import json
import serial
import time
import os
import threading
import paho.mqtt.client as mqtt  # pip install paho-mqtt

SERIAL_PORT = '/dev/ttyUSB0'  # Адаптируйте
BAUDRATE = 115200
MISSION_FILE = 'mission.json'  # Копируйте с PC вручную или добавьте скачивание
MQTT_BROKER = "192.168.1.237"  # Или IP PC/брокера
MQTT_PORT = 1883
TELEMETRY_TOPIC = "auv/telemetry"
CONTROL_TOPIC = "auv/control"

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

mission_active = False

def on_message(client, userdata, msg):
    global mission_active
    command = msg.payload.decode()
    if command == "start":
        mission_active = True
        threading.Thread(target=send_mission).start()
    elif command == "stop":
        mission_active = False
        ser.write("STOP\n".encode())
        print("Отправлен STOP")

client.subscribe(CONTROL_TOPIC)
client.on_message = on_message

def send_mission():
    global mission_active
    if not os.path.exists(MISSION_FILE):
        print("Файл миссии не найден!")
        return
    
    with open(MISSION_FILE) as f:
        data = json.load(f)
    
    for step in data['mission']:
        if not mission_active:
            break
        cmd = f"DEPTH:{step['depth']} YAW:{step['yaw']} TIME:{step['hold_time']}\n"
        ser.write(cmd.encode())
        print(f"Отправлено: {cmd.strip()}")
        response = ser.readline().decode().strip()
        print(f"Ответ ESP: {response}")
        time.sleep(1)  # Паuza
    
    mission_active = False
    print("Миссия завершена")

# Цикл чтения телеметрии
def read_telemetry():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            try:
                data = json.loads(line)
                client.publish(TELEMETRY_TOPIC, json.dumps(data))
            except:
                pass  # Игнор не-JSON (e.g., "OK")
        time.sleep(0.05)

threading.Thread(target=read_telemetry, daemon=True).start()

if __name__ == '__main__':
    print("Jetson готов. Ожидание команд по MQTT...")
    while True:
        time.sleep(1)  # Держим живым