import time
from JMotor import JMotor
from Gyro import Gyro
from JServo import JServo
from Screen import Screen

motor = JMotor()
servo = JServo()
gyro = Gyro()
screen = Screen()

servo.fullleft()
screen.screen_data(gyro.screen)
time.sleep(2)
motor.turn_right()
gyro.desired_turn(90)
motor.stop()
motor.cleanup()
servo.cleanup()


    

