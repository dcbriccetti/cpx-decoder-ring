from sense_hat import SenseHat
from time import sleep
from itertools import chain

sh = SenseHat()
w = [128 for n in range(3)]
off = (0, 0, 0)

# From Wikipedia
msg = '''
Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python's design philosophy emphasizes code readability with its notable use of significant whitespace. Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.[27]
Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming. Python is often described as a "batteries included" language due to its comprehensive standard library.[28]
'''
frames = []
for pos in range(0, len(msg), 8):
    eight_chars = msg[pos:pos + 8]
    eight_chars += ' ' * (8 - len(eight_chars))  # Pad to 8 chars
    frame = []
    for ch in eight_chars:
        for p in range(8):
            frame.append(w if ord(ch) & 1 << p else off)
    frames.append(frame)

while True:
    for frame in frames:
        sh.set_pixels(frame)
        sleep(0.05)
        sh.clear()
        sleep(0.08)
    sleep(0.5)
