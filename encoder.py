import time
from adafruit_circuitplayground.express import cpx

cpx.pixels.brightness = 0.1
cpx.pixels.auto_write = False

num = 0
white = 64, 64, 64
for rp in (7, 9):
    cpx.pixels[rp] = white

def display(num):
    for i in range(5):
        power = i
        on = num & (1 << power)
        cpx.pixels[i] = white if on else (0, 0, 0)
    cpx.pixels.show()


message = 'it is amazing that a computer can read this'

while True:
    for c in message:
        num = 27 if c == ' ' else ord(c) - ord('a') + 1
        display(num)
        time.sleep(1/50)
        display(0)
        time.sleep(1/50)
    time.sleep(1)
