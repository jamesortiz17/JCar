import time
from Gyro import Gyro

def main():
    gyro = Gyro(wait_for_calibration=True)  # or False if you want it to start right away

    try:
        while True:
            heading = gyro.euler_heading()
            print(f"Heading: {heading:.2f}°")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    main()
