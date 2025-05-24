import pigpio

COUNTS_PER_REV = 800
WHEEL_CIRCUMFERENCE = 0.26  # meters

class EncoderReader:
    def __init__(self, pi, left_pin_a=5, left_pin_b=6, right_pin_a=13, right_pin_b=19):
        self.pi = pi

        # Pins
        self.left_a = left_pin_a
        self.left_b = left_pin_b
        self.right_a = right_pin_a
        self.right_b = right_pin_b

        # Encoder counts
        self.left_count = 0
        self.right_count = 0
        self.direction_forward = True

        # Set pins as inputs with pull-ups
        for pin in [self.left_a, self.left_b, self.right_a, self.right_b]:
            self.pi.set_mode(pin, pigpio.INPUT)
            self.pi.set_pull_up_down(pin, pigpio.PUD_UP)

        # Setup callbacks on both edges of left and right A pins
        self.left_cb = self.pi.callback(self.left_a, pigpio.EITHER_EDGE, self._left_callback)
        self.right_cb = self.pi.callback(self.right_a, pigpio.EITHER_EDGE, self._right_callback)

    def _left_callback(self, gpio, level, tick):
        a = self.pi.read(self.left_a)
        b = self.pi.read(self.left_b)
        if a == b:
            self.left_count += 1 if self.direction_forward else -1
        else:
            self.left_count -= 1 if self.direction_forward else -1

    def _right_callback(self, gpio, level, tick):
        a = self.pi.read(self.right_a)
        b = self.pi.read(self.right_b)
        if a == b:
            self.right_count += 1 if self.direction_forward else -1
        else:
            self.right_count -= 1 if self.direction_forward else -1

    def set_direction(self, forward=True):
        self.direction_forward = forward

    def get_distances(self):
        left_rev = self.left_count / COUNTS_PER_REV
        right_rev = self.right_count / COUNTS_PER_REV
        return (left_rev * WHEEL_CIRCUMFERENCE, right_rev * WHEEL_CIRCUMFERENCE)

    def reset(self):
        self.left_count = 0
        self.right_count = 0

    def cleanup(self):
        self.left_cb.cancel()
        self.right_cb.cancel()
