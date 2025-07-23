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
        
    def heading(self):
        heading = self.sensor.euler[0]
        if heading is None:
            return 0
        return heading

    def format_vector(self, label, vec):
        if vec is None:
            return f"{label}: None"
        return f"{label}: x={vec[0]:.2f}, y={vec[1]:.2f}, z={vec[2]:.2f}"

    def get_heading(self):
        mag = self.sensor.magnetic
        if mag is None:
            return None
        x, y, z = mag
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        if heading_deg < 0:
            heading_deg += 360
        return heading_deg

gyro = Gyro()

while True:
    print("="*40)
    print("Temperature:", gyro.sensor.temperature, "°C")
    print(gyro.format_vector("Accelerometer", gyro.sensor.acceleration))
    print(gyro.format_vector("Magnetometer", gyro.sensor.magnetic))
    print(gyro.format_vector("Gyroscope", gyro.sensor.gyro))
    print(gyro.format_vector("Euler Angles", gyro.sensor.euler))
    print(gyro.format_vector("Quaternion", gyro.sensor.quaternion))
    print(gyro.format_vector("Linear Acceleration", gyro.sensor.linear_acceleration))
    print(gyro.format_vector("Gravity Vector", gyro.sensor.gravity))
    time.sleep(1)
