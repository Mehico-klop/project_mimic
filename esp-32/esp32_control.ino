#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* mqtt_server = "192.168.1.100";

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<200> doc;
  deserializeJson(doc, payload, length);

  int pitch = doc["pitch"];
  int roll  = doc["roll"];
  int yaw   = doc["yaw"];

  moveAUV(pitch, roll, yaw);
}

void moveAUV(int pitch, int roll, int yaw) {
  // ТУТ ТВОЯ ЛОГИКА
  // преобразование углов в PWM
  Serial.printf("Pitch: %d Roll: %d Yaw: %d\n", pitch, roll, yaw);
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  while (!client.connected()) {
    client.connect("ESP32_AUV");
  }

  client.subscribe("auv/control");
}

void loop() {
  client.loop();
}
