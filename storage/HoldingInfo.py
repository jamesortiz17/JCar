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

   def veering_trend(self, threshold=0.15, max_jump=3.0):
        left_hist = list(self.sensors["left"]["history"])
        right_hist = list(self.sensors["right"]["history"])

        if len(left_hist) < 3 or len(right_hist) < 3:
            return None

        left_diffs = [left_hist[i+1] - left_hist[i] for i in range(len(left_hist)-1)]
        right_diffs = [right_hist[i+1] - right_hist[i] for i in range(len(right_hist)-1)]

        if any(abs(d) > max_jump for d in left_diffs + right_diffs):
            return None  # Ignore big jumps

        avg_left_change = sum(left_diffs) / len(left_diffs)
        avg_right_change = sum(right_diffs) / len(right_diffs)

        print(f"Avg left change: {avg_left_change:.2f}, Avg right change: {avg_right_change:.2f}")

        # Detect veering if left and right change oppositely *and* magnitude difference is within 0.2 of each other
        if (avg_left_change > threshold and avg_right_change < -threshold
            and abs(abs(avg_left_change) - abs(avg_right_change)) < 0.2):
            return "right"

        if (avg_left_change < -threshold and avg_right_change > threshold
            and abs(abs(avg_left_change) - abs(avg_right_change)) < 0.2):
            return "left"

        return None



    def side_stable(self, tolerance=0.5):
        left = list(self.sensors["left"]["history"])
        right = list(self.sensors["right"]["history"])

        if len(left) < 3 or len(right) < 3:
            return False

        def is_stable(seq):
            return max(abs(seq[i+1] - seq[i]) for i in range(len(seq)-1)) < tolerance

        return is_stable(left) and is_stable(right)

    def get_history(self, sensor):
        return list(self.sensors[sensor]["history"]) if sensor in self.sensors else []

    def wait_if_obstacle_ahead(self, threshold=30.0, confirm_readings=1, jitter_tolerance=2.0):
        
        consistent = 0
        last_dist = None

        while True:
            dist = self._read_distance(self.sensors["front"]["trig"], self.sensors["front"]["echo"])

            if dist is None:
                consistent = 0
                last_dist = None
                continue

            self.sensors["front"]["history"].append(dist)

            if dist < threshold:
                if last_dist is None or abs(dist - last_dist) < jitter_tolerance:
                    consistent += 1
                else:
                    consistent = 0
                last_dist = dist

                if consistent >= confirm_readings:
                    break
            else:
                return  

        # Once confirmed, stay in this loop until object clears
        while True:
            dist = self._read_distance(self.sensors["front"]["trig"], self.sensors["front"]["echo"])
            if dist is not None and dist > threshold + jitter_tolerance:
                return
            time.sleep(0.05)
