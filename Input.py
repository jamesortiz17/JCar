from time import sleep
from JMotor import JMotor
from JDist import JDist

distance_sensor = JDist(19,26)
motor = JMotor()

while True:
    
    distance = input("How far do you want to drive?\n")
    speed = float(input("what speed do you want?"))
    
    t = float(distance) / float(motor.speed_ms*speed)
    print(t)
    print(distance_sensor.read_distance())
    motor.forward()
    sleep(int(t))
    motor.instant_stop()
    sleep(1)
    motor.cleanup()
    print("done")
    print ("hi")
    break 
    



