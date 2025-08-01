from Drive import Drive
import time
from collections import deque

def main():
    drive = Drive()

    trend_history = deque(maxlen=5)
    repeat_required = 2
    last_direction = None
    last_correct_time = 0
    correction_duration = 0.5  # seconds to hold correction before allowing change

    try:
        print("Starting forward drive with stabilized auto-steering (Ctrl+C to stop)...")
        drive.motor.forward()

        while True:
            drive.dist.update()
            trend = drive.dist.veering_trend()

            # Append current trend (can be None)
            trend_history.append(trend)

            now = time.time()
            left_count = trend_history.count("left")
            right_count = trend_history.count("right")

            # Decide correction based on consistent veering
            if left_count >= repeat_required:
                # Only apply new correction if direction changed or cooldown elapsed
                if last_direction != "left" or now - last_correct_time > correction_duration:
                    drive.servo.slight_right()
                    last_direction = "left"
                    last_correct_time = now
                    print("⬅Consistent left veer — correcting right")

            elif right_count >= repeat_required:
                if last_direction != "right" or now - last_correct_time > correction_duration:
                    drive.servo.slight_left()
                    last_direction = "right"
                    last_correct_time = now
                    print("Consistent right veer — correcting left")

            else:
                # If no consistent veering and cooldown elapsed, center servo
                if last_direction is not None and now - last_correct_time > correction_duration:
                    drive.servo.center()
                    last_direction = None
                    print(" Centered — no consistent veer")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")

    finally:
        drive.motor.stop()
        drive.cleanup()

if __name__ == "__main__":
    main()
