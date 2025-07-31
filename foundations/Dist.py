import time
import lgpio
from collections import deque

class JDist:
    def __init__(self, h):
        self.h = h
        self.sensors = {
            "front": {"trig": 19, "echo": 26, "history": deque(maxlen=5)},
            "left":  {"trig": 25, "echo": 24, "history": deque(maxlen=5)},
            "right": {"trig": 23, "echo": 15, "history": deque(maxlen=5)}
        }
        self.claimed = set()
        self._setup_all_sensors()

    def _setup_all_sensors(self):
        for name, sensor in self.sensors.items():
            self._setup_sensor(sensor["trig"], sensor["echo"], name)

    def _setup_sensor(self, trig, echo, label):
        try:
            lgpio.gpio_claim_output(self.h, trig)
            self.claimed.add(trig)
        except lgpio.error:
            print(f"[Trig] GPIO {trig} busy — cannot claim for {label}")

        try:
            lgpio.gpio_claim_input(self.h, echo)
            self.claimed.add(echo)
        except lgpio.error:
            print(f"[Echo] GPIO {echo} busy — cannot claim for {label}")

        if trig in self.claimed:
            try:
                lgpio.gpio_write(self.h, trig, 0)
                time.sleep(0.05)
            except lgpio.error:
                print(f"GPIO {trig} write failed — possibly unclaimed")

    def _read_distance(self, trig, echo):
        if trig not in self.claimed or echo not in self.claimed:
            return None

        lgpio.gpio_write(self.h, trig, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(self.h, trig, 0)

        start = time.time()
        while lgpio.gpio_read(self.h, echo) == 0:
            if time.time() - start > 0.02:
                return None
        pulse_start = time.time()

        while lgpio.gpio_read(self.h, echo) == 1:
            if time.time() - pulse_start > 0.04:
                return None
        pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        return round(pulse_duration * 17150, 2)

    def update(self):
        for name, sensor in self.sensors.items():
            dist = self._read_distance(sensor["trig"], sensor["echo"])
            if dist is not None:
                sensor["history"].append(dist)

    def get_current_distances(self):
        return {
            name: (sensor["history"][-1] if sensor["history"] else None)
            for name, sensor in self.sensors.items()
        }

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
