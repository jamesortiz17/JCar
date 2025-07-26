import time
import board
import busio
import adafruit_bno055
import math

class Gyro:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)
        
        while self.sensor.euler is None:
            time.sleep(0.1)

    def format_vector(self, label, vec):
        if vec is None:
            return f"{label}: None"
        return f"{label}: x={vec[0]:.2f}, y={vec[1]:.2f}, z={vec[2]:.2f}"

    def heading(self):
        mag = self.sensor.magnetic
        if mag is None:
            return None
        x, y, z = mag
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        if heading_deg < 0:
            heading_deg += 360
        return heading_deg

    def print_vals(self):
        
        while True:
            print("Temperature:", self.sensor.temperature, "°C")
            print(self.format_vector("Accelerometer", self.sensor.acceleration))
            print(self.format_vector("Magnetometer", self.sensor.magnetic))
            print(self.format_vector("Gyroscope", self.sensor.gyro))
            print(self.format_vector("Euler Angles", self.sensor.euler))
            print(self.format_vector("Quaternion", self.sensor.quaternion))
            print(self.format_vector("Linear Acceleration", self.sensor.linear_acceleration))
            print(self.format_vector("Gravity Vector", self.sensor.gravity))
            time.sleep(1)
        
    def desired_turn(self, target_deg):
        start_heading = self.heading()
        print(f"Start heading: {start_heading}")

        while True:
            current_heading = self.heading()
        # Calculate how much we've turned (0 to 360)
            turned = (current_heading - start_heading + 360) % 360
            print(f"Current heading: {current_heading}, Turned: {turned:.2f}°")

            if turned >= target_deg:
                print("Target reached!")
                break

            time.sleep(0.01)  # small delay to avoid hogging CPU

    def test_gyro_heading(gyro):
        print("Rotate the robot slowly, press Ctrl+C to stop")
        try:
            while True:
                h = gyro.heading()
                print(f"Heading: {h:.2f}°")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped")
