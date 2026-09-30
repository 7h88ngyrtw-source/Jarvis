import sys
import time
from machine import I2C, Pin

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
PCA_ADDRESS = 0x40

def pca_write(register, value):
    i2c.writeto_mem(PCA_ADDRESS, register, bytes([value]))

def pca_start():
    pca_write(0x00, 0x00) 
    scaling = int(25000000.0 / (4096 * 50) - 1)
    pca_write(0x00, 0x10)
    pca_write(0x00, scaling)
    pca_write(0x00, 0x00)
    time.sleep(0.005)
    pca_write(0x00, 0xA1)

def servo_angle(channel, angle):
    angle = max(0, min(180, angle))
    pulse_length = 500 + (2500 -500) * angle / 180
    value = int(pulse_length * 4096 / 20000) 
    register = 0x06 + 4 * channel
    pca_write(register, value & 0xFF)
    pca_write(register + 1, (value >> 8) & 0xFF)

pca_start()

angles = [90, 90, 90, 90, 90, 90]

def move_servos(goal_angles):
    global angles
    steps = 30
    start_angles = angles[:]
    for step in range(1, steps +1):
        for channel in range(6):
            new_angle = start_angles[channel] + (goal_angles[channel] - start_angles[channel]) * step / steps
            servo_angle(channel, new_angle)
            servo_angle(channel, new_angle)
        time.sleep(0.015)
    angles = goal_angles[:]

print("Ready!")
while True:
    line = sys.stdin.readline()
    if line:
        try: 
            text= line.strip().split(",")
            goal_angles = [int(z) for z in text]
            move_servos(goal_angles)
            print("Moved to angles:", goal_angles)
        except Exception:
            print("Error processing input:", line.strip())

    


