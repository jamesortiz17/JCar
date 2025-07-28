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

        while self.sensor.euler is None:
            time.sleep(0.1)

        if wait_for_calibration:
            print("Waiting for gyro calibration...")
            while not self.is_calibrated():
                sys, gyro, accel, mag = self.sensor.calibration_status
                print(f"Calib status - Sys:{sys}, Gyro:{gyro}, Accel:{accel}, Mag:{mag}")
                time.sleep(0.5)
            print("Calibration complete.")

    def format_vector(self, label, vec):
        if vec is None:
            return f"{label}: None"
        return f"{label}: x={vec[0]:.2f}, y={vec[1]:.2f}, z={vec[2]:.2f}"

    def heading(self):
        mag = self.sensor.magnetic
        if mag is None:
            return 0.0
        x, y, z = mag
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        if heading_deg < 0:
            heading_deg += 360
        return heading_deg

    def euler_heading(self):
        heading = self.sensor.euler[0]
        return heading if heading is not None else 0.0

    def is_calibrated(self):
        _, gyro, _, _ = self.sensor.calibration_status
        return gyro == 3

    def normalize_angle(self, angle):
        return angle % 360

    def turn_to(self, direction, degrees, smoothing_window=5):
        if direction.lower() not in ['left', 'right']:
            raise ValueError("Direction must be 'left' or 'right'")

        print(f"Rotating {direction} by {degrees} degrees...")

        start_heading = self.euler_heading()
        readings = deque([start_heading], maxlen=smoothing_window)

        if direction.lower() == 'right':
            target_heading = self.normalize_angle(start_heading + degrees)
        else:
            target_heading = self.normalize_angle(start_heading - degrees)

        print(f"Start Heading: {start_heading:.2f}° | Target: {target_heading:.2f}°")

        try:
            while True:
                heading = self.euler_heading()
                readings.append(heading)
                avg_heading = sum(readings) / len(readings)
                avg_heading = self.normalize_angle(avg_heading)

                print(f"Smoothed Heading: {avg_heading:.2f}°  (Raw: {heading:.2f}°)")

                if direction.lower() == 'right':
                    if self.normalize_angle(avg_heading - start_heading) >= degrees:
                        break
                else:
                    if self.normalize_angle(start_heading - avg_heading) >= degrees:
                        break

                time.sleep(0.05)

            print("Turn complete.")
        except KeyboardInterrupt:
            print("\nTurn interrupted.")
