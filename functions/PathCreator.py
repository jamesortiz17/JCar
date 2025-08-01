import sys
import os
import json
from time import sleep, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from foundations.Drive import Drive
from foundations.Encoder import DistanceEncoder

drive = Drive()
path = []

drive.servo.center()
sleep(1)

print("Starting path recording. Robot will drive forward. Enter 'L <deg>', 'R <deg>', or 'STOP'")

drive.encoder.reset_counts()
drive.forward()

# Initialize zero reference heading at start of run
zero_heading = drive.gyro.get_relative_heading()
driving_start_time = time()

try:
    while True:
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

                # Stop and record distance traveled before turn
                drive.stop()
                left_dist, right_dist = drive.encoder.get_distances_cm()
                avg_dist = (left_dist + right_dist) / 2
                path.append({"action": "forward", "distance_cm": avg_dist})

                # Calculate target heading relative to zero_heading
                if direction == "right":
                    target_heading = drive.gyro.normalize_angle(zero_heading + degrees)
                else:
                    target_heading = drive.gyro.normalize_angle(zero_heading - degrees)

                print(f"Turning {direction} from zero reference heading {zero_heading:.2f}° to target heading {target_heading:.2f}°")

                # Perform turn
                # Determine heading offset since gyro may already drifted before turn starts
                initial_drift = drive.gyro.angle_difference(drive.gyro.get_relative_heading(), zero_heading)

                # Adjust turn angle by subtracting the current offset
                adjusted_degrees = degrees - initial_drift if direction == "right" else degrees + initial_drift

                print(f"Adjusted turn: {degrees:.2f}° -> {adjusted_degrees:.2f}° (correction: {initial_drift:.2f}°)")
                drive.turn_to(direction, adjusted_degrees)


                # Reset zero reference heading after turn (simulate reset relative heading)
                zero_heading = drive.gyro.get_relative_heading()
                # If your gyro class supports reset, call it here, e.g.
                # drive.gyro.reset_relative_heading()

                # Log turn action with new zero heading
                path.append({
                    "action": "turn",
                    "direction": direction,
                    "degrees": degrees,
                    "start_heading": zero_heading,
                    "end_heading": zero_heading
                })

                # Reset encoder and servo, start moving forward again
                drive.encoder.reset_counts()
                drive.servo.center()
                drive.forward()
                driving_start_time = time()  # reset driving timer after turn
                continue

        else:
            # Maintain heading correction only if driving more than 2 seconds after last turn
            if time() - driving_start_time > 2:
                drive.correct_heading_with_servo()

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

# -------------------------------------
# Generate Replay File
# -------------------------------------

replay_script = f"""import json
from time import sleep, time
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

            print(f"Replaying turn {{direction}} {{degrees}}°, from zero reference heading {{zero_heading:.2f}}° to target heading {{target_heading:.2f}}°")

            drive.turn_to(direction, degrees)

            # Reset zero heading after turn (simulate relative heading reset)
            zero_heading = drive.gyro.get_relative_heading()
            # If your gyro class supports reset, call it here, e.g.
            # drive.gyro.reset_relative_heading()

            drive.servo.center()
finally:
    drive.cleanup()

print("Replay complete.")
"""

with open(f"Replay_{filename}.py", "w") as f:
    f.write(replay_script)

print(f"Replay script written to Replay_{filename}.py")
