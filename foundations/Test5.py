import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'foundations')))

import time
from .Drive import Drive

def main():
    drive = Drive()
    drive.servo.center()
    drive.forward()

    print("Driving forward. Monitoring heading...")

    correction_pulse_amount = 15 # fixed servo pulse adjust amount
    correction_threshold = 1.0   # wider deadband to avoid constant flipping
    correction_cooldown = 2.0    # seconds between corrections
    last_correction_time = 0
    last_correction_direction = 0  # -1 for right, 1 for left, 0 none

    current_pulse_offset = 0  # track current servo pulse offset from center

    try:
        while True:
            heading = drive.gyro.get_relative_heading()
            print(f"Relative Heading: {heading:.2f}°")

            now = time.time()

            if abs(heading) > correction_threshold and (now - last_correction_time) > correction_cooldown:
                correction_direction = 1 if heading > 0 else -1

                # Update offset only if direction changed or no last correction
                if correction_direction != last_correction_direction:
                    print("Correction direction changed, resetting last correction direction")
                    # Optional: could reset offset or keep as is

                # Update current pulse offset (accumulate corrections)
                current_pulse_offset += correction_pulse_amount * correction_direction
                # Clamp to servo limits (optional, adjust as per your servo)
                max_offset = 600  # example limit, tune as needed
                current_pulse_offset = max(min(current_pulse_offset, max_offset), -max_offset)

                # Apply new pulse relative to center
                drive.servo.adjust_to(current_pulse_offset)

                print(f"Applied servo correction of {correction_pulse_amount * correction_direction}, total offset: {current_pulse_offset}")

                last_correction_time = now
                last_correction_direction = correction_direction

            elif abs(heading) <= correction_threshold:
                print("Heading within deadband, holding servo position.")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nInterrupted. Stopping and cleaning up.")
        drive.stop()
        drive.cleanup()

if __name__ == "__main__":
    main()
