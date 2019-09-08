# This encoder runs on the Circuit Playground Express

import time
from adafruit_circuitplayground.express import cpx

cpx.pixels.brightness = 0.1

num = 0
white = 64, 64, 64
for rp in (7, 9):
    cpx.pixels[rp] = white


def display(n):
    for i in range(5):
        power = i
        on = num & (1 << power)
        cpx.pixels[i] = white if on else (0, 0, 0)


message = 'it is amazing that a computer can read this'

while True:
    for c in message:
        num = 27 if c == ' ' else ord(c) - ord('a') + 1
        display(num)
        time.sleep(1/24)
        for i in range(5):
            cpx.pixels[i] = (0, 0, 0);
        time.sleep(1/24)
    time.sleep(1)
