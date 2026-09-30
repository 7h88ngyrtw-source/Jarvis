#### JARVIS IS THE MAIN FILE FOR THIS PROJECT (THE ONLY FINISHED PART)
## Introduction 
Jarvis is my Desk Assistant made for helping me, both physically and mentally (means that he can talk about anything with me). He uses camera vision, speech recognition a local AI - Gemma3. My goal was to build my own little Jarvis, like Iron Man's. I couldn't finish it because it took much longer than I thought and sometimes I didn't even want to finish it because all the problem really sucked. I still hope that you can use this and maybe correct some of it.

## Jarvis my assistant:

Jarvis would be a assistant robot that can see, listen, and talk — built around a Raspberry Pi 5, a local voice assistant, and (in progress) a robotic arm that can hand you things you ask for.

This was built as my Hack Club Stardance project.

## What Jarvis can do right now:

- : a camera (originally a MacBook webcam, later swapped for the official Raspberry Pi Camera Module) feeds a YOLOv8 Nano model that detects objects in real time and keeps a live list of what's currently visible. (Is not included in my finished code because i had to seperate both scripts to finish one)
- Listens and talks: A voice assistant listens through the microphone, transcribes speech with speech recognition, and responds using Gemma3 1b running locally through Ollama — no cloud API needed. Responses are spoken back with 'pyttsx3'.
Whatever the camera currently sees is passed to the assistant as context, so it can answer questions like 
Camera and voice used to run as two separate scripts (started via `subprocess`), and were later merged into one program (`haupt.py`) that runs both as parallel threads so they can share information — most importantly, the list of currently detected objects. (in progress)

## The robot arm (work in progress)

The plan for Jarvis' arm: three segments (one vertical, two angled joints) ending in a gripper, driven by six servos through a PCA9685 driver controlled by a Raspberry Pi Pico W, with the Pi 5 sending movement commands to the Pico over serial. Both the arm and the power supply sit in custom 3D-printed enclosures (designed in TinkerCAD).
later.

Status: the servo/PCA9685 control code, the teach tool, and the serial link between the Pico and the Pi all work individually and have been tested end to end. What's still missing is the final piece connecting it to the voice assistant — matching a spoken request ("give me my book") to a detected object and triggering the right saved sequence. The hardware and the software for each piece exist; they just aren't fully wired together yet.

## Tech stack:

-Hardware: Raspberry Pi 5, Raspberry Pi Pico W, PCA9685 servo driver, 6x servos, Raspberry Pi Camera Module, custom PSU switching supply
-Computer vision**: OpenCV + Picamera2, YOLOv8 Nano (Ultralytics)
-Voice: SpeechRecognition (Google), pyttsx3 (text-to-speech)
-AI: Ollama running Gemma 3 1B, fully local
-Arm control: MicroPython on the Pico W, PCA9685 (I2C), pyserial on the Pi 5

## What's next

- Finish connecting object detection + voice commands to the arm's saved sequences
- Teach real pick-up positions for a handful of everyday objects
- Move from manual `python3 haupt.py` startup to a systemd service so Desa starts headless on boot

## Lessons learned

A big chunk of the time went into things that aren't visible in the code: figuring out CSI camera orientation, why 'cv2.imsho' doesn't work over SSH without a display,'pyttsx3' defaulting to a voice ID that doesn't exist on Linux, and generally the gap between "runs on my Mac" and "runs headless on a Pi." Most of the actual debugging was hardware/environment plumbing, not the robotics logic itself.

## I'm uploading all files and here you can look what each one does or should do as soon as my robot is finished.
 'camera2.py'  Runs on the Pi 5. Captures frames from the Raspberry Pi Camera, detects objects with YOLOv8 Nano, and keeps a live list of what's currently visible. 
'jarvis2.py' Voice assistant meant to run alongside the camera. Listens via microphone, sends commands to Gemma 3 (via Ollama), speaks the reply with 'pyttsx3'. Takes a camera tracker as input so it knows what's currently in view. 
'haupt.py' Main entry point. Starts the camera and the voice assistant together as two parallel threads. 
'pico_arm.py' Runs on the Pico W. Drives the 6 servos through the PCA9685 and waits for angle commands sent over USB. 
'arm_controller.py' Runs on the Pi 5. Sends movement commands to the Pico over serial, and manages named positions/sequences saved as JSON.
'teach_positions.py' Terminal tool for teaching arm positions: jog each servo with +/- and save the current pose under a name. 

## This is my voice assistant that works and that you can use now and is the one that took me the most time to write and finish:

'Jarvis.py' Standalone version of the voice assistant — same core loop (listen, ask Gemma, speak) but runs on its own, without the camera.
