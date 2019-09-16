'Reads a video file and decodes the message played on the Raspberry Pi Sense HAT'

from typing import Tuple, Generator, Iterable
import cv2
import numpy as np
from geometry import Geometry

INPUT_VIDEO_FILENAME = 'message.mov'
OUTPUT_VIDEO_FILENAME = 'decoded.mov'
DECODED_VID_FPS = 10
LOG = False
SHOW_FRAMES = False
TOP_RIGHT = (255, 721)  # row, col
SPACING = (32, 30)  # vertical, horizontal


def process_video():
    'Process the input video file and write the result to a new file'

    video_in = cv2.VideoCapture(INPUT_VIDEO_FILENAME)
    read_return_code, frame = video_in.read()
    height, width = frame.shape[:2]
    video_out = cv2.VideoWriter(OUTPUT_VIDEO_FILENAME, cv2.VideoWriter_fourcc(*'avc1'),
                                DECODED_VID_FPS, (width, height))
    in_paint = False
    accum = None
    msg = ''

    while read_return_code:
        chars = chars_from_frame(frame)

        if chars:
            if in_paint:
                accum = cv2.bitwise_or(accum, frame)
            else:
                accum = frame
                in_paint = True
        else:
            if in_paint:
                chars = chars_from_frame(accum)
                msg += chars
                in_paint = False
                cv2.putText(accum, chars, (accum.shape[1] // 2 - SPACING[1] * 8 // 2, accum.shape[0] - 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (250, 250, 250), 4)
                cv2.putText(accum, msg[-100:], (30, accum.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 100), 2)
                video_out.write(accum)

        if SHOW_FRAMES:
            cv2.imshow('Frame', frame)
            if accum is not None:
                cv2.imshow('Accum', accum)
            cv2.waitKey(0)

        read_return_code, frame = video_in.read()

    print(msg)
    video_in.release()
    video_out.release()
    cv2.destroyAllWindows()


def chars_from_frame(gray):
    chars = ''
    for lrow in range(7, -1, -1):
        row = TOP_RIGHT[0] + lrow * SPACING[0]
        byte = 0
        for lcol in range(8):
            col = TOP_RIGHT[1] - lcol * SPACING[1]
            on = np.any(gray[row, col] > 200)
            if on:
                byte |= 1 << lcol
        if byte != 0:
            char = ' ' if byte == 10 else chr(byte)  # Replace newlines
            chars += char
    return chars


process_video()
