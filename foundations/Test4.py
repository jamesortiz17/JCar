import sys
import os
import time
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'foundations')))
from .Drive import Drive

def main():
    drive = Drive()
    drive.servo.center()
    time.sleep(1)
    drive.servo.center()
    drive.forward()
    
    

    print("Driving forward. Monitoring heading...")

    correction_pulse_amount = 8       # fixed servo pulse adjust amount
    correction_threshold = 1.0           # deadband for heading
    correction_cooldown = 1.5           # minimum seconds between corrections
    history_length = 5                   # number of past readings to track
    min_heading_improvement_per_reading = 0.02  # degrees toward center per reading

    last_correction_time = 0
    last_correction_direction = 0  # -1 for right, 1 for left, 0 none
    current_pulse_offset = 0       # track cumulative pulse offset from center

    heading_history = deque(maxlen=history_length)


    try:
        while True:
            heading = drive.gyro.get_relative_heading()
            print(f"Relative Heading: {heading:.2f}°")

            now = time.time()
            heading_history.append(heading)

            def is_heading_correcting():
                if len(heading_history) < 2:
                    return False  # not enough data
                diffs = [
                    abs(heading_history[i]) - abs(heading_history[i + 1])
                    for i in range(len(heading_history) - 1)
                ]
                avg_improvement = sum(diffs) / len(diffs)
                print(f"Avg improvement per reading: {avg_improvement:.3f}")
                return avg_improvement >= min_heading_improvement_per_reading

            if abs(heading) > correction_threshold:
                if (now - last_correction_time) > correction_cooldown:
                    if is_heading_correcting():
                        print("Heading correcting itself, skipping servo adjustment.")
                    else:
                        correction_direction = 1 if heading > 0 else -1

                        if correction_direction != last_correction_direction:
                            print("Correction direction changed, resetting last correction direction")

                        current_pulse_offset += correction_pulse_amount * correction_direction
                        max_offset = 600  # tune this for your servo
                        current_pulse_offset = max(min(current_pulse_offset, max_offset), -max_offset)

                        drive.servo.adjust_to(current_pulse_offset)
                        print(f"Applied servo correction of {correction_pulse_amount * correction_direction}, total offset: {current_pulse_offset}")

                        last_correction_time = now
                        last_correction_direction = correction_direction
            else:
                print("Heading within deadband, holding servo position.")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nInterrupted. Stopping and cleaning up.")
        drive.stop()
        drive.cleanup()

if __name__ == "__main__":
    main()
