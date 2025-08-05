import lgpio
import time

class JMotor:
    def __init__(self, h):
        self.h = h
        self.INL1 = 17 # GPIO pins 
        self.INL2 = 27
        self.ENL = 22
        self.INR1 = 20
        self.INR2 = 16
        self.ENR = 21
        self.speed = 15  # percent duty cycle
        self.current_dir = None

        for pin in [self.INL1, self.INL2, self.ENL, self.INR1, self.INR2, self.ENR]:
            lgpio.gpio_claim_output(self.h, pin, 0)

        lgpio.tx_pwm(self.h, self.ENL, 1000, 0)
        lgpio.tx_pwm(self.h, self.ENR, 1000, 0)

    def set_speed(self, speed):
        self.speed = speed
        lgpio.tx_pwm(self.h, self.ENL, 1000, self.speed)
        lgpio.tx_pwm(self.h, self.ENR, 1000, self.speed)

    def set_left_motor(self, forward, duty):
        lgpio.gpio_write(self.h, self.INL1, 1 if forward else 0)
        lgpio.gpio_write(self.h, self.INL2, 0 if forward else 1)
        lgpio.tx_pwm(self.h, self.ENL, 1000, duty)

    def set_right_motor(self, forward, duty):
        lgpio.gpio_write(self.h, self.INR1, 1 if forward else 0)
        lgpio.gpio_write(self.h, self.INR2, 0 if forward else 1)
        lgpio.tx_pwm(self.h, self.ENR, 1000, duty)

    def forward(self):
        self.set_left_motor(True, self.speed)
        self.set_right_motor(True, self.speed)
        self.current_dir = "forward"

    def backward(self):
        self.set_left_motor(False, self.speed)
        self.set_right_motor(False, self.speed)
        self.current_dir = "backward"

    def instant_stop(self):
        if self.current_dir == "forward":
            self.backward()
        elif self.current_dir == "backward":
            self.forward()
        time.sleep(0.01 * self.speed)
        self.stop()
        self.set_speed(0)

    def stop(self):
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 0)
        lgpio.tx_pwm(self.h, self.ENL, 1000, 0)
        lgpio.tx_pwm(self.h, self.ENR, 1000, 0)
        self.current_dir = None

    def cleanup(self):
        self.stop()
      
