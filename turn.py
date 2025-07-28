import time
from JMotor import JMotor
from Gyro import Gyro
from JServo import JServo
from Screen import screen_print
from encodertest import JEncoder

motor = JMotor()
servo = JServo()
gyro = Gyro()
enc = JEncoder()

motor.forward()
enc.print_counts()

#motor.turn("right",90)


#screen_print("hi", 'hello')
#motor.forward()
#time.sleep(1)
#motor.chat_turn("right", 90)
#print("done")
#motor.cleanup()


    

