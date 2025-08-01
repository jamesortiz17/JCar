import json
from time import sleep, time
from foundations.Drive import Drive
from foundations.Encoder import DistanceEncoder

drive = Drive()
encoder = DistanceEncoder(drive.h)

with open('paths/night.json', 'r') as f:
    path = json.load(f)

try:
    zero_heading = drive.gyro.get_relative_heading()

    for step in path:
        if step['action'] == 'forward':
            encoder.reset_counts()
            drive.forward()
            target_cm = step['distance_cm']
            start_time = time()
            driving_start_time = time()

            while True:
                left, right = encoder.get_distances_cm()
                avg = (left + right) / 2

                # Only correct heading after 2 seconds of driving
                if time() - driving_start_time > 2:
                    drive.correct_heading_with_servo()

                if avg >= target_cm or time() - start_time > 10:
                    break
                sleep(0.01)
            drive.stop()

        elif step['action'] == 'turn':
            direction = step['direction']
            degrees = step['degrees']

            # Calculate target heading relative to zero_heading
            if direction == 'right':
                target_heading = drive.gyro.normalize_angle(zero_heading + degrees)
            else:
                target_heading = drive.gyro.normalize_angle(zero_heading - degrees)

            print(f"Replaying turn {direction} {degrees}°, from zero reference heading {zero_heading:.2f}° to target heading {target_heading:.2f}°")

            drive.turn_to(direction, degrees)

            # Reset zero heading after turn (simulate relative heading reset)
            zero_heading = drive.gyro.get_relative_heading()
            # If your gyro class supports reset, call it here, e.g.
            # drive.gyro.reset_relative_heading()

            drive.servo.center()
finally:
    drive.cleanup()

print("Replay complete.")
