import time
import lgpio
from collections import deque 

from .Motor import JMotor
from .Gyro import Gyro
from .Servo import JServo
from .Encoder import DistanceEncoder
from .Dist import JDist


class Drive:
    def __init__(self):
        self.h = lgpio.gpiochip_open(0)
        self.motor = JMotor(self.h)
        self.servo = JServo(self.h)
        self.gyro = Gyro()
        self.encoder = DistanceEncoder(self.h)
        self.dist = JDist(self.h)  

    def forward(self):
        self.motor.forward()

    def backward(self):
        self.motor.backward()

    def stop(self):
        self.motor.stop()

    def turn_to(self, direction, degrees):
        if direction.lower() not in ['left', 'right']:
            raise ValueError("Direction must be 'left' or 'right'")

        #use relative heading from gyro
        start_heading = self.gyro.get_relative_heading()
        if direction == "right":
            target_heading = self.gyro.normalize_angle(start_heading + degrees)
        else:
            target_heading = self.gyro.normalize_angle(start_heading - degrees)

        print(f"Turning {direction} from {start_heading:.2f}° to {target_heading:.2f}°")
        acceptable_error = 0.1

        try:
            while True:
                current_heading = self.gyro.get_relative_heading()
                delta = abs(self.gyro.angle_difference(current_heading, target_heading))
                print(f"Current Heading: {current_heading:.2f}°, Target: {target_heading:.2f}°, Error: {delta:.2f}°")

                if delta <= acceptable_error:
                    break

                if direction == "right":
                    self.motor.set_left_motor(True, 30)
                    self.motor.set_right_motor(False, 30)
                else:
                    self.motor.set_left_motor(False, 30)
                    self.motor.set_right_motor(True, 30)

                time.sleep(0.0075)
        finally:
            self.motor.stop()
            self.servo.center()
            #print("Turn complete.")

    def cleanup(self):
        self.motor.cleanup()
        self.servo.cleanup()
        self.encoder.close()
        lgpio.gpiochip_close(self.h)

