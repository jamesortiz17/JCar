from time import sleep
from JMotor import JMotor


motor = JMotor()

while True:
    
    distance = input("How far do you want to drive?\n")
    speed = float(input("what speed do you want?"))
    
    t = float(distance) / float(motor.speed_ms*speed)
    print(t)
    motor.forward()
    sleep(int(t))
    motor.instant_stop()
    sleep(1)
    motor.cleanup()
    print("done")
    print ("hi")
    break 
    



