import lgpio
import time
from Encoder import EncoderReader  # Ensure Enc.py contains EncoderReader with .set_directions() and .cleanup()

class JMotor:
    def __init__(self):
        # Motor control pins
        self.INL1 = 17
        self.INL2 = 27
        self.ENL = 22
        self.INR1 = 20
        self.INR2 = 16
        self.ENR = 21

        # Open GPIO chip
        self.h = lgpio.gpiochip_open(0)

        # Set motor pins as outputs
        for pin in [self.INL1, self.INL2, self.ENL, self.INR1, self.INR2, self.ENR]:
            lgpio.gpio_claim_output(self.h, pin, 0)

        # Enable PWM at 30% duty cycle
        lgpio.tx_pwm(self.h, self.ENL, 1000, 30.0)
        lgpio.tx_pwm(self.h, self.ENR, 1000, 30.0)

        # Initialize encoder reader
        self.encoder = EncoderReader()

    def forward(self):
        # Set encoder directions forward
        self.encoder.set_direction(True)

        # Drive both motors forward
        lgpio.gpio_write(self.h, self.INL1, 1)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 1)
        lgpio.gpio_write(self.h, self.INR2, 0)

    def backward(self):
        # Set encoder directions backward
        self.encoder.set_direction(False)

        # Drive both motors backward
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 1)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 1)

    def cleanup(self):
        # Stop motors
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 0)

        # Stop PWM
        lgpio.tx_pwm(self.h, self.ENL, 0, 0.0)
        lgpio.tx_pwm(self.h, self.ENR, 0, 0.0)

        # Cleanup encoder
        self.encoder.cleanup()

        # Close GPIO chip
        lgpio.gpiochip_close(self.h)
