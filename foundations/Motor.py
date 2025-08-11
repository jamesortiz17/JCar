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

    def zigzag(self, max_speed=30, cycles=3, step_delay=0.05, step_size=2, forward=True):
        """
        Moves the robot in a zig-zag pattern by smoothly varying motor speeds.

        Args:
        max_speed (int): Maximum duty cycle percentage for either motor.
        cycles (int): Number of full oscillations (left+right turns).
        step_delay (float): Delay between each PWM adjustment.
        step_size (int): Change in duty cycle per step.
        forward (bool): True for forward motion, False for backward.
        """
        if max_speed <= 0 or max_speed > 100:
            raise ValueError("max_speed must be between 1 and 100")

        left_speed = max_speed
        right_speed = max_speed // 2

        for _ in range(cycles):
        # Shift to left turn
            while right_speed < max_speed:
                right_speed += step_size
                left_speed -= step_size
                self.set_left_motor(forward, max(0, min(max_speed, left_speed)))
                self.set_right_motor(forward, max(0, min(max_speed, right_speed)))
                time.sleep(step_delay)

        # Shift to right turn
            while left_speed < max_speed:
                left_speed += step_size
                right_speed -= step_size
                self.set_left_motor(forward, max(0, min(max_speed, left_speed)))
                self.set_right_motor(forward, max(0, min(max_speed, right_speed)))
                time.sleep(step_delay)

        self.stop()

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
      
