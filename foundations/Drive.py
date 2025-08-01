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

        # Use relative heading from gyro
        start_heading = self.gyro.get_relative_heading()
        if direction == "right":
            target_heading = self.gyro.normalize_angle(start_heading + degrees)
        else:
            target_heading = self.gyro.normalize_angle(start_heading - degrees)

        print(f"Turning {direction} from {start_heading:.2f}° to {target_heading:.2f}°")
        acceptable_error = 0.2

        try:
            while True:
                current_heading = self.gyro.get_relative_heading()
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

                time.sleep(0.0075)
        finally:
            self.motor.stop()
            self.servo.center()
            print("Turn complete.")

    def correct_heading_with_servo(
        self,
        correction_threshold=1.0,
        correction_pulse_amount=8,
        correction_cooldown=1.5,
        history_length=5,
        min_heading_improvement_per_reading=0.02,
        max_offset=200
    ):
        if not hasattr(self, '_heading_history'):
            self._heading_history = deque(maxlen=history_length)
            self._last_correction_time = 0
            self._last_correction_direction = 0
            self._current_pulse_offset = 0

        heading = self.gyro.get_relative_heading()
        print(f"Relative Heading: {heading:.2f}°")
        now = time.time()
        self._heading_history.append(heading)

        def is_heading_correcting():
            if len(self._heading_history) < 2:
                return False
            diffs = [
                abs(self._heading_history[i]) - abs(self._heading_history[i + 1])
                for i in range(len(self._heading_history) - 1)
            ]
            avg_improvement = sum(diffs) / len(diffs)
            print(f"Avg improvement per reading: {avg_improvement:.3f}")
            return avg_improvement >= min_heading_improvement_per_reading

        if abs(heading) > correction_threshold:
            if (now - self._last_correction_time) > correction_cooldown:
                if is_heading_correcting():
                    print("Heading correcting itself, skipping servo adjustment.")
                else:
                    correction_direction = 1 if heading > 0 else -1
                    if correction_direction != self._last_correction_direction:
                        print("Correction direction changed, resetting last correction direction")

                    self._current_pulse_offset += correction_pulse_amount * correction_direction
                    self._current_pulse_offset = max(min(self._current_pulse_offset, max_offset), -max_offset)

                    self.servo.adjust_to(self._current_pulse_offset)
                    print(f"Applied servo correction of {correction_pulse_amount * correction_direction}, total offset: {self._current_pulse_offset}")

                    self._last_correction_time = now
                    self._last_correction_direction = correction_direction
        else:
            #print("Heading within deadband, holding servo position.")
            pass

    def cleanup(self):
        self.motor.cleanup()
        self.servo.cleanup()
        self.encoder.close()
        lgpio.gpiochip_close(self.h)

    def turn_to_absolute(self, target_heading):
        acceptable_error = 0.2  # or whatever you like
        direction = 'right' if self.gyro.angle_difference(self.gyro.get_relative_heading(), target_heading) > 0 else 'left'
    
        try:
            while True:
                current = self.gyro.get_relative_heading()
                error = self.gyro.angle_difference(current, target_heading)
    
                if abs(error) <= acceptable_error:
                    break
    
                if error > 0:
                    self.servo.turn_right()
                    self.motor.set_left_motor(True, 30)
                    self.motor.set_right_motor(False, 30)
                else:
                    self.servo.turn_left()
                    self.motor.set_left_motor(False, 30)
                    self.motor.set_right_motor(True, 30)
    
                sleep(0.0075)
        finally:
            self.motor.stop()
            self.servo.center()
            print("Turn complete.")

