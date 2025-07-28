import time
from JMotor import JMotor
from Gyro import Gyro
from JServo import JServo

class Drive:
    def __init__(self):
        self.motor = JMotor()
        self.gyro = Gyro()
        self.servo = JServo()

    def turn_to(self, direction, degrees):
        if direction.lower() not in ['left', 'right']:
            raise ValueError("Direction must be 'left' or 'right'")

        start_heading = self.gyro.euler_heading()
        if direction == "right":
            target_heading = self.gyro.normalize_angle(start_heading + degrees)
            # Motor config for right turn
            self.motor.set_left_motor(True, 30)
            self.motor.set_right_motor(False, 30)
        else:
            target_heading = self.gyro.normalize_angle(start_heading - degrees)
            # Motor config for left turn
            self.motor.set_left_motor(False, 30)
            self.motor.set_right_motor(True, 30)

        print(f"Turning {direction} from {start_heading:.2f}° to {target_heading:.2f}°")

        acceptable_error = 0.1  # degrees tolerance
        try:
            while True:
                current_heading = self.gyro.euler_heading()
                delta = abs(self.gyro.angle_difference(current_heading, target_heading))
                print(f"Current Heading: {current_heading:.2f}°, Target: {target_heading:.2f}°, Error: {delta:.2f}°")

                if delta <= acceptable_error:
                    break
                time.sleep(0.01)
        finally:
            self.motor.stop()
            self.servo.center()
            print("Turn complete.")

    def forward(self):
        self.motor.forward()

    def backward(self):
        self.motor.backward()

    def stop(self):
        self.motor.stop()

    def cleanup(self):
        self.motor.cleanup()
        self.servo.cleanup()
