import time
import lgpio
from Motor import JMotor
from Gyro import Gyro
from Servo import JServo
from Encoder import DistanceEncoder
from Dist import JDist


class Drive:
    def __init__(self):
        self.h = lgpio.gpiochip_open(0)
        self.motor = JMotor(self.h)
        self.servo = JServo(self.h)
        self.gyro = Gyro()
        self.encoder = DistanceEncoder(self.h)
        self.dist = JDist(self.h)  
        self.last_veering_direction = None
        self.veer_repeat_count = 0


    def forward(self):
        self.motor.forward()

    def backward(self):
        self.motor.backward()

    def stop(self):
        self.motor.stop()

    def maintain_center(self, check_interval=0.2, max_correction_time=0.5):
        self.dist.update()
        direction = self.dist.veering_trend()

        if direction != self.last_veering_direction:
            self.veer_repeat_count = 1
            self.last_veering_direction = direction
        else:
            self.veer_repeat_count += 1

        # Only correct if trend repeated a few times
        if self.veer_repeat_count < 3 or direction is None:
            self.servo.center()
            print("Centered or not consistently veering.")
            return

        print(f"Veering {direction}. Applying gentle correction.")
        if direction == "left":
            self.servo.slight_right()
        elif direction == "right":
            self.servo.slight_left()

        start_time = time.time()
        while time.time() - start_time < max_correction_time:
            time.sleep(check_interval)
            self.dist.update()
            if self.dist.side_stable():
                print("Wall alignment stabilized. Re-centering steering.")
                break

        self.servo.center()



    def turn_to(self, direction, degrees):
        if direction.lower() not in ['left', 'right']:
            raise ValueError("Direction must be 'left' or 'right'")

        start_heading = self.gyro.euler_heading()
        if direction == "right":
            target_heading = self.gyro.normalize_angle(start_heading + degrees)
        else:
            target_heading = self.gyro.normalize_angle(start_heading - degrees)

        print(f"Turning {direction} from {start_heading:.2f}° to {target_heading:.2f}°")
        acceptable_error = 1.0

        try:
            while True:
                current_heading = self.gyro.euler_heading()
                delta = abs(self.gyro.angle_difference(current_heading, target_heading))
                print(f"Current Heading: {current_heading:.2f}°, Target: {target_heading:.2f}°, Error: {delta:.2f}°")

                if delta <= acceptable_error:
                    break

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

    def cleanup(self):
        self.motor.cleanup()
        self.servo.cleanup()
        self.encoder.close()
        lgpio.gpiochip_close(self.h)
