# from JMotor import JMotor
# from Gyro import Gyro
import time

# motor = JMotor()
# gyro = Gyro()


initial_time = time.time()
deg = 0
while(True):
    # drive until input then calculate time of drive
    # motor.forward()
    
    inp = input()
    if inp == "r":
        deg = 90
        print("here")
        # motor.turn_right()
    elif inp == 'l':
        deg = 270
        print("bere")
    else:
        continue
        # motor.turn_left()
        
    # gyro.desired_turn(deg)
    cur_time = time.time()
    turn_time =  cur_time - initial_time
    print(f"{turn_time} before turning {deg}")
    #sql save insert deg and time 
    initial_time = cur_time    
        
    # motor.stop()
    time.sleep(1)

#use elasped time to calculate distance 
d = motor.distance(elapsed_time, motor.velocity)
print(d)

