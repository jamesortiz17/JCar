import json
import os
from time import sleep
from JMotor import JMotor
from JServo import JServo
from Encoder import DistanceEncoder
from Gyro import Gyro  # Only used to record heading before/after turn

motor = JMotor()
servo = JServo()
encoder = DistanceEncoder()
gyro = Gyro()

path = []

print("Starting path recording. Robot will drive forward. Enter 'L <deg>', 'R <deg>', or 'STOP'")
motor.forward()
encoder.reset_counts()
servo.center()

try:
    while True:
        user_input = input("Command: ").strip()
        parts = user_input.split()

        if len(parts) == 1 and parts[0].upper() == "STOP":
            motor.stop()
            left_dist, right_dist = encoder.get_distances_cm()
            avg_dist = (left_dist + right_dist) / 2
            path.append({"action": "forward", "distance_cm": avg_dist})
            break

        if len(parts) == 2 and parts[1].isdigit():
            direction_input = parts[0].upper()
            if direction_input in ("L", "R"):
                direction = "left" if direction_input == "L" else "right"
                degrees = int(parts[1])

                # Stop and record forward distance
                motor.stop()
                left_dist, right_dist = encoder.get_distances_cm()
                avg_dist = (left_dist + right_dist) / 2
                path.append({"action": "forward", "distance_cm": avg_dist})

                # Record heading before turn
                start_heading = gyro.euler_heading()

                # Perform turn (this includes gyro feedback)
                motor.turn(direction, degrees)

                # Record heading after turn
                end_heading = gyro.euler_heading()

                path.append({
                    "action": "turn",
                    "direction": direction,
                    "degrees": degrees,
                    "start_heading": start_heading,
                    "end_heading": end_heading
                })

                encoder.reset_counts()
                servo.center()
                motor.forward()
                continue

        print("Invalid input. Use 'L <deg>', 'R <deg>', or 'STOP'")

except KeyboardInterrupt:
    print("\nInterrupted. Stopping robot.")

motor.stop()
servo.center()
motor.cleanup()
servo.cleanup()
encoder.close()

filename = input("Enter a filename to save this path (no extension): ").strip()
os.makedirs("paths", exist_ok=True)
json_path = f"paths/{filename}.json"

with open(json_path, "w") as f:
    json.dump(path, f, indent=4)

print(f"Path saved to {json_path}")

# Auto-generate replay script with timeout
replay_script = f"""
from JMotor import JMotor
from JServo import JServo
from DistanceEncoder import DistanceEncoder
import json
from time import sleep, time

motor = JMotor()
servo = JServo()
encoder = DistanceEncoder()

with open('{json_path}', 'r') as f:
    path = json.load(f)

for step in path:
    if step['action'] == 'forward':
        encoder.reset_counts()
        motor.forward()
        target_cm = step['distance_cm']
        start_time = time()
        while True:
            left, right = encoder.get_distances_cm()
            avg = (left + right) / 2
            if avg >= target_cm or time() - start_time > 10:
                break
            sleep(0.01)
        motor.stop()
    elif step['action'] == 'turn':
        motor.turn(step['direction'], step['degrees'])
        servo.center()

motor.cleanup()
servo.cleanup()
encoder.close()
print("Replay complete.")
"""

with open(f"Replay_{filename}.py", "w") as f:
    f.write(replay_script)

print(f"Replay script written to Replay_{filename}.py")
