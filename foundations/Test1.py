from Gyro import Gyro
import time

def main():
    gyro = Gyro(wait_for_calibration=True, min_change_deg=0.01)

    print("Zeroed relative heading. Rotate to test.")

    try:
        while True:
            heading = gyro.get_heading_if_changed()
            if heading is not None:
                print(f"Relative Heading: {heading:.2f}°")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
