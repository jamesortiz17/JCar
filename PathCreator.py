import json
import os
from time import sleep
from JMotor import JMotor
from JServo import JServo
from Encoder import DistanceEncoder

motor = JMotor()
servo = JServo()
encoder = DistanceEncoder()

path = []

print("Starting path recording. Robot will drive forward. Enter 'L <deg>', 'R <deg>', or 'STOP'")
motor.forward()
encoder.reset_counts()

try:
    while True:
        user_input = input("Command: ").strip().upper()

        if user_input == "STOP":
            motor.stop()
            left_dist, right_dist = encoder.get_distances_cm()
            avg_dist = (left_dist + right_dist) / 2
            path.append({"action": "forward", "distance_cm": avg_dist})
            break

        if user_input.startswith("L ") or user_input.startswith("R "):
            parts = user_input.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Invalid input. Use 'L 90' or 'R 45'")
                continue

            direction = "left" if parts[0] == "L" else "right"
            degrees = int(parts[1])

            # Stop and record forward distance
            motor.stop()
            left_dist, right_dist = encoder.get_distances_cm()
            avg_dist = (left_dist + right_dist) / 2
            path.append({"action": "forward", "distance_cm": avg_dist})

            # Turn and record
            motor.turn(direction, degrees)
            path.append({"action": "turn", "direction": direction, "degrees": degrees})

            # Reset encoder and servo
            encoder.reset_counts()
            servo.center()

            # Resume forward motion
            motor.forward()
        else:
            print("Unknown command. Use 'L <deg>', 'R <deg>', or 'STOP'")

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

# Auto-generate replay script
replay_script = f"""
from JMotor import JMotor
from JServo import JServo
from DistanceEncoder import DistanceEncoder
import json
from time import sleep

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
        while True:
            left, right = encoder.get_distances_cm()
            avg = (left + right) / 2
            if avg >= target_cm:
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
