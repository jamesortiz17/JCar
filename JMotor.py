import lgpio
import time
import statsmodels.api as sm
import numpy as np



class JMotor:
    def __init__(self):
        
        self.INL1 = 17
        self.INL2 = 27
        self.ENL = 22
        self.INR1 = 20
        self.INR2 = 16
        self.ENR = 21
        self.speed = 5 #set speed (1-10 > percent duty cycle*10)
        self.speed_ms = 11.33 # conversion factor
        self.current_dir = None 
        

        # Open GPIO chip
        self.h = lgpio.gpiochip_open(0)

        # Set motor pins as outputs
        for pin in [self.INL1, self.INL2, self.ENL, self.INR1, self.INR2, self.ENR]:
            lgpio.gpio_claim_output(self.h, pin, 0)

        # Enable PWM 
        self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, self.speed*10) 
        self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, self.speed*10)

     
    def set_speed(self, speed):
        self.speed = speed
        self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, self.speed*10) 
        self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, self.speed*10)


    def forward(self):
       
        lgpio.gpio_write(self.h, self.INL1, 1)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 1)
        lgpio.gpio_write(self.h, self.INR2, 0)
        
        self.current_dir = "forward"

    def backward(self):
        
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 1)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 1)
        
        self.current_dir = "backward"

    def instant_stop(self): 
        
        if self.current_dir == "forward":
            self.backward()

        elif self.current_dir == "backward":
            self.forward()
            
        else: 
            pass
            
        time.sleep(0.001*self.speed)
        self.stop()
        self.set_speed(0)



    def cleanup(self):
        # Stop motors
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 0)

        #Stop PWM
        lgpio.tx_pwm(self.h, self.ENL, 0, 0.0)
        lgpio.tx_pwm(self.h, self.ENR, 0, 0.0)

 # Close GPIO chip
        lgpio.gpiochip_close(self.h)

    def stop(self):
        # Stop motors
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 0)

def simulate(car, max_seconds=3):

    print("go forward")
    car.forward()
    time.sleep(max_seconds)
    print("done driving at speed", car.speed)

def run_tests(speeds, car, max_seconds=3):
    results = []
    print(f"Simulating each speed for {max_seconds} seconds...\n")
    for speed in speeds:
        print(f"Testing speed: {speed}")
        car.set_speed(speed)
        input("Press Enter to start driving...\n")
        simulate(car, max_seconds)
        car.instant_stop()
        results.append((speed, max_seconds))
        input("Press Enter to continue to the next speed...\n")
    return results

def prompt_user_for_distances(speeds):
    print("\nNow enter the real-world distances moved at each test speed.\n")
    distances = []
    for s in speeds:
        d = float(input(f"Distance travelled at speed {s}: "))
        distances.append(d)
    return distances

def estimate_base_speed(speeds, times, distances):
    rates = np.array(distances) / np.array(times)  # real units per second
    speeds = np.array(speeds)
    speeds_with_const = sm.add_constant(speeds)  # adds intercept term

    model = sm.OLS(rates, speeds_with_const).fit()

    base_units_per_second = model.params[1] * 1 + model.params[0]  # slope * 1 + intercept

    print(f"\nEstimated: speed = 1 corresponds to ~{base_units_per_second:.4f} real units/second.")
    print(model.summary())  # Optional: shows regression details

    return model


def main():
    
    car = JMotor()
    try:
        test_speeds = [1, 2, 3, 5]
        results = run_tests(test_speeds, car)

        input("\nPress Enter when ready to enter measured distances...\n")
        speeds = [r[0] for r in results]
        times = [r[1] for r in results]
        distances = prompt_user_for_distances(speeds)

        estimate_base_speed(speeds, times, distances)
    finally:
        print("done")
if __name__ == "__main__":
    main()