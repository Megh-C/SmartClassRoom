#include <SoftwareSerial.h>
#include <Servo.h>

SoftwareSerial espSerial(2, 3);
Servo cleanerServo;

// -------- CLASSROOM LEDs --------
int room1 = 8;
int room2 = 7;


// -------- BUTTON + SERVO --------
int buttonPin = 4;
int servoPin = 9;

// -------- ULTRASONIC --------
int trigPin = 5;

int echoPins[4] = {6, 10, 11, 12};
int ledPins[4]  = {A0, A1, A2, A3};

// -------- VARIABLES --------
long lastDistances[4] = {0,0,0,0};
unsigned long stableStart[4] = {0,0,0,0};
unsigned long lastSeen[4] = {0,0,0,0};

bool isActive[4] = {false, false, false, false};

// -------- THRESHOLDS --------
int thresholdMin = 20;
int thresholdMax = 120;

unsigned long stableTime = 2000;   // 2 sec
unsigned long timeout = 10000;     // 10 sec

// -------- SETUP --------
void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);

  pinMode(room1, OUTPUT);
  pinMode(room2, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(trigPin, OUTPUT);

  for (int i = 0; i < 4; i++) {
    pinMode(echoPins[i], INPUT);
    pinMode(ledPins[i], OUTPUT);
  }
}

// -------- DISTANCE --------
long getDistance(int echoPin) {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 20000);
  long distance = duration * 0.034 / 2;

  return distance;
}

// -------- SERVO --------
void cleanBoard() {
  cleanerServo.attach(servoPin);
  cleanerServo.write(90);

  for (int i = 0; i < 3; i++) {
    cleanerServo.write(0);
    delay(700);
    cleanerServo.write(90);
    delay(700);
  }

  cleanerServo.detach();
}

// -------- LOOP --------
void loop() {

  // -------- BUTTON --------
  if (digitalRead(buttonPin) == LOW) {
    cleanBoard();
    while (digitalRead(buttonPin) == LOW);
    delay(200);
  }

  // -------- ESP --------
  if (espSerial.available()) {

    String cmd = espSerial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "SJT-401") digitalWrite(room1, HIGH);
    if (cmd == "SJT-402") digitalWrite(room2, HIGH);
    if (cmd == "SJT-401_OFF") digitalWrite(room1, LOW);
    if (cmd == "SJT-402_OFF") digitalWrite(room2, LOW);
  }

  unsigned long now = millis();

  // -------- SENSOR PROCESSING --------
  for (int i = 0; i < 4; i++) {

    long dist = getDistance(echoPins[i]);

    if (dist == 0) continue;

    if (dist > thresholdMin && dist < thresholdMax) {

      if (abs(dist - lastDistances[i]) < 5) {

        if (stableStart[i] == 0) {
          stableStart[i] = now;
        }

        // 🔥 STABLE → TURN ON
        if (now - stableStart[i] > stableTime) {
          isActive[i] = true;
          lastSeen[i] = now;
        }

      } else {
        stableStart[i] = 0;
      }

      lastDistances[i] = dist;
    }

    delay(70);
  }

  // -------- OUTPUT --------
  for (int i = 0; i < 4; i++) {


    if (isActive[i] && (now - lastSeen[i] > timeout)) {
      isActive[i] = false;
    }

    digitalWrite(ledPins[i], isActive[i] ? HIGH : LOW);
  }

  delay(100);
}