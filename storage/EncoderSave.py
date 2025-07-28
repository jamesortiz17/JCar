# Encoder.py

import lgpio

class DistanceEncoder:
    def __init__(self, r_pin_a=5, r_pin_b=6, l_pin_a=12, l_pin_b=13):
        self.gpio = lgpio.gpiochip_open(0)

        self.r_pin_a = r_pin_a
        self.r_pin_b = r_pin_b
        self.l_pin_a = l_pin_a
        self.l_pin_b = l_pin_b

        self.right_count = 0
        self.left_count = 0

        # Claim inputs
        lgpio.gpio_claim_input(self.gpio, self.r_pin_a)
        lgpio.gpio_claim_input(self.gpio, self.r_pin_b)
        lgpio.gpio_claim_input(self.gpio, self.l_pin_a)
        lgpio.gpio_claim_input(self.gpio, self.l_pin_b)

        # Claim alerts (correct constant name!)
        lgpio.gpio_claim_alert(self.gpio, self.r_pin_a, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.l_pin_a, lgpio.BOTH_EDGES)

        # Register callbacks (correct function and arguments)
        self.cb_right = lgpio.callback(self.gpio, self.r_pin_a, lgpio.BOTH_EDGES, self._right_callback)
        self.cb_left = lgpio.callback(self.gpio, self.l_pin_a, lgpio.BOTH_EDGES, self._left_callback)

    def _right_callback(self, chip, gpio, level, tick):
        a = lgpio.gpio_read(self.gpio, self.r_pin_a)
        b = lgpio.gpio_read(self.gpio, self.r_pin_b)
        if a == b:
            self.right_count += 1
        else:
            self.right_count -= 1

    def _left_callback(self, chip, gpio, level, tick):
        a = lgpio.gpio_read(self.gpio, self.l_pin_a)
        b = lgpio.gpio_read(self.gpio, self.l_pin_b)
        if a == b:
            self.left_count += 1
        else:
            self.left_count -= 1

    def get_counts(self):
        return self.left_count, self.right_count

    def reset_counts(self):
        self.left_count = 0
        self.right_count = 0

    def close(self):
        self.cb_right.cancel()
        self.cb_left.cancel()
        lgpio.gpiochip_close(self.gpio)
        
import lgpio

class DistanceEncoder:
    def __init__(self, r_pin_a=5, r_pin_b=6, l_pin_a=13, l_pin_b=12,
                 wheel_circumference_cm=0.00000028, counts_per_rev= 700):
        self.gpio = lgpio.gpiochip_open(0)

        self.r_pin_a = r_pin_a
        self.r_pin_b = r_pin_b
        self.l_pin_a = l_pin_a
        self.l_pin_b = l_pin_b

        self.right_count = 0
        self.left_count = 0

        self.wheel_circumference_cm = wheel_circumference_cm
        self.counts_per_rev = counts_per_rev

        # Claim inputs
        lgpio.gpio_claim_input(self.gpio, self.r_pin_a)
        lgpio.gpio_claim_input(self.gpio, self.r_pin_b)
        lgpio.gpio_claim_input(self.gpio, self.l_pin_a)
        lgpio.gpio_claim_input(self.gpio, self.l_pin_b)

        # Claim alerts for both A and B pins
        lgpio.gpio_claim_alert(self.gpio, self.r_pin_a, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.r_pin_b, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.l_pin_a, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.l_pin_b, lgpio.BOTH_EDGES)

        # Initialize previous states
        a = lgpio.gpio_read(self.gpio, self.r_pin_a)
        b = lgpio.gpio_read(self.gpio, self.r_pin_b)
        self._prev_right_state = (a << 1) | b

        a = lgpio.gpio_read(self.gpio, self.l_pin_a)
        b = lgpio.gpio_read(self.gpio, self.l_pin_b)
        self._prev_left_state = (a << 1) | b

        # Register callbacks on both A and B pins
        self.cb_right_a = lgpio.callback(self.gpio, self.r_pin_a, lgpio.BOTH_EDGES, self._right_callback)
        self.cb_right_b = lgpio.callback(self.gpio, self.r_pin_b, lgpio.BOTH_EDGES, self._right_callback)

        self.cb_left_a = lgpio.callback(self.gpio, self.l_pin_a, lgpio.BOTH_EDGES, self._left_callback)
        self.cb_left_b = lgpio.callback(self.gpio, self.l_pin_b, lgpio.BOTH_EDGES, self._left_callback)

    def _decode_quadrature(self, prev, current):
        lookup = {
            (0, 1): 1,
            (1, 3): 1,
            (3, 2): 1,
            (2, 0): 1,
            (1, 0): -1,
            (3, 1): -1,
            (2, 3): -1,
            (0, 2): -1,
        }
        return lookup.get((prev, current), 0)

    def _right_callback(self, chip, gpio, level, tick):
        a = lgpio.gpio_read(self.gpio, self.r_pin_a)
        b = lgpio.gpio_read(self.gpio, self.r_pin_b)
        current_state = (a << 1) | b
        delta = self._decode_quadrature(self._prev_right_state, current_state)
        self.right_count -= delta  # direction fix
        self._prev_right_state = current_state

    def _left_callback(self, chip, gpio, level, tick):
        a = lgpio.gpio_read(self.gpio, self.l_pin_a)
        b = lgpio.gpio_read(self.gpio, self.l_pin_b)
        current_state = (a << 1) | b
        delta = self._decode_quadrature(self._prev_left_state, current_state)
        self.left_count += delta
        self._prev_left_state = current_state

    def get_counts(self):
        return self.left_count, self.right_count

    def get_distances_cm(self):
        left_distance = (self.left_count / self.counts_per_rev) * self.wheel_circumference_cm
        right_distance = (self.right_count / self.counts_per_rev) * self.wheel_circumference_cm
        return left_distance, right_distance

    def reset_counts(self):
        self.left_count = 0
        self.right_count = 0

    def close(self):
        self.cb_right_a.cancel()
        self.cb_right_b.cancel()
        self.cb_left_a.cancel()
        self.cb_left_b.cancel()
        lgpio.gpiochip_close(self.gpio)

