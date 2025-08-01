import time
from Drive import Drive

def main():
    drive = Drive()
    try:
        print("Starting forward drive with auto-centering and veering correction...")
        drive.forward()

        run_time = 20  # seconds to run test
        start_time = time.time()

        while time.time() - start_time < run_time:
            drive.maintain_center(check_interval=0.2, max_correction_time=0.3)
            time.sleep(0.1)

        print("Test run complete. Stopping motors and cleaning up.")
        drive.stop()

    except KeyboardInterrupt:
        print("Interrupted by user. Stopping motors and cleaning up.")
        drive.stop()

    finally:
        drive.cleanup()

if __name__ == "__main__":
    main