from Servo import JServo
import lgpio
from time import sleep

def main():
    h = lgpio.gpiochip_open(0)
    servo = JServo(h)

    try:
        print("Turning right...")
        servo.turn_right()
        sleep(1)

        print("Centering...")
        servo.center()
        sleep(1)

        print("Turning left...")
        servo.turn_left()
        sleep(1)

        print("Centering...")
        servo.center()
        sleep(1)

    finally:
        print("Cleaning up and detaching servo...")
        servo.cleanup()
        lgpio.gpiochip_close(h)

if __name__ == "__main__":
    main()
