import time
import math
from collections import deque
import board
import busio
import adafruit_bno055


class Gyro:
    def __init__(self, wait_for_calibration=False):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

        # Wait until sensor starts returning valid data
        while self.sensor.euler is None:
            time.sleep(0.1)

        if wait_for_calibration:
            print("Waiting for gyro calibration...")
            while not self.is_calibrated():
                sys, gyro, accel, mag = self.sensor.calibration_status
                print(f"Calib status - Sys:{sys}, Gyro:{gyro}, Accel:{accel}, Mag:{mag}")
                time.sleep(0.5)
            print("Calibration complete.")

    def euler_heading(self):
        heading = self.sensor.euler[0]
        return heading if heading is not None else 0.0

    def is_calibrated(self):
        _, gyro, _, _ = self.sensor.calibration_status
        return gyro == 3

    def normalize_angle(self, angle):
        """Wrap angle to [0, 360)."""
        return angle % 360

    def angle_difference(self, a, b):
        """Shortest signed difference between two angles in degrees."""
        diff = (a - b + 180) % 360 - 180
        return diff

    def average_angles(self, angles):
        """Circular mean of angles."""
        sin_sum = sum(math.sin(math.radians(a)) for a in angles)
        cos_sum = sum(math.cos(math.radians(a)) for a in angles)
        return math.degrees(math.atan2(sin_sum, cos_sum)) % 360

    def turn_to(self, direction, degrees):
        if direction.lower() not in ['left', 'right']:
            raise ValueError("Direction must be 'left' or 'right'")

        start_heading = self.euler_heading()

        if direction.lower() == 'right':
            target_heading = self.normalize_angle(start_heading + degrees)
        else:
            target_heading = self.normalize_angle(start_heading - degrees)

        #print(f"Start Heading: {start_heading:.2f}° | Target: {target_heading:.2f}°")

        try:
            while True:
                current_heading = self.euler_heading()
                delta = abs(self.angle_difference(current_heading, start_heading))

                print(f"Current Heading: {current_heading:.2f}°")

                if delta >= degrees:
                    break

                time.sleep(0.01)

            print("Turn complete.")

        except KeyboardInterrupt:
            print("\nTurn interrupted.")
