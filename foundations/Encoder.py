import lgpio

class DistanceEncoder:
    def __init__(self, h,
                 r_pin_a=6, r_pin_b=5, l_pin_a=13, l_pin_b=12,
                 wheel_circumference_cm=28.8, counts_per_rev=1928):
        self.gpio = h

        self.r_pin_a = r_pin_a
        self.r_pin_b = r_pin_b
        self.l_pin_a = l_pin_a
        self.l_pin_b = l_pin_b

        self.right_count = 0
        self.left_count = 0

        self.wheel_circumference_cm = wheel_circumference_cm
        self.counts_per_rev = counts_per_rev

        # Claim inputs and alerts
        lgpio.gpio_claim_input(self.gpio, self.r_pin_a)
        lgpio.gpio_claim_input(self.gpio, self.r_pin_b)
        lgpio.gpio_claim_input(self.gpio, self.l_pin_a)
        lgpio.gpio_claim_input(self.gpio, self.l_pin_b)

        lgpio.gpio_claim_alert(self.gpio, self.r_pin_a, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.r_pin_b, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.l_pin_a, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.gpio, self.l_pin_b, lgpio.BOTH_EDGES)

        a = lgpio.gpio_read(self.gpio, self.r_pin_a)
        b = lgpio.gpio_read(self.gpio, self.r_pin_b)
        self._prev_right_state = (a << 1) | b

        a = lgpio.gpio_read(self.gpio, self.l_pin_a)
        b = lgpio.gpio_read(self.gpio, self.l_pin_b)
        self._prev_left_state = (a << 1) | b

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
        self.right_count += delta
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

    # New method to return updated distance for easy use externally
    def get_updated_distances(self):
        return self.get_distances_cm()

    def reset_counts(self):
        self.left_count = 0
        self.right_count = 0

    def close(self):
        self.cb_right_a.cancel()
        self.cb_right_b.cancel()
        self.cb_left_a.cancel()
        self.cb_left_b.cancel()
       
