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

print("Starting path recording. Robot will drive forward. Enter 'l <deg>', 'r <deg>', or 'stop'")

drive.encoder.reset_counts()

# Preload distance sensor history before starting
for _ in range(3):
    drive.dist.update()
    sleep(0.05)

drive.forward()
driving_start_time = time()

try:
    while True:
        user_input = input("Command: ").strip()
        parts = user_input.split()

        if len(parts) == 1 and parts[0].lower() == "stop":
            drive.stop()
            left_dist, right_dist = drive.encoder.get_distances_cm()
            avg_dist = (left_dist + right_dist) / 2
            path.append({"action": "forward", "distance_cm": avg_dist})
            break

        if len(parts) == 2 and parts[1].isdigit():
            direction_input = parts[0].lower()
            if direction_input in ("l", "r"):
                direction = "left" if direction_input == "l" else "right"
                degrees = int(parts[1])

                drive.stop()
                left_dist, right_dist = drive.encoder.get_distances_cm()
                avg_dist = (left_dist + right_dist) / 2
                path.append({"action": "forward", "distance_cm": avg_dist})

                drive.turn_to(direction, degrees)

                path.append({
                    "action": "turn",
                    "direction": direction,
                    "degrees": degrees
                })

                drive.encoder.reset_counts()
                drive.servo.center()
                drive.forward()

                # Reset drive time after turn
                driving_start_time = time()
                continue

        print("Invalid input. Use 'l <deg>', 'r <deg>', or 'stop'")

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
dist_sensors = drive.dist

# Preload distance sensor history
for _ in range(3):
    dist_sensors.update()
    sleep(0.05)

with open('{json_path}', 'r') as f:
    path = json.load(f)

try:
    for step in path:
        if step['action'] == 'forward':
            encoder.reset_counts()
            drive.forward()
            target_cm = step['distance_cm']
            start_time = time()

            consecutive_below_10 = 0

            while True:
                left, right = encoder.get_distances_cm()
                avg = (left + right) / 2

                dist_sensors.update()
                dists = dist_sensors.get_current_distances()

                if any(d is not None and d < 10 for d in dists.values()):
                    consecutive_below_10 += 1
                else:
                    consecutive_below_10 = 0

                if consecutive_below_10 >= 2:
                    print("Obstacle detected. Pausing...")
                    drive.stop()

                    while True:
                        dist_sensors.update()
                        dists_clear = dist_sensors.get_current_distances()
                        if all(d is not None and d > 10 for d in dists_clear.values()):
                            print("Obstacle cleared. Resuming.")
                            drive.forward()
                            consecutive_below_10 = 0
                            break
                        sleep(0.1)

                if avg >= target_cm or time() - start_time > 10:
                    break
                sleep(0.01)

            drive.stop()

        elif step['action'] == 'turn':
            direction = step['direction']
            degrees = step['degrees']

            print(f"Turning {{direction}} {{degrees}}°")
            drive.turn_to(direction, degrees)
            drive.servo.center()

finally:
    drive.cleanup()

print("Replay complete.")
"""

with open(f"Replay_{filename}.py", "w") as f:
    f.write(replay_script)

print(f"Replay script written to Replay_{filename}.py")
