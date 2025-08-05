import json
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

with open('paths/runnn.json', 'r') as f:
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

            print(f"Turning {direction} {degrees}°")
            drive.turn_to(direction, degrees)
            drive.servo.center()

finally:
    drive.cleanup()

print("Replay complete.")
