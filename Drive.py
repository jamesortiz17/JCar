from Encoder import DistanceEncoder
from JMotor import JMotor
import time

# Set up your motors and encoders
left_encoder = DistanceEncoder(pin_a=12, pin_b=13)
right_encoder = DistanceEncoder(pin_a=5, pin_b=6)
motor = JMotor()

def drive_cm(target_distance_cm, speed = motor.set_speed):
    # Reset encoders
    left_encoder.reset()
    right_encoder.reset()

    motor.forward(speed)

    while True:
        left_dist = left_encoder.get_distance_cm()
        right_dist = right_encoder.get_distance_cm()
        avg_dist = (left_dist + right_dist) / 2

        if avg_dist >= target_distance_cm:
            break

        time.sleep(0.01)

    motor.stop()
