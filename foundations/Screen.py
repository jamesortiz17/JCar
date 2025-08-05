import smbus
import time

#setup constants
I2C_ADDR = 0x27   
LCD_WIDTH = 16    #max chars per line

LCD_CHR = 1       #sending data
LCD_CMD = 0       #sending command

LCD_LINE_1 = 0x80 #address for line 1
LCD_LINE_2 = 0xC0 #address for line 2

LCD_BACKLIGHT = 0x08

ENABLE = 0b00000100

#setup bus
bus = smbus.SMBus(1) 


def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low  = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)
        
def lcd_init():
    lcd_byte(0x33, LCD_CMD) 
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.0005)

def screen_print(line1, line2):
    lcd_init()
    lcd_string(line1, LCD_LINE_1)
    lcd_string(line2, LCD_LINE_2)


