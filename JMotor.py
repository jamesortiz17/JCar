import lgpio
import time
from Gyro import Gyro

class JMotor:
    def __init__(self):
        
        self.INL1 = 17
        self.INL2 = 27
        self.ENL = 22
        self.INR1 = 20
        self.INR2 = 16
        self.ENR = 21
        self.speed = 40 #percent duty cycle
        self.speed_ms = 1.2 # conversion factor
        self.current_dir = None 
        
        
        # Open GPIO chip
        self.h = lgpio.gpiochip_open(0)

        # Set motor pins as outputs
        for pin in [self.INL1, self.INL2, self.ENL, self.INR1, self.INR2, self.ENR]:
            lgpio.gpio_claim_output(self.h, pin, 0)

        # Enable PWM 
        self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, self.speed) 
        self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, self.speed)

        self.gyro = Gyro()
     
    def set_speed(self, speed):
        self.speed = speed
        self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, self.speed) 
        self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, self.speed)


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
            
        time.sleep(0.01*self.speed)
        self.stop()
        self.set_speed(0)



    def cleanup(self):
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 0)

        #stop PWM
        lgpio.tx_pwm(self.h, self.ENL, 0, 0.0)
        lgpio.tx_pwm(self.h, self.ENR, 0, 0.0)

        #close chip
        lgpio.gpiochip_close(self.h)

    def stop(self):
        # Stop motors
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 0)
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 0)
        
    def turn(self, dir, deg):
        if dir == "right":
            lgpio.gpio_write(self.h, self.INL1, 1)
            lgpio.gpio_write(self.h, self.INL2, 0)
            self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, 50) 
        
            lgpio.gpio_write(self.h, self.INR1, 0)
            lgpio.gpio_write(self.h, self.INR2, 1)
            self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, 50)
            
        elif dir =="left":
        
            lgpio.gpio_write(self.h, self.INL1, 0)
            lgpio.gpio_write(self.h, self.INL2, 1)
            self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, 50) 
        
            lgpio.gpio_write(self.h, self.INR1, 1)
            lgpio.gpio_write(self.h, self.INR2, 0)
            self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, 30)
        
        self.gyro.turn_to(dir, deg)
        self.stop()
        self.set_speed(50)
    
    def chat_turn(self, dir, deg):
        print(f"Starting turn {dir} by {deg} degrees")

    # Set motor directions and speeds for turning
        if dir == "right":
            lgpio.gpio_write(self.h, self.INL1, 1)
            lgpio.gpio_write(self.h, self.INL2, 0)
            self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, 30)

            lgpio.gpio_write(self.h, self.INR1, 0)
            lgpio.gpio_write(self.h, self.INR2, 1)
            self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, 15)

        elif dir == "left":
            lgpio.gpio_write(self.h, self.INL1, 0)
            lgpio.gpio_write(self.h, self.INL2, 1)
            self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, 20)

            lgpio.gpio_write(self.h, self.INR1, 1)
            lgpio.gpio_write(self.h, self.INR2, 0)
            self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, 20)

        else:
            print("Invalid turn direction! Use 'left' or 'right'.")
            return

        time.sleep(0.1)  # small delay to let motors start spinning

        try:
            self.gyro.turn_to(dir,deg)
        except Exception as e:
            print(f"Error during turn: {e}")

        self.stop()
        self.set_speed(50)

         
        
        

