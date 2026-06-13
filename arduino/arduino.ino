#include <MFRC522.h>
#include <SPI.h>
#include <Servo.h>

// Pin definitions
const int fanPin = 5;
const int ampulPin = 6;
const int lockServoPin = 4;
const int openDoorServoPin = 3;
const int RST_PIN = 9;
const int SS_PIN = 10;
const int trigPin = 7;
const int echoPin = 8;
const int digitalPin = 1;
const int gasSensorPin = A0;
const int fan2Pin = A1;
const int buzzerPin = 2;

// Gas thresholds
const int gasThreshold = 400;
const int turnOffThreshold = 350;

MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo lockServo;
Servo openDoorServo;

// System flags
bool manualFanRequest = false;
bool gasFanRequest = false;
bool safeMode = false;
bool fireState = false;

// Door sequence state machine
enum DoorSeqState {
  DOOR_IDLE,
  DOOR_UNLOCK,
  DOOR_LIGHT,
  DOOR_OPEN,
  DOOR_WAIT,
  DOOR_CLOSE,
  DOOR_LOCK
};
DoorSeqState doorSeqState = DOOR_IDLE;
unsigned long doorSeqStart = 0;

// Different sequence types
enum SeqType {
  SEQ_RFID,
  SEQ_GAS_OPEN,
  SEQ_GAS_CLOSE
};
SeqType currentSeq = SEQ_RFID;

// Gas door tracking
bool gasDoorOpened = false;

// Gas sensor timing
unsigned long lastGasRead = 0;
const unsigned long GAS_INTERVAL = 200;
bool gasAlarmTriggered = false;

// Distance sensor
unsigned long lastDistTime = 0;
const unsigned long DIST_INTERVAL = 100;

// Buzzer
bool buzzerActive = false;
unsigned long buzzerStart = 0;
int buzzerCount = 0;
int buzzerStep = 0;
const unsigned long BUZZ_PHASE = 200;

// ------------------------------------------------------------------
// Buzzer
// ------------------------------------------------------------------
void startBuzzer(int beeps) {
  if (buzzerActive) return;
  buzzerActive = true;
  buzzerCount = beeps;
  buzzerStep = 0;
  buzzerStart = millis();
  tone(buzzerPin, 1000);
}

void updateBuzzer() {
  if (!buzzerActive) return;
  unsigned long now = millis();
  unsigned long elapsed = now - buzzerStart;
  int totalPhases = buzzerCount * 2;
  if (elapsed >= totalPhases * BUZZ_PHASE) {
    noTone(buzzerPin);
    buzzerActive = false;
    return;
  }
  int phase = elapsed / BUZZ_PHASE;
  if (phase != buzzerStep) {
    buzzerStep = phase;
    if (phase % 2 == 0) tone(buzzerPin, 1000);
    else noTone(buzzerPin);
  }
}

// ------------------------------------------------------------------
// Fan control
// ------------------------------------------------------------------
void updateFan() {
  bool on = manualFanRequest || gasFanRequest;
  analogWrite(fanPin, on ? 255 : 0);
  analogWrite(fan2Pin, on ? 255 : 0);
  if (on && !manualFanRequest) Serial.println("fan on (gas)");
  else if (!on && manualFanRequest) Serial.println("fan off (gas cleared)");
}

void fanOn() {
  manualFanRequest = true;
  updateFan();
  Serial.println("fan on (manual)");
}

void fanOff() {
  manualFanRequest = false;
  updateFan();
  Serial.println("fan off (manual)");
}

// ------------------------------------------------------------------
// Actuators
// ------------------------------------------------------------------
void unlockDoor() {
  lockServo.write(90);
  Serial.println("door unlocked");
}
void lockDoor() {
  lockServo.write(0);
  Serial.println("door locked");
}
void openLight() {
  digitalWrite(ampulPin, HIGH);
  Serial.println("lights on");
}
void closeLight() {
  digitalWrite(ampulPin, LOW);
  Serial.println("lights off");
}
void doorOpen() {
  openDoorServo.write(50);
  Serial.println("door open");
}
void doorClose() {
  openDoorServo.write(180);
  Serial.println("door close");
}

// ------------------------------------------------------------------
// Door sequence (non-blocking)
// ------------------------------------------------------------------
void startDoorSequence(SeqType type) {
  if (doorSeqState != DOOR_IDLE) return;
  currentSeq = type;
  if (type == SEQ_GAS_CLOSE) {
    doorSeqState = DOOR_CLOSE;  // start closing directly
  } else {
    doorSeqState = DOOR_UNLOCK;
  }
  doorSeqStart = millis();
}

void updateDoorSequence() {
  if (doorSeqState == DOOR_IDLE) return;
  unsigned long now = millis();

  switch (doorSeqState) {
    case DOOR_UNLOCK:
      unlockDoor();
      doorSeqState = (currentSeq == SEQ_RFID) ? DOOR_LIGHT : DOOR_OPEN;
      doorSeqStart = now;
      break;

    case DOOR_LIGHT:
      if (now - doorSeqStart >= 100) {
        openLight();
        doorSeqState = DOOR_OPEN;
        doorSeqStart = now;
      }
      break;

    case DOOR_OPEN:
      if (now - doorSeqStart >= (currentSeq == SEQ_RFID ? 1000 : 500)) {
        if (currentSeq == SEQ_RFID) closeLight();
        doorOpen();
        doorSeqState = DOOR_WAIT;
        doorSeqStart = now;
      }
      break;

    case DOOR_WAIT:
      {
        unsigned long wait = (currentSeq == SEQ_RFID) ? 5000 : 3000;
        if (now - doorSeqStart >= wait) {
          doorClose();
          doorSeqState = DOOR_CLOSE;
          doorSeqStart = now;
        }
      }
      break;

    case DOOR_CLOSE:
      if (now - doorSeqStart >= 2000) {
        doorSeqState = DOOR_LOCK;
        doorSeqStart = now;
      }
      break;

    case DOOR_LOCK:
      if (now - doorSeqStart >= 500) {
        lockDoor();
        doorSeqState = DOOR_IDLE;
      }
      break;
  }
}

// ------------------------------------------------------------------
// Gas sensor with door open/close
// ------------------------------------------------------------------
void updateGasSensor() {
  if (!fireState) return;

  unsigned long now = millis();
  if (now - lastGasRead < GAS_INTERVAL) return;
  lastGasRead = now;

  int gas = analogRead(gasSensorPin);

  if (gas > gasThreshold) {
    Serial.println("fire_on");

    // Gas detected
    if (!gasFanRequest) {
      gasFanRequest = true;
      updateFan();
    }
    if (!gasAlarmTriggered) {
      gasAlarmTriggered = true;
      startBuzzer(3);
    }
    // Open door if not already open or in a sequence
    if (!gasDoorOpened && doorSeqState == DOOR_IDLE) {
      gasDoorOpened = true;
      startDoorSequence(SEQ_GAS_OPEN);
      delay(1000);
    }
  } else if (gas <= turnOffThreshold) {
    // Gas cleared
    if (gasFanRequest) {
      gasFanRequest = false;
      updateFan();
    }
    gasAlarmTriggered = false;
    // Close door if it was opened by gas and door is idle
    if (gasDoorOpened && doorSeqState == DOOR_IDLE) {
      gasDoorOpened = false;
      startDoorSequence(SEQ_GAS_CLOSE);
    }
  }
}

// ------------------------------------------------------------------
// Distance meter
// ------------------------------------------------------------------
void updateDistanceMeter() {
  if (!safeMode) return;
  unsigned long now = millis();
  if (now - lastDistTime < DIST_INTERVAL) return;
  lastDistTime = now;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 30000);
  if (duration == 0) return;
  int distance = duration * 0.0343 / 2;
  if (distance < 33) {
    Serial.println("motion_detected");
    startBuzzer(2);
  }
}

// ------------------------------------------------------------------
// RFID card reader
// ------------------------------------------------------------------
void updateCardReader() {
  if (doorSeqState != DOOR_IDLE) return;
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  const byte allowed[3][4] = {
    { 0, 0, 0, 0 }, // buraya kendi ardunio nuzun değerlerini girmelisiniz
    { 0, 0, 0, 0 },// suan kodun hata vermesi gayet normal
    { 0, 0, 0, 0}
  };
  bool granted = false;
  for (int i = 0; i < 3; i++) {
    if (memcmp(mfrc522.uid.uidByte, allowed[i], 4) == 0) {
      granted = true;
      break;
    }
  }

  Serial.print("Card UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) Serial.print("0");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  if (granted) {
    Serial.println("Access granted");
    startDoorSequence(SEQ_RFID);
  } else {
    Serial.println("Access DENIED");
    startBuzzer(1);
  }
  mfrc522.PICC_HaltA();
}

// ------------------------------------------------------------------
// Serial commands
// ------------------------------------------------------------------
void handleSerial() {
  if (Serial.available() == 0) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();

  if (cmd == "fan_on") fanOn();
  else if (cmd == "fan_off") fanOff();
  else if (cmd == "light_on") openLight();
  else if (cmd == "light_off") closeLight();
  else if (cmd == "open_door") {
    doorOpen();
    doorSeqState = DOOR_IDLE;
  } else if (cmd == "close_door") {
    doorClose();
    doorSeqState = DOOR_IDLE;
  } else if (cmd == "door_open") {
    unlockDoor();
    doorSeqState = DOOR_IDLE;
  } else if (cmd == "door_locked") {
    lockDoor();
    doorSeqState = DOOR_IDLE;
  } else if (cmd == "securitymode_on") {
    safeMode = true;
  } else if (cmd == "securitymode_off") safeMode = false;
  else if (cmd == "firesystem_on") {
    fireState = true;
  } else if (cmd == "firesystem_off") fireState = false;
}

// ------------------------------------------------------------------
// Setup
// ------------------------------------------------------------------
void setup() {
  Serial.begin(9600);
  pinMode(fanPin, OUTPUT);
  pinMode(ampulPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(gasSensorPin, INPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(fan2Pin, OUTPUT);
  pinMode(digitalPin, INPUT);

  digitalWrite(fanPin, LOW);
  digitalWrite(ampulPin, LOW);
  digitalWrite(buzzerPin, LOW);

  lockServo.attach(lockServoPin);
  openDoorServo.attach(openDoorServoPin);
  lockServo.write(90);
  openDoorServo.write(180);

  SPI.begin();
  mfrc522.PCD_Init();
  delay(1000);
}

// ------------------------------------------------------------------
// Main loop
// ------------------------------------------------------------------
void loop() {
  handleSerial();
  updateGasSensor();
  updateDistanceMeter();
  updateCardReader();
  updateDoorSequence();
  updateBuzzer();
}