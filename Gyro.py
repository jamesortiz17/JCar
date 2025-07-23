import time
import board
import busio
import adafruit_bno055

class Gyro:
    def __init__(self, i2c):
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

        # wait for initialize
        while self.sensor.euler is None:
            time.sleep(0.1)

    def heading(self):
        
        heading = self.sensor.euler[0]
        if heading is None:
            return 0  # Fallback or error value
        return heading


# Set up I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize BNO055 sensor
sensor = adafruit_bno055.BNO055_I2C(i2c)

# Helper to avoid 'None' values from uninitialized data
def format_vector(label, vec):
    if vec is None:
        return f"{label}: None"
    return f"{label}: x={vec[0]:.2f}, y={vec[1]:.2f}, z={vec[2]:.2f}"{vec[2]:.2f}"


def get_heading(sensor):
    mag = sensor.magnetic
    if mag is None:
        return None

    x, y, z = mag
    heading_rad = math.atan2(y, x)
    heading_deg = math.degrees(heading_rad)
    if heading_deg < 0:
        heading_deg += 360
    return heading_deg

        
while True:
    print("="*40)
    print("Temperature:", sensor.temperature, "°C")
    print(format_vector("Accelerometer", sensor.acceleration))
    print(format_vector("Magnetometer", sensor.magnetic))
    print(format_vector("Gyroscope", sensor.gyro))
    print(format_vector("Euler Angles", sensor.euler))
    print(format_vector("Quaternion", sensor.quaternion))
    print(format_vector("Linear Acceleration", sensor.linear_acceleration))
    print(format_vector("Gravity Vector", sensor.gravity))
    time.sleep(1)
    
    
