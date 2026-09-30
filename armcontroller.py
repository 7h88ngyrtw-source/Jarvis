import serial
import time
import json
import os

PICO_PORT = "/dev/ttyACM0"
POSITION_FILE = "position.json"
SEQUENCE_FILE = "sequence.json"

connection = serial.Serial(PICO_PORT, 115200, timeout=2)
time.sleep(2)  # Wait for the connection to establish

def move_servo(angle):
    command = ",".join(map(str, angle)) + "\n"
    connection.write(command.encode())
    response = connection.readline().decode().strip()
    print("Response from Pico:", response)
    answer = connection.readline().decode().strip()
    return answer

def load_file(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return {}

def save_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def position_save(name, angle):
    position = load_file(POSITION_FILE)
    position[name] = angle
    save_file(POSITION_FILE, position)

def go_to_position(name):
    position = load_file(POSITION_FILE)
    if name not in position:
        print(f"Position '{name}' not found.")
        return
    move_servo(position[name])

def sequence_save(name, positions_names):
    sequence = load_file(SEQUENCE_FILE)
    sequence[name] = positions_names
    save_file(SEQUENCE_FILE, sequence)

def run_sequence(name, pause_time=1):
    sequence = load_file(SEQUENCE_FILE)
    if name not in sequence:
        print(f"Sequence '{name}' not found.")
        return
    for position_name in sequence[name]:
        go_to_position(position_name)
        time.sleep(pause_time)
