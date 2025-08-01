import sys
import os
import json
from time import sleep
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

try:
    while True:
        # Removed veering correction calls here

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

                start_heading = drive.gyro.get_relative_heading()
                drive.turn_to(direction, degrees)
                end_heading = drive.gyro.get_relative_heading()

                path.append({
                    "action": "turn",
                    "direction": direction,
                    "degrees": degrees,
                    "start_heading": start_heading,
                    "end_heading": end_heading
                })

                drive.encoder.reset_counts()
                drive.servo.center()
                drive.forward()
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
    for step in path:
        if step['action'] == 'forward':
            encoder.reset_counts()
            drive.forward()
            target_cm = step['distance_cm']
            start_time = time()
            while True:
                left, right = encoder.get_distances_cm()
                avg = (left + right) / 2
                # No maintain_center call here
                if avg >= target_cm or time() - start_time > 10:
                    break
                sleep(0.01)
            drive.stop()
        elif step['action'] == 'turn':
            drive.turn_to(step['direction'], step['degrees'])
            drive.servo.center()
finally:
    drive.cleanup()

print("Replay complete.")
"""

with open(f"Replay_{filename}.py", "w") as f:
    f.write(replay_script)

print(f"Replay script written to Replay_{filename}.py")
