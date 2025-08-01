import json
from time import sleep, time
from foundations.Drive import Drive
from foundations.Encoder import DistanceEncoder

drive = Drive()
encoder = DistanceEncoder(drive.h)

with open('paths/testy.json', 'r') as f:
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
