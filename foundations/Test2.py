import time
import lgpio
from Dist import JDist  # Make sure JDist.py is in the same directory or in your PYTHONPATH

def main():
    h = lgpio.gpiochip_open(0)  # Open GPIO chip 0
    dist = JDist(h)

    try:
        print("Reading right sensor distances...\nPress Ctrl+C to stop.")
        while True:
            dist.update()
            right = dist.get_current_distances()["right"]
            print(f"Right sensor: {right} cm")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        lgpio.gpiochip_close(h)

if __name__ == "__main__":
    main()
