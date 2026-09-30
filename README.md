
Jarvis is my Desk Assistant made for helping me, both physically and mentally (means that he can talk about anything with me). He uses camera vision, speech recognition a local AI - Gemma3. My goal was to build my own little Jarvis, like Iron Man's. I couldn't finish it because it took much longer than I thought and sometimes I didn't even want to finish it because all the problem really sucked. I still hope that you can use this and maybe correct some of it.


Table of Contents

1. [Voice Control – Desa Listens and Responds](#1-voice-control--desa-listens-and-responds)
2. [Camera & Object Detection](#2-camera--object-detection)
3. [Connecting the AI with Camera Context](#3-connecting-the-ai-with-camera-context)
4. [Running Camera and AI at the Same Time](#4-running-camera-and-ai-at-the-same-time)
5. [Bringing It All Together with Threading](#5-bringing-it-all-together-with-threading)
6. [The Robotic Arm (Servos & Control)](#6-the-robotic-arm-servos--control)

---

## 1. Voice Control – Desa Listens and Responds

The first thing I built was voice output and voice recognition. Desa listens through the microphone, recognizes when its name is said, and then responds using a local AI (Ollama with Gemma3).

Installed for this:
- `pyttsx3` – for voice output
- `speech_recognition` + `pyaudio` – for voice recognition
- `ollama` – to chat locally with Gemma3

**`jarvis2.py`**

```python
import pyttsx3
import speech_recognition as sr
import ollama
from ollama import chat
import os

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
    "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

class JarvisBot:
    def __init__(self):
        self.jarvi = pyttsx3.init()
        self.recognizer = sr.Recognizer()

        # My own settings
        self.jarvi.setProperty('voice', 'com.apple.speech.synthesis.voice.sinji')
        self.jarvi.setProperty('rate', 230)
        self.recognizer.pause_threshold = 0.6
        self.recognizer.energy_threshold = 300
        self.name = "Jarvis"

    def listen_for_command(self, source):
        try:
            audio = self.recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=10
            )
            try:
                prompt = self.recognizer.recognize_google(audio)
                prompt = self.recognizer.recognize_google(audio, language="en-US")
                print(prompt)
                return prompt
            except sr.UnknownValueError:
                print("Could not understand audio")
                return ""
            except sr.RequestError as e:
                print("Error with speech recognition", e)
                return ""
        except Exception as e:
            print("Error listening for command:", e)
            return ""

    def speak(self, text):
        clean_text = remove_emojis(text)
        print(clean_text)
        self.jarvi.say(clean_text)
        self.jarvi.runAndWait()

    def run(self, camera_tracker):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Jarvis is ready")

            while True:
                text = self.listen_for_command(source)

                if not text:
                    continue
                if self.name.lower() not in text.lower():
                    continue

                command = text.lower().replace(self.name.lower(), "").strip()
                if not command:
                    self.speak("Yes?")
                    continue

                print("Command:", command)

                # Get the currently detected objects from the camera
                current_objects = camera_tracker.detected_objects
                objects_str = ", ".join(current_objects) if current_objects else "nothing detected"

                # Pass a system prompt so the AI knows what's in the frame
                system_context = f"You are Jarvis. Your camera currently sees: {objects_str}. Use this information when the user asks about it."

                try:
                    response = ollama.chat(
                        model='gemma3:1b',
                        messages=[
                            {'role': 'system', 'content': system_context},
                            {'role': 'user', 'content': command},
                        ],
                        options={
                            'temperature': 0.1
                        }
                    )

                    answer = response['message']['content']
                    self.speak(answer)

                except Exception as e:
                    print("Error processing command:", e)
                    self.speak("I am not sure what you mean. Please try again.")
```

The cool part: Desa gets the objects currently detected by the camera passed into the AI prompt as context, so I can ask what's currently on my desk.

---

## 2. Camera & Object Detection

Next came camera vision. I use OpenCV together with YOLOv8 Nano to detect objects in real time.

**`camera2.py`**

```python
import json
import cv2
from ultralytics import YOLO

class CameraTracker:
    def __init__(self, model_path="/Users/jamie.wiebe/Hack Club/yolov8n.pt"):
        self.model = YOLO(model_path)
        self.detected_objects = []
        self.is_running = False

    def start(self):
        cam = cv2.VideoCapture(0)
        self.is_running = True

        while self.is_running and cam.isOpened():
            ret, frame = cam.read()
            if not ret:
                break

            results = self.model(frame)
            class_ids = results[0].boxes.cls.tolist()
            self.detected_objects = list(set([self.model.names[int(cls)] for cls in class_ids]))

            annotated_frame = results[0].plot()
            cv2.imshow("Camera", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_running = False
                break
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    camera = CameraTracker()
    camera.start()
```

This is what took me the longest to figure out: I wanted to connect YOLOv8n with Gemma3 so the AI would know what's visible in the frame – that's exactly what's solved above in `jarvis2.py` via `detected_objects`.

---

## 3. Connecting the AI with Camera Context

This step actually already lives inside `jarvis2.py` (see above, `system_context`): as soon as I ask Desa something, the program sends the objects currently detected by the camera along to Gemma3, so the answer matches what's actually on my desk right now.

---

## 4. Running Camera and AI at the Same Time

A bigger problem: camera tracking and Jarvis needed to run at the same time. I first solved this with two separate processes using `subprocess`.

**`multiprocess.py`**

```python
import subprocess
import sys
import time

if __name__ == "__main__":
    print("Starting main.py...")
    camera_process = subprocess.Popen([sys.executable, "Camera.py"])
    ki_process = subprocess.Popen([sys.executable, "Jarvis.py"])
    print("Processes started. Waiting for them to finish...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Terminating processes...")
        camera_process.terminate()
        ki_process.terminate()
        print("Processes terminated. Exiting.")
```

This worked, but it was a bit clunky because both programs ran completely separately and sharing the object data between them wasn't straightforward.

---

## 5. Bringing It All Together with Threading

After that, I combined both into a single program and ran them at the same time using `threading`, so the camera and Jarvis could share the detected objects directly, without going through files or process boundaries.

**`haupt.py`**

```python
import threading
import time
from camera2 import CameraTracker
from jarvis2 import JarvisBot

tracker = CameraTracker()
jarvis = JarvisBot()

jarvis_thread = threading.Thread(target=jarvis.run, args=(tracker,), daemon=True)

jarvis_thread.start()
try:
    tracker.start()
except KeyboardInterrupt:
    print("Stopping threads")
```

This was the step that took the longest – but now the camera detection and the voice assistant genuinely run together in one program.

---

## 6. The Robotic Arm (Servos & Control)

Finally, the actual robotic arm: a housing I designed in Lido (CAD) and 3D printed, with servos and cables inside. The arm consists of three segments (one vertical segment, two angled segments) ending in a gripper. I also printed a dedicated PETG housing for the power supply (open at the bottom, closed at the top with a small air gap, vents on the left, right, and back) as well as a matching housing for the Raspberry Pi 5.

Control runs across two devices:
- **Raspberry Pi 5** – sends movement commands to the Pico over USB/Serial
- **Raspberry Pi Pico W** – drives the servos directly through a PCA9685 servo driver (I2C)

### 6.1 On the Pico W – drives the servos directly

```python
# pico_arm.py
# Runs on the Raspberry Pi Pico W.
# Reads numbers over the USB connection and uses them to move 6 servos.
#
# How to upload it: copy it onto the Pico W as main.py
# (e.g. with the MicroPico extension in VS Code).
# It then starts automatically as soon as the Pico gets power.

import sys
import time
from machine import I2C, Pin

# ---------------------------------------------------------
# This part talks to the PCA9685 servo driver.
# You don't need to understand or change anything here.
# ---------------------------------------------------------

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
PCA_ADDRESS = 0x40

def pca_write(register, value):
    i2c.writeto_mem(PCA_ADDRESS, register, bytes([value]))

def pca_start():
    pca_write(0x00, 0x00)
    prescale = int(25000000.0 / (4096 * 50) - 1)  # 50 Hz for servos
    pca_write(0x00, 0x10)
    pca_write(0xFE, prescale)
    pca_write(0x00, 0x00)
    time.sleep_ms(5)
    pca_write(0x00, 0xA1)

def set_servo_angle(channel, angle):
    angle = max(0, min(180, angle))
    pulse_microseconds = 500 + (2500 - 500) * angle / 180
    off_value = int(pulse_microseconds * 4096 / 20000)
    register = 0x06 + 4 * channel
    i2c.writeto_mem(PCA_ADDRESS, register, bytes([0, 0, off_value & 0xFF, off_value >> 8]))

pca_start()

# ---------------------------------------------------------
# From here on is the important part you should understand too.
# ---------------------------------------------------------

current_angles = [90, 90, 90, 90, 90, 90]  # Starting position: all servos centered

def move_arm(target_angles):
    """Moves all 6 servos slowly from the current position to the target position,
    so it doesn't jerk."""
    global current_angles
    steps = 30
    start_angles = current_angles[:]
    for step in range(1, steps + 1):
        for channel in range(6):
            new_angle = start_angles[channel] + (target_angles[channel] - start_angles[channel]) * step / steps
            set_servo_angle(channel, new_angle)
        time.sleep_ms(15)
    current_angles = target_angles[:]

# Main loop: waits for a line like "90,45,120,60,30,90" over USB
print("ready")
while True:
    line = sys.stdin.readline()
    if line:
        try:
            number_text = line.strip().split(",")
            target_angles = [int(z) for z in number_text]
            move_arm(target_angles)
            print("ok")
        except Exception:
            print("error: expected 6 comma-separated numbers, e.g. 90,90,90,90,90,90")
```

### 6.2 On the Raspberry Pi 5 – sends commands & remembers positions

```python
# arm_controller.py
# Runs on the Raspberry Pi 5.
# Sends movement commands to the Pico W and remembers named
# positions (e.g. "grab_book") in a file, so they persist
# even after the program is restarted.

import serial
import time
import json
import os

PICO_PORT = "/dev/ttyACM0"
POSITIONS_FILE = "positions.json"
SEQUENCES_FILE = "sequences.json"

connection = serial.Serial(PICO_PORT, 115200, timeout=2)
time.sleep(2)  # give the Pico time to start up


def move_arm(angles):
    """angles = list of 6 numbers between 0 and 180, e.g. [90,90,90,90,90,90]"""
    text = ",".join(str(w) for w in angles)
    connection.write((text + "\n").encode())
    reply = connection.readline().decode().strip()
    return reply


def load_file(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return {}


def save_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_position(name, angles):
    positions = load_file(POSITIONS_FILE)
    positions[name] = angles
    save_file(POSITIONS_FILE, positions)


def go_to_position(name):
    positions = load_file(POSITIONS_FILE)
    if name not in positions:
        print(f"Position '{name}' does not exist")
        return
    move_arm(positions[name])


def save_sequence(name, position_names):
    """position_names = list of position names to move through in order
    e.g. save_sequence("book", ["approach_book", "grab_book", "lift_book", "hand_over"])"""
    sequences = load_file(SEQUENCES_FILE)
    sequences[name] = position_names
    save_file(SEQUENCES_FILE, sequences)


def run_sequence(name, pause=1.0):
    sequences = load_file(SEQUENCES_FILE)
    if name not in sequences:
        print(f"Sequence '{name}' does not exist")
        return
    for position_name in sequences[name]:
        go_to_position(position_name)
        time.sleep(pause)
```

### 6.3 Teaching Positions (Terminal Program)

So I don't have to painfully convert positions into numbers by hand, there's a small terminal tool that lets me move each servo individually and then save the current pose under a name.

```python
# teach_positions.py
# Terminal program for teaching arm positions.
# Run with: python3 teach_positions.py

from arm_controller import move_arm, save_position

angles = [90, 90, 90, 90, 90, 90]
selected_servo = 0
step_size = 5

print("0-5 = select servo | + / - = move | s NAME = save | q = quit")
move_arm(angles)

while True:
    entry = input(f"[Servo {selected_servo} = {angles[selected_servo]} degrees] > ").strip()

    if entry == "q":
        break
    elif entry in "012345":
        selected_servo = int(entry)
    elif entry == "+":
        angles[selected_servo] = min(180, angles[selected_servo] + step_size)
        move_arm(angles)
    elif entry == "-":
        angles[selected_servo] = max(0, angles[selected_servo] - step_size)
        move_arm(angles)
    elif entry.startswith("s "):
        name = entry[2:].strip()
        save_position(name, angles[:])
        print(f"Position '{name}' saved")
    else:
        print("I didn't understand that")
```

This lets me type e.g. `s grab_book` to save the current arm pose under the name `grab_book`, and later drive back to exactly that pose with `go_to_position("grab_book")`.

---

## Hardware & Software Used

- Raspberry Pi 5 (main control, camera, AI, voice)
- Raspberry Pi Pico W (servo control)
- PCA9685 servo driver (I2C)
- 6 servos
- Camera (Raspberry Pi Camera Module, CSI)
- 3D-printed housing (designed in Lido), PETG housing for the power supply
- Python, OpenCV, Ultralytics YOLOv8, Ollama (Gemma3), pyttsx3, SpeechRecognition
