import time
import lgpio

from Motor import JMotor
from Encoder import DistanceEncoder

# Setup
h = lgpio.gpiochip_open(0)
motor = JMotor(h)
encoder = DistanceEncoder(h)

def drive_distance(motor, encoder, forward=True, distance=1.0, speed=30):
    """Drive a fixed distance in meters."""
    encoder.reset()
    if forward:
        motor.forward()
    else:
        motor.backward()
    motor.set_speed(speed)

    while abs(encoder.get_distance()) < distance:
        time.sleep(0.01)

    motor.stop()

try:
    print("Driving forward 1m...")
    drive_distance(motor, encoder, forward=True, distance=1.0, speed=30)

    time.sleep(1)

    print("Driving backward 1m...")
    drive_distance(motor, encoder, forward=False, distance=1.0, speed=30)

    time.sleep(1)

    print("Zigzag forward...")
    motor.zigzag(max_speed=30, cycles=3, step_delay=0.05, step_size=2, forward=True)

    time.sleep(1)

    print("Zigzag backward...")
    motor.zigzag(max_speed=30, cycles=3, step_delay=0.05, step_size=2, forward=False)

finally:
    print("Cleaning up...")
    motor.cleanup()
    encoder.close()
    lgpio.gpiochip_close(h)
