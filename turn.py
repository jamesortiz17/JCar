import time
from JMotor import JMotor
from Gyro import Gyro
from JServo import JServo
from Screen import screen_print

motor = JMotor()
servo = JServo()
gyro = Gyro()

screen_print("hi", 'hello')
motor.forward()
motor.turn("right", 90)
motor.cleanup()


    

