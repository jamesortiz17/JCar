import time
import lgpio
from collections import deque

class JDist:
    def __init__(self, h, front_pins, left_pins, right_pins):
        self.h = h
        self.sensors = {
            "front": {"trig": front_pins[0], "echo": front_pins[1], "history": deque(maxlen=5)},
            "left": {"trig": left_pins[0], "echo": left_pins[1], "history": deque(maxlen=5)},
            "right": {"trig": right_pins[0], "echo": right_pins[1], "history": deque(maxlen=5)}
        }
        for sensor in self.sensors.values():
            self._setup_sensor(sensor["trig"], sensor["echo"])

    def _setup_sensor(self, trig, echo):
        lgpio.gpio_claim_output(self.h, trig)
        lgpio.gpio_claim_input(self.h, echo)
        lgpio.gpio_write(self.h, trig, 0)
        time.sleep(0.05)

    def _read_distance(self, trig, echo):
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
        distance = pulse_duration * 17150
        return round(distance, 2)

    def update(self):
        for name, sensor in self.sensors.items():
            distance = self._read_distance(sensor["trig"], sensor["echo"])
            if distance is not None:
                sensor["history"].append(distance)

    def get_current_distances(self):
        return {
            name: sensor["history"][-1] if sensor["history"] else None
            for name, sensor in self.sensors.items()
        }

    def veering_trend(self, threshold=1.5):
        """Detect if there's a consistent trend of veering toward one side."""
        left = list(self.sensors["left"]["history"])
        right = list(self.sensors["right"]["history"])

        if len(left) < 3 or len(right) < 3:
            return None  # Not enough data

        # Compute average change across last few readings
        delta_left = left[-1] - left[0]
        delta_right = right[-1] - right[0]

        if delta_left < -threshold and delta_right > threshold:
            return "left"
        elif delta_right < -threshold and delta_left > threshold:
            return "right"
        return None

    def side_stable(self, tolerance=0.8):
        """Return True if both left and right readings have stabilized (i.e., no trend)."""
        left = list(self.sensors["left"]["history"])
        right = list(self.sensors["right"]["history"])

        if len(left) < 3 or len(right) < 3:
            return False

        def stable(d):
            diffs = [abs(d[i+1] - d[i]) for i in range(len(d)-1)]
            return max(diffs) < tolerance

        return stable(left) and stable(right)

    def get_history(self, sensor):
        return list(self.sensors[sensor]["history"]) if sensor in self.sensors else []
