#include <ArduinoJson.h>
#include <PID_v1.h>
#include <Wire.h>
#include <MS5837.h>  // Библиотека для MS5837 (BlueRobotics)
#include <Adafruit_BME280.h>  // Для BME280
#include <Servo.h>  // Для ESC моторов

// Распиновка из вашего описания
#define I2C_SDA 21
#define I2C_SCL 22
#define SERIAL_BAUD 9600
#define RXD2 27
#define TXD2 26
const int escPins[] = {32, 33, 5, 19, 18};
#define ADC_CURRENT_PIN 2
#define ADC_VOLTAGE_PIN 4

// Сенсоры
MS5837 depthSensor;
Adafruit_BME280 pressureSensor;
HardwareSerial SerialInclino(2);  // Serial2 для инклинометра
Servo esc[5];  // Моторы

// PID для глубины
double setpoint_depth = 0, input_depth = 0, output_depth = 0;
PID pid_depth(&input_depth, &output_depth, &setpoint_depth, 2.0, 0.5, 0.1, DIRECT);  // Тюнить

// PID для yaw
double setpoint_yaw = 0, input_yaw = 0, output_yaw = 0;
PID pid_yaw(&input_yaw, &output_yaw, &setpoint_yaw, 2.0, 0.5, 0.1, DIRECT);

bool mission_active = false;  // Флаг для прерывания миссии

void setup() {
  Serial.begin(115200);  // Для Jetson
  SerialInclino.begin(SERIAL_BAUD, SERIAL_8N1, RXD2, TXD2);  // Инклинометр
  
  Wire.begin(I2C_SDA, I2C_SCL);
  
  // Инициализация датчиков
  if (!depthSensor.init()) {
    Serial.println("MS5837 init failed!");
  }
  depthSensor.setModel(MS5837_30BA);
  depthSensor.setFluidDensity(997);  // Для пресной воды, тюнить для морской
  
  if (!pressureSensor.begin(0x77)) {
    Serial.println("BME280 init failed!");
  }
  
  // Моторы
  for (int i = 0; i < 5; i++) {
    esc[i].attach(escPins[i]);
    esc[i].writeMicroseconds(1500);  // Нейтраль
  }
  
  pid_depth.SetMode(AUTOMATIC);
  pid_yaw.SetMode(AUTOMATIC);
  pid_depth.SetOutputLimits(-400, 400);  // Для ESC, тюнить
  pid_yaw.SetOutputLimits(-400, 400);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    if (cmd.startsWith("DEPTH:")) {
      float depth, yaw;
      int hold_time;
      sscanf(cmd.c_str(), "DEPTH:%f YAW:%f TIME:%d", &depth, &yaw, &hold_time);
      
      setpoint_depth = depth;
      setpoint_yaw = yaw;
      mission_active = true;
      
      unsigned long start = millis();
      while (millis() - start < hold_time * 1000 && mission_active) {
        // Чтение датчиков
        input_depth = get_depth();
        input_yaw = get_yaw();
        
        pid_depth.Compute();
        pid_yaw.Compute();
        
        // Управление моторами
        control_thrusters_vertical(output_depth);
        control_thrusters_yaw(output_yaw);
        
        // Отправка телеметрии в JSON
        send_telemetry();
        
        delay(50);  // 20 Hz
      }
      stop_thrusters();  // Остановка после шага
      Serial.println("STEP_DONE");
    } else if (cmd == "STOP\n") {
      mission_active = false;
      stop_thrusters();
      Serial.println("MISSION_STOPPED");
    }
  }
}

// Функции чтения
float get_depth() {
  depthSensor.read();
  return depthSensor.depth();
}

float get_pressure() {
  return pressureSensor.readPressure() / 100.0;  // hPa
}

float get_yaw() {  // Из инклинометра, предположим формат "YAW:123.45\n"
  if (SerialInclino.available()) {
    String data = SerialInclino.readStringUntil('\n');
    if (data.startsWith("YAW:")) {
      return data.substring(4).toFloat();
    }
  }
  return input_yaw;  // Вернуть предыдущее если нет
}

float get_current() {
  return analogRead(ADC_CURRENT_PIN) * (3.3 / 4095.0) * /* коэффициент сенсора тока */;
  // Тюнить множитель по вашему сенсору тока (e.g., ACS712)
}

float get_voltage() {
  return analogRead(ADC_VOLTAGE_PIN) * (3.3 / 4095.0) * /* делитель напряжения */;
  // Тюнить по вашему делителю (e.g., 11 для 3.3V ADC на 36V бат)
}

// Отправка телеметрии
void send_telemetry() {
  StaticJsonDocument<256> doc;
  doc["depth"] = get_depth();
  doc["pressure"] = get_pressure();
  doc["yaw"] = get_yaw();
  doc["current"] = get_current();
  doc["voltage"] = get_voltage();
  serializeJson(doc, Serial);
  Serial.println();
}

// Управление
void control_thrusters_vertical(double pwm) {
  // Пример: esc[0] и esc[1] - вертикальные
  esc[0].writeMicroseconds(1500 + pwm);
  esc[1].writeMicroseconds(1500 + pwm);
}

void control_thrusters_yaw(double pwm) {
  // Пример: esc[2] левый, esc[3] правый
  esc[2].writeMicroseconds(1500 + pwm);
  esc[3].writeMicroseconds(1500 - pwm);
}

void stop_thrusters() {
  for (int i = 0; i < 5; i++) {
    esc[i].writeMicroseconds(1500);
  }
}