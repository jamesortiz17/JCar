import lgpio
import time

class JDist:
    def __init__(self, trig, echo):
        self.TRIG = trig
        self.ECHO = echo

        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self.h, self.TRIG)
        lgpio.gpio_claim_input(self.h, self.ECHO)

    def read_distance(self):
        # Make sure trigger is low
        lgpio.gpio_write(self.h, self.TRIG, 0)
        time.sleep(0.002)

        # Send 10us pulse
        lgpio.gpio_write(self.h, self.TRIG, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(self.h, self.TRIG, 0)

        pulse_start = None
        pulse_end = None

        timeout = time.time() + 0.02  # 20ms timeout

        # Wait for echo to go HIGH
        while lgpio.gpio_read(self.h, self.ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                return -1

        timeout = time.time() + 0.02  # reset timeout

        # Wait for echo to go LOW
        while lgpio.gpio_read(self.h, self.ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                return -1

        if pulse_start is None or pulse_end is None:
            return -1  # invalid measurement

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # cm
        return round(distance, 2)

    def cleanup(self):
        lgpio.gpiochip_close(self.h)
