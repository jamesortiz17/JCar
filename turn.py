import time
from JMotor import JMotor
from Gyro import Gyro
from JServo import JServo

motor = JMotor()
servo = JServo()

servo.fullleft()
time.sleep(2)
motor.turn_right()
time.sleep(1.5)
motor.stop()
motor.cleanup()
servo.cleanup()


    

