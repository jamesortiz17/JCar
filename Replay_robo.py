import json
from time import sleep, time
from foundations.Drive import Drive
from foundations.Encoder import DistanceEncoder

drive = Drive()
encoder = DistanceEncoder(drive.h)

with open('paths/robo.json', 'r') as f:
    path = json.load(f)

try:
    zero_heading = drive.gyro.get_relative_heading()

    for step in path:
        if step['action'] == 'forward':
            encoder.reset_counts()
            drive.forward()
            target_cm = step['distance_cm']
            start_time = time()
            while True:
                left, right = encoder.get_distances_cm()
                avg = (left + right) / 2

                # Maintain centered heading while moving forward
                drive.correct_heading_with_servo()

                if avg >= target_cm or time() - start_time > 10:
                    break
                sleep(0.01)
            drive.stop()
        elif step['action'] == 'turn':
            direction = step['direction']
            degrees = step['degrees']

            # Calculate target heading relative to zero_heading (replay resets zero_heading after each turn)
            if direction == 'right':
                target_heading = drive.gyro.normalize_angle(zero_heading + degrees)
            else:
                target_heading = drive.gyro.normalize_angle(zero_heading - degrees)

            print(f"Replaying turn right 90°, from zero reference heading 90.25° to target heading 90.00°")

            drive.turn_to(direction, degrees)

            # Reset zero heading after turn
            zero_heading = drive.gyro.get_relative_heading()
            drive.servo.center()
finally:
    drive.cleanup()

print("Replay complete.")
