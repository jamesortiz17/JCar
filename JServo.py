import lgpio
from time import sleep

class JServo:
    def __init__(self, pin=15, frequency=50, tick=50):
        self.pin = pin
        self.frequency = frequency
        self.tick = tick
        self.middle_pulse = 1620
        self.maxleft_pulse = 2500
        self.maxright_pulse = 500
        self.pulse_width = self.middle_pulse

        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self.h, self.pin, 0)

        self.set_pulse(self.pulse_width)

    def pulse_to_dutycycle(self, pulse_us):
        period_us = 1_000_000 / self.frequency
        return (pulse_us / period_us) * 100

    def set_pulse(self, pulse_us):
        duty_cycle = self.pulse_to_dutycycle(pulse_us)
        lgpio.tx_pwm(self.h, self.pin, self.frequency, duty_cycle)

    def center(self):
        self.pulse_width = self.middle_pulse
        self.set_pulse(self.pulse_width)

    def turn_right(self):
        self.pulse_width = max(self.maxright_pulse, self.pulse_width - self.tick)
        self.set_pulse(self.pulse_width)

    def turn_left(self):
        self.pulse_width = min(self.maxleft_pulse, self.pulse_width + self.tick)
        self.set_pulse(self.pulse_width)

    def cleanup(self):
        self.center()
        sleep(0.5)
        lgpio.tx_pwm(self.h, self.pin, self.frequency, 0)
        lgpio.gpiochip_close(self.h)
        print("Servo cleanup complete")
