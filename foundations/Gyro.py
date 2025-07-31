import time
import math
import board
import busio
import adafruit_bno055

class Gyro:
    def __init__(self, wait_for_calibration=False, min_change_deg=0.5):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

        while self.sensor.euler is None:
            time.sleep(0.1)

        self.initial_heading = self._get_raw_heading()
        self.prev_heading = 0.0  # relative to initial
        self.min_change_deg = min_change_deg

        if wait_for_calibration:
            print("Waiting for gyro calibration...")
            while not self.is_calibrated():
                sys, gyro, accel, mag = self.sensor.calibration_status
                print(f"Calib status - Sys:{sys}, Gyro:{gyro}, Accel:{accel}, Mag:{mag}")
                time.sleep(0.5)
            print("Calibration complete.")

    def _get_raw_heading(self):
        """Raw euler heading from sensor (0–360), fallback-safe."""
        heading = self.sensor.euler[0]
        return heading if heading is not None else self.initial_heading

    def get_relative_heading(self):
        """Returns current heading relative to initial, normalized between -180 and 180."""
        current = self._get_raw_heading()
        delta = self.angle_difference(current, self.initial_heading)
        return delta

    def heading_changed(self):
        """Returns True if relative heading changed by more than threshold."""
        current = self.get_relative_heading()
        diff = self.angle_difference(current, self.prev_heading)
        if abs(diff) >= self.min_change_deg:
            self.prev_heading = current
            return True
        return False

    def get_heading_if_changed(self):
        if self.heading_changed():
            return self.prev_heading
        return None

    def is_calibrated(self):
        _, gyro, _, _ = self.sensor.calibration_status
        return gyro == 3

    def normalize_angle(self, angle):
        """Clamp any angle to 0–360."""
        return angle % 360

    def angle_difference(self, a, b):
        """Shortest signed difference between two angles."""
        return (a - b + 180) % 360 - 180

    def orientation(self):
        """Optional magnetometer-based heading (as backup or correction)."""
        mag = self.sensor.magnetic
        if mag is None:
            return None
        x, y, _ = mag
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        return heading_deg % 360

    def reset_heading(self):
        """Call this to re-zero the heading to current direction."""
        self.initial_heading = self._get_raw_heading()
        self.prev_heading = 0.0
