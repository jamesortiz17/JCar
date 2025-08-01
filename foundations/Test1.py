import sys
import os
import json
import time
import math
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from foundations.Drive import Drive

def main():
    drive = Drive()
    path = []

    drive.servo.center()
    time.sleep(1)
    drive.encoder.reset_counts()
    drive.forward()

    heading_history = deque(maxlen=3)
    servo_offset = 0.0
    last_heading_error = 0.0
    last_correction_direction = 0

    print("Starting path recording. Enter 'L <deg>', 'R <deg>', or 'STOP'")

    zero_heading = drive.gyro.get_relative_heading()
    driving_start_time = time.time()

    try:
        while True:
            # Heading correction every loop
            raw_heading = drive.gyro.get_relative_heading()
            heading_history.append(raw_heading)
            heading = sum(heading_history) / len(heading_history)
            print(f"Relative Heading: {heading:.2f}°")

            deadband = 0.4
            max_offset = 300
            decay = 4.2
            min_pulse_step = 4
            max_servo_step = 10

            if abs(heading) > deadband:
                correction_direction = -1 if heading > 0 else 1
                error_increased = abs(heading) > abs(last_heading_error)

                if last_correction_direction != 0 and correction_direction != last_correction_direction and error_increased:
                    print("Correction direction reversed and error increased - backing off.")
                    servo_offset *= 0.7
                    pulse = drive.servo.set_offset(servo_offset)
                    print(f"Servo offset damped to {servo_offset:.1f}, pulse set to {pulse}")
                    last_correction_direction = 0
                    last_heading_error = heading
                else:
                    target_offset = correction_direction * (max_offset * (1 - math.exp(-abs(heading) / decay)))
                    delta = target_offset - servo_offset

                    if abs(delta) >= min_pulse_step:
                        delta = max(-max_servo_step, min(max_servo_step, delta))
                        servo_offset += delta
                        pulse = drive.servo.set_offset(servo_offset)
                        print(f"Applied delta: {delta:+.1f}, new servo pulse: {pulse}")
                        last_correction_direction = correction_direction
                    else:
                        print(f"Correction ({delta:+.1f}) too small to apply.")

                last_heading_error = heading

            user_input = input("Command: ").strip()
            parts = user_input.split()

            if len(parts) == 1 and parts[0].upper() == "STOP":
                drive.stop()
                left_dist, right_dist = drive.encoder.get_distances_cm()
                avg_dist = (left_dist + right_dist) / 2
                path.append({"action": "forward", "distance_cm": avg_dist})
                break

            if len(parts) == 2 and parts[1].isdigit():
                direction_input = parts[0].upper()
                if direction_input in ("L", "R"):
                    direction = "left" if direction_input == "L" else "right"
                    degrees = int(parts[1])

                    drive.stop()
                    left_dist, right_dist = drive.encoder.get_distances_cm()
                    avg_dist = (left_dist + right_dist) / 2
                    path.append({"action": "forward", "distance_cm": avg_dist})

                    initial_drift = drive.gyro.angle_difference(drive.gyro.get_relative_heading(), zero_heading)
                    adjusted_degrees = degrees - initial_drift if direction == "right" else degrees + initial_drift

                    print(f"Turning {direction} from {zero_heading:.2f}° by {degrees}° (adjusted: {adjusted_degrees:.2f}°)")
                    drive.turn_to(direction, adjusted_degrees)
                    zero_heading = drive.gyro.get_relative_heading()

                    path.append({
                        "action": "turn",
                        "direction": direction,
                        "degrees": degrees,
                        "start_heading": zero_heading,
                        "end_heading": zero_heading
                    })

                    drive.encoder.reset_counts()
                    drive.servo.center()
                    drive.forward()
                    driving_start_time = time.time()
                    continue

            print("Invalid input. Use 'L <deg>', 'R <deg>', or 'STOP'")

    except KeyboardInterrupt:
        print("\nInterrupted. Stopping robot.")
        drive.stop()

    drive.cleanup()

    filename = input("Enter a filename to save this path (no extension): ").strip()
    os.makedirs("paths", exist_ok=True)
    json_path = f"paths/{filename}.json"

    with open(json_path, "w") as f:
        json.dump(path, f, indent=4)

    print(f"Path saved to {json_path}")
    generate_replay_script(json_path, filename)

def generate_replay_script(json_path, filename):
    replay_script = f"""import json
import time
from foundations.Drive import Drive
from foundations.Encoder import DistanceEncoder

drive = Drive()
encoder = DistanceEncoder(drive.h)

with open('{json_path}', 'r') as f:
    path = json.load(f)

try:
    zero_heading = drive.gyro.get_relative_heading()

    for step in path:
        if step['action'] == 'forward':
            encoder.reset_counts()
            drive.forward()
            target_cm = step['distance_cm']
            start_time = time.time()
            driving_start_time = time.time()
            heading_history = []
            servo_offset = 0.0
            last_heading_error = 0.0
            last_correction_direction = 0

            while True:
                left, right = encoder.get_distances_cm()
                avg = (left + right) / 2
                raw_heading = drive.gyro.get_relative_heading()
                heading_history.append(raw_heading)
                if len(heading_history) > 3:
                    heading_history.pop(0)
                heading = sum(heading_history) / len(heading_history)

                if abs(heading) > 0.4:
                    correction_direction = -1 if heading > 0 else 1
                    error_increased = abs(heading) > abs(last_heading_error)
                    if last_correction_direction != 0 and correction_direction != last_correction_direction and error_increased:
                        servo_offset *= 0.7
                        drive.servo.set_offset(servo_offset)
                        last_correction_direction = 0
                    else:
                        target_offset = correction_direction * (300 * (1 - math.exp(-abs(heading) / 4.2)))
                        delta = target_offset - servo_offset
                        if abs(delta) >= 4:
                            delta = max(-10, min(10, delta))
                            servo_offset += delta
                            drive.servo.set_offset(servo_offset)
                            last_correction_direction = correction_direction
                    last_heading_error = heading

                if avg >= target_cm or time.time() - start_time > 10:
                    break
                time.sleep(0.075)
            drive.stop()

        elif step['action'] == 'turn':
            direction = step['direction']
            degrees = step['degrees']

            if direction == 'right':
                target_heading = drive.gyro.normalize_angle(zero_heading + degrees)
            else:
                target_heading = drive.gyro.normalize_angle(zero_heading - degrees)

            print(f"Replaying turn {{direction}} {{degrees}}°, from heading {{zero_heading:.2f}}° to {{target_heading:.2f}}°")
            drive.turn_to(direction, degrees)
            zero_heading = drive.gyro.get_relative_heading()
            drive.servo.center()
finally:
    drive.cleanup()

print("Replay complete.")"""

    with open(f"Replay_{filename}.py", "w") as f:
        f.write(replay_script)

    print(f"Replay script written to Replay_{filename}.py")

if __name__ == "__main__":
    main()
