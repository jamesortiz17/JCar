import time
from Gyro import Gyro

def main():
    print("Starting gyro test...")
    gyro = Gyro(wait_for_calibration=False)  # skip calibration wait

    try:
        while True:
            euler = gyro.euler_heading()
            mag_orient = gyro.orientation()
            mag_str = f"{mag_orient:.2f}°" if mag_orient is not None else "No data"
            print(f"Euler Heading: {euler:.2f}°, Magnetometer Orientation: {mag_str}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test stopped by user.")

if __name__ == "__main__":
    main()
