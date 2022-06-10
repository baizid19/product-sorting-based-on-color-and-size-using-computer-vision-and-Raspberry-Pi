from time import *
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

kit.servo[0].angle = 160

while True:
    kit.servo[0].angle = 50
    sleep(0.5)
    kit.servo[0].angle = 160
    sleep(2.9)
    