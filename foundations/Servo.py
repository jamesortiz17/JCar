import lgpio
from time import sleep

class JServo:
    def __init__(self, h, pin=18, frequency=50):
        self.h = h
        self.pin = pin
        self.frequency = frequency
        self.middle_pulse = 1610
        self.maxleft_pulse = 2200
        self.maxright_pulse = 1020

        lgpio.gpio_claim_output(self.h, self.pin, 0)
        self.center()

    def pulse_to_dutycycle(self, pulse_us):
        period_us = 1_000_000 / self.frequency
        return (pulse_us / period_us) * 100

    def set_pulse(self, pulse_us):
        duty_cycle = self.pulse_to_dutycycle(pulse_us)
        lgpio.tx_pwm(self.h, self.pin, self.frequency, duty_cycle)

    def center(self):
        self.set_pulse(self.middle_pulse)

    def turn_right(self):
        self.set_pulse(self.maxright_pulse)

    def turn_left(self):
        self.set_pulse(self.maxleft_pulse)

    def cleanup(self):
        self.center()
        sleep(0.5)
        lgpio.tx_pwm(self.h, self.pin, self.frequency, 0)
