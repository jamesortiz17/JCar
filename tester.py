import time
from collections import deque
from adafruit_bno055 import BNO055_I2C
import board
import busio

# Initialize I2C and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = BNO055_I2C(i2c)

def get_heading():
    """Get heading from sensor safely."""
    heading = sensor.euler[0]
    if heading is None:
        return 0.0
    return heading

def is_calibrated():
    """Check if gyro is calibrated."""
    sys, gyro, accel, mag = sensor.calibration_status
    return gyro == 3

def run_heading_test(smoothing_window=5):
    print("Rotate the robot slowly. Press Ctrl+C to stop.")
    
    readings = deque(maxlen=smoothing_window)

    try:
        while True:
            if not is_calibrated():
                print("Waiting for gyro calibration...")
                time.sleep(0.5)
                continue

            heading = get_heading()
            readings.append(heading)

            avg_heading = sum(readings) / len(readings)
            print(f"Smoothed Heading: {avg_heading:.2f}°  (Raw: {heading:.2f}°)")

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    run_heading_test()
