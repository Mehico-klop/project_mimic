import json
import serial
import time
import os

SERIAL_PORT = '/dev/ttyUSB0'  # Проверь ls /dev/tty*
BAUDRATE = 115200
MISSION_FILE = 'mission.json'  # Положи рядом

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Дать ESP32 загрузиться

def send_mission():
    if not os.path.exists(MISSION_FILE):
        print("Файл миссии не найден!")
        return
    
    with open(MISSION_FILE) as f:
        data = json.load(f)
    
    for step in data['mission']:
        cmd = f"DEPTH:{step['depth']} YAW:{step['yaw']} TIME:{step['hold_time']}\n"
        ser.write(cmd.encode())
        print(f"Отправлено: {cmd.strip()}")
        # Ждём подтверждения от ESP32 (опционально)
        response = ser.readline().decode().strip()
        print(f"Ответ ESP: {response}")
        time.sleep(1)  # Паузы между командами

if __name__ == '__main__':
    print("Мост Jetson готов. Отправка миссии...")
    send_mission()
    ser.close()