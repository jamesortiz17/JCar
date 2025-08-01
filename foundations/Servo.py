import lgpio 
from time import sleep

class JServo:
    def __init__(self, h, pin=18, frequency=50):
        self.h = h
        self.pin = pin
        self.frequency = frequency
        self.middle_pulse = 1580
        self.maxleft_pulse = 2200
        self.maxright_pulse = 1020
        self.current_pulse = None
        lgpio.gpio_claim_output(self.h, self.pin, 0)
        self.center()
        self.current_offset = 0  # track current offset from center

    def pulse_to_dutycycle(self, pulse_us):
        period_us = 1_000_000 / self.frequency
        return 100 * pulse_us / period_us

    def set_offset(self, offset):
            """Set servo position relative to center pulse."""
            # clamp offset within servo limits relative to center
            max_left_offset = self.maxleft_pulse - self.middle_pulse
            max_right_offset = self.maxright_pulse - self.middle_pulse
            offset = max(min(offset, max_left_offset), max_right_offset)
            self.current_offset = offset
            self.adjust_to(offset)
            return self.middle_pulse + offset  # return actual pulse sent
            
    def set_pulse(self, pulse_us):
        if self.current_pulse == pulse_us:
            return  # Skip redundant write
        self.current_pulse = pulse_us
        duty_cycle = self.pulse_to_dutycycle(pulse_us)
        lgpio.tx_pwm(self.h, self.pin, self.frequency, duty_cycle)

    def center(self):
        self.set_pulse(self.middle_pulse)

    def slight_left(self):
        self.set_pulse(self.middle_pulse + 100)

    def slight_right(self):
        self.set_pulse(self.middle_pulse - 100)

    def turn_left(self):
        self.set_pulse(self.maxleft_pulse)

    def turn_right(self):
        self.set_pulse(self.maxright_pulse)

    def adjust_to(self, pulse_delta):
        target_pulse = self.middle_pulse + pulse_delta
        target_pulse = max(min(target_pulse, self.maxleft_pulse), self.maxright_pulse)
        print(f"Setting servo pulse to {target_pulse} (delta {pulse_delta})")
        self.set_pulse(target_pulse)



    def cleanup(self):
        self.center()
        sleep(0.5)
        lgpio.tx_pwm(self.h, self.pin, self.frequency, 0)
        lgpio.gpio_free(self.h, self.pin)