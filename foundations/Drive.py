import time
import lgpio
from .Motor import JMotor
from .Gyro import Gyro
from .Servo import JServo
from .Encoder import DistanceEncoder

class Drive:
    def __init__(self):
        self.h = lgpio.gpiochip_open(0)   # open once here
        self.motor = JMotor(self.h)
        self.servo = JServo(self.h)
        self.gyro = Gyro()
        self.encoder = DistanceEncoder(self.h)  # modify DistanceEncoder to accept h!


    def turn_to(self, direction, degrees):
        if direction.lower() not in ['left', 'right']:
            raise ValueError("Direction must be 'left' or 'right'")
    
        start_heading = self.gyro.euler_heading()
        if direction == "right":
            target_heading = self.gyro.normalize_angle(start_heading + degrees)
        else:
            target_heading = self.gyro.normalize_angle(start_heading - degrees)
    
        print(f"Turning {direction} from {start_heading:.2f}° to {target_heading:.2f}°")
    
        acceptable_error = 1.0  # increased tolerance for reliability
    
        try:
            while True:
                current_heading = self.gyro.euler_heading()
                delta = abs(self.gyro.angle_difference(current_heading, target_heading))
                print(f"Current Heading: {current_heading:.2f}°, Target: {target_heading:.2f}°, Error: {delta:.2f}°")
    
                if delta <= acceptable_error:
                    break
    
                # Repeat motor and servo commands continuously during turn
                if direction == "right":
                    self.servo.turn_right()
                    self.motor.set_left_motor(True, 30)
                    self.motor.set_right_motor(False, 30)
                else:
                    self.servo.turn_left()
                    self.motor.set_left_motor(False, 30)
                    self.motor.set_right_motor(True, 30)
    
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
        self.motor.cleanup()    # remove any gpiochip_close here
        self.servo.cleanup()    # remove gpiochip_close here
        self.encoder.close()    # remove gpiochip_close here
        lgpio.gpiochip_close(self.h)  # close once here

