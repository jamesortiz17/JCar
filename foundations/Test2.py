import time
import lgpio
import numpy as np
from collections import deque
from your_dist_module import JDist  # replace with your actual import path

def filter_outliers(history, new_val, max_jump=3.0):
    """Ignore new_val if it differs too much from recent average."""
    if not history:
        return True  # accept first reading
    avg = np.mean(history)
    if abs(new_val - avg) > max_jump:
        return False
    return True

def calc_slope(data):
    """Calculate slope of data points using linear regression."""
    if len(data) < 2:
        return 0
    x = np.arange(len(data))
    y = np.array(data)
    A = np.vstack([x, np.ones(len(x))]).T
    m, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return m

def main():
    h = lgpio.gpiochip_open(0)
    dist_sensor = JDist(h)
    slope_threshold = 0.05  # cm per sample (adjust based on speed & noise)
    max_jump = 3.0  # cm, max allowed jump to accept reading

    print("Starting veering detection test. Ctrl+C to stop.")

    try:
        while True:
            dist_sensor.update()
            # Get raw current distances
            distances = dist_sensor.get_current_distances()

            # Filter new readings to avoid jumps
            for side in ["left", "right"]:
                hist = dist_sensor.sensors[side]["history"]
                if hist:
                    latest = hist[-1]
                    # If latest reading is a big jump, remove it
                    if not filter_outliers(list(hist)[:-1], latest, max_jump):
                        hist.pop()  # discard outlier

            left_hist = list(dist_sensor.sensors["left"]["history"])
            right_hist = list(dist_sensor.sensors["right"]["history"])

            left_slope = calc_slope(left_hist) if left_hist else 0
            right_slope = calc_slope(right_hist) if right_hist else 0

            status = "Straight"
            if left_slope < -slope_threshold:
                status = "Veering Left"
            elif right_slope < -slope_threshold:
                status = "Veering Right"
            elif left_slope > slope_threshold:
                status = "Veering Right"
            elif right_slope > slope_threshold:
                status = "Veering Left"

            print(f"Left Distances: {left_hist}")
            print(f"Right Distances: {right_hist}")
            print(f"Left Slope: {left_slope:.4f}, Right Slope: {right_slope:.4f} => {status}")
            print("-" * 50)

            time.sleep(0.1)  # 100ms delay, adjust as needed

    except KeyboardInterrupt:
        print("Stopping veering detection test.")
    finally:
        lgpio.gpiochip_close(h)

if __name__ == "__main__":
    main()
