import time
from JMotor import JMotor
from Encoder import DistanceEncoder
from JServo import JServo
from Gyro import Gyro

def main():
    print("Initializing components...")

    # Init gyro WITHOUT waiting for calibration
    gyro = Gyro(wait_for_calibration=False)
    initial_heading = gyro.euler_heading()
    print(f"Initial heading: {initial_heading:.2f}°")

    # Init and center servo (pin 15, per your JServo code)
    servo = JServo(pin=15)
    servo.center()
    print("Servo centered to 90° (middle position)")

    # Init motors and encoder
    motor = JMotor()
    encoder = DistanceEncoder()

    try:
        print("Starting motors forward at 40% speed...")
        motor.set_speed(40)
        motor.forward()

        # Run motors for 5 seconds
        time.sleep(3)

        motor.stop()
        print("Motors stopped.")

        # Get distances
        left_dist, right_dist = encoder.get_updated_distances()
        print(f"Final Distances After 5s:\nLeft:  {left_dist:.2f} cm\nRight: {right_dist:.2f} cm")

        final_heading = gyro.euler_heading()
        print(f"Final heading: {final_heading:.2f}°")

        heading_diff = final_heading - initial_heading
        print(f"Heading change during run: {heading_diff:.2f}°")

        if abs(heading_diff) > 2.0:
            print("Warning: Robot veered during movement (heading changed).")

    finally:
        motor.cleanup()
        encoder.close()
        servo.cleanup()
        print("Cleaned up GPIO and PWM.")

if __name__ == "__main__":
    main()
