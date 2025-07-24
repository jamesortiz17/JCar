from JMotor import JMotor
import time

motor = JMotor()



# drive until input then calculate time of drive
motor.forward()
initial_time = time.time()
input()
motor.stop()
final_time = time.time()
elapsed_time = final_time - initial_time
print(elapsed_time)

#use elasped time to calculate distance 
d = motor.distance(elapsed_time, motor.velocity)
print(d)

