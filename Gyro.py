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

    def print_vals(self):
        
        print("Temperature:", self.sensor.temperature, "°C")
        print(self.format_vector("Accelerometer", self.sensor.acceleration))
        print(self.format_vector("Magnetometer", self.sensor.magnetic))
        print(self.format_vector("Gyroscope", self.sensor.gyro))
        print(self.format_vector("Euler Angles", self.sensor.euler))
        print(self.format_vector("Quaternion", self.sensor.quaternion))
        print(self.format_vector("Linear Acceleration", self.sensor.linear_acceleration))
        print(self.format_vector("Gravity Vector", self.sensor.gravity))
        time.sleep(1)
        
    def desired_turn(self, target_degrees):
        start_angle = self.get_angle()
    
        while True:
            current_angle = self.get_angle()
            theta = (current_angle - start_angle + 360) % 360
            
            if theta >= target_degrees:
                break
            
            time.sleep(0.01)  
