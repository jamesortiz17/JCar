import lgpio
from time import sleep

# Setup servo parameters
PIN = 4
FREQUENCY = 50  # Hz for servo PWM
PERIOD_US = 1_000_000 / FREQUENCY  # microseconds per period

# Pulse widths for servo positions (in microseconds)
MIN_PULSE = 1000  # full right (1 ms)
MID_PULSE = 1500  # center (1.5 ms)
MAX_PULSE = 2000  # full left (2 ms)

def pulse_to_dutycycle(pulse_us):
    return (pulse_us / PERIOD_US) * 100

def test_servo():
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, PIN, 0)

    try:
        while True:
            print("Moving to full left")
            lgpio.tx_pwm(h, PIN, FREQUENCY, pulse_to_dutycycle(MAX_PULSE))
            sleep(2)

            print("Moving to center")
            lgpio.tx_pwm(h, PIN, FREQUENCY, pulse_to_dutycycle(MID_PULSE))
            sleep(2)

            print("Moving to full right")
            lgpio.tx_pwm(h, PIN, FREQUENCY, pulse_to_dutycycle(MIN_PULSE))
            sleep(2)

            print("Moving to center")
            lgpio.tx_pwm(h, PIN, FREQUENCY, pulse_to_dutycycle(MID_PULSE))
            sleep(2)

    except KeyboardInterrupt:
        print("Stopping servo test")

    finally:
        lgpio.tx_pwm(h, PIN, FREQUENCY, 0)  # Stop PWM
        lgpio.gpiochip_close(h)

if __name__ == "__main__":
    test_servo()
