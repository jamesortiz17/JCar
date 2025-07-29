import json
import time
from foundations.Drive import drive_cm
from foundatins.Gyro import turn_to

# --- MAIN REPLAYER ---
def replay_path():
    name = input("Enter path file name (no .json): ").strip()
    filename = f"paths/{name}.json"

    try:
        with open(filename, 'r') as f:
            path = json.load(f)
    except FileNotFoundError:
        print(f"Path file '{filename}' not found.")
        return

    print(f"Replaying path: {filename}")

    for i, step in enumerate(path):
        action = step["action"]

        if action == "forward":
            dist = step["distance_cm"]
            print(f"Step {i+1}: Drive {dist:.1f} cm forward")
            drive_cm(dist)

        elif action == "turn":
            direction = step["direction"]
            angle = step["angle"]
            print(f"Step {i+1}: Turn {direction.upper()} {angle:.1f}°")

            # Use +angle for right, -angle for left
            if direction.lower() == "right":
                turn_to(angle)
            elif direction.lower() == "left":
                turn_to(-angle)

        time.sleep(0.5)

    print("\nPath complete.")

if __name__ == "__main__":
    replay_path()
