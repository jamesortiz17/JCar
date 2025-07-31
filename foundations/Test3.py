from Drive import Drive
import time

def main():
    drive = Drive()
    drive.servo.center()
    print("Servo centered.")

    try:
        print("Starting forward drive with auto-steering and obstacle check (Ctrl+C to stop)...")

        drive.motor.forward()

        # Tracking veer state
        veer_trend = None
        veer_count = 0
        stable_count = 0
        VEER_THRESHOLD = 3       # How many consistent veer readings before steering
        STABLE_THRESHOLD = 2  # How many stable readings before re-centering

        while True:
    
            # Update sensor readings
            drive.dist.update()

            # Get veering direction (no more hallway check!)
            current_trend = drive.dist.veering_trend()

            # Debug print (optional)
            print(f"Veering trend: {current_trend}")

            if current_trend == veer_trend and current_trend is not None:
                veer_count += 1
                stable_count = 0
            elif current_trend is None:
                stable_count += 1
                veer_count = 0
            else:
                veer_trend = current_trend
                veer_count = 1
                stable_count = 0

            # Apply correction
            if veer_count >= VEER_THRESHOLD:
                print(f"Veering {veer_trend}. Applying correction.")
                if veer_trend == "left":
                    drive.servo.slight_left()
                elif veer_trend == "right":
                    drive.servo.slight_right()

            # Reset to center if stable
            if stable_count >= STABLE_THRESHOLD:
                print("Stable path detected. Re-centering steering.")
                drive.servo.center()
                veer_trend = None
                veer_count = 0
                stable_count = 0

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")

    finally:
        drive.motor.stop()
        drive.cleanup()

if __name__ == "__main__":
    main()
