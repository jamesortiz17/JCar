import time
import lgpio
from collections import deque

class JDist:
    def __init__(self, h):
        self.h = h
        self.sensors = {
            "front": {"trig": 19, "echo": 26, "history": deque(maxlen=5)},
            "left":  {"trig": 25, "echo": 24, "history": deque(maxlen=10)},
            "right": {"trig": 23, "echo": 15, "history": deque(maxlen=10)}
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


  