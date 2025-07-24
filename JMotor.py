import lgpio
import time

class JMotor:
    def __init__(self):
        
        self.INL1 = 17
        self.INL2 = 27
        self.ENL = 22
        self.INR1 = 20
        self.INR2 = 16
        self.ENR = 21
        self.speed = 5 #set speed (1-10 > percent duty cycle*10)
        self.speed_ms = 1.2 # conversion factor
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
            
        time.sleep(0.01*self.speed)
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
        
    def turn_right(self):
        
        lgpio.gpio_write(self.h, self.INL1, 1)
        lgpio.gpio_write(self.h, self.INL2, 0)
        self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, 3) 
        
        lgpio.gpio_write(self.h, self.INR1, 0)
        lgpio.gpio_write(self.h, self.INR2, 1)
        self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, 5)
        
    def turn_left(self):
        
        lgpio.gpio_write(self.h, self.INL1, 0)
        lgpio.gpio_write(self.h, self.INL2, 1)
        self.motorL = lgpio.tx_pwm(self.h, self.ENL, 1000, 5) 
        
        lgpio.gpio_write(self.h, self.INR1, 1)
        lgpio.gpio_write(self.h, self.INR2, 0)
        self.motorR = lgpio.tx_pwm(self.h, self.ENR, 1000, 3)
        
    
        
         
        
        

