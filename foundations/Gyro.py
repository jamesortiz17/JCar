import time
import math
import board
import busio
import adafruit_bno055

class Gyro:
    def __init__(self, wait_for_calibration=False):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

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
        return angle % 360

    def angle_difference(self, a, b):
        diff = (a - b + 180) % 360 - 180
        return diff

    def mag_heading(self):
        """
        Calculate heading (0-360 degrees) from magnetometer readings.
        Uses atan2 of magnetic Y and X axes.
        """
        mag = self.sensor.magnetic  # returns (x, y, z) or None if no data

        if mag is None:
            return None

        x, y, _ = mag
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        if heading_deg < 0:
            heading_deg += 360

        return heading_deg
