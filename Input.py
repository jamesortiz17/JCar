from time import sleep
from JMotor import JMotor
from JDist import JDist

distance_sensor = JDist(19, 26)
motor = JMotor()

motor.speed_ms = 1.23  # Your measured speed at 100% PWM

try:
    while True:
        distance = float(input("How far do you want to drive? (in METERS): "))
        input_speed = float(input("Speed (1 to 10): "))

        motor.set_speed(input_speed)

        # Assume linear scaling of speed_ms\
        
        scaled_speed = (input_speed / 10.0) * motor.speed_ms
        t = distance / scaled_speed

        print(f"Calculated drive time: {t:.2f} seconds")

        motor.forward()
        sleep(t)
        motor.instant_stop()
        sleep(1)

        print("done")
        break

finally:
    motor.cleanup()
