'Reads a video file and decodes the message played on the Circuit Playground Express pixels 0–5'

from typing import Tuple, Generator, Iterable
import cv2
import numpy as np
from geometry import Geometry

INPUT_VIDEO_FILENAME = 'media/cpx.mov'
OUTPUT_VIDEO_FILENAME = 'media/decoded.mov'
DECODED_VID_FPS = 60
BRIGHT_AREA_RANGE = 250, 255
LOG = True


def process_video():
    'Process the input video file and write the result to a new file'

    video_in = cv2.VideoCapture(INPUT_VIDEO_FILENAME)
    read_return_code, frame = video_in.read()
    height, width = frame.shape[:2]
    video_out = cv2.VideoWriter(OUTPUT_VIDEO_FILENAME, cv2.VideoWriter_fourcc(*'avc1'),
                                DECODED_VID_FPS, (width, height))
    # The greatest number found between pixels-off times is likely to be the correct number.
    greatest_sum_of_on_powers = None
    message = ''

    while read_return_code:
        bright_areas = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
            BRIGHT_AREA_RANGE[0], BRIGHT_AREA_RANGE[1])
        geom = Geometry(bright_areas)

        def on_powers() -> Iterable[int]:
            'Return those powers of two corresponding to the lit pels'
            return (power for power in range(5) if geom.pel_on(power))

        if geom.registration_pels_found():
            sum_of_on_powers = sum(1 << power for power in on_powers())
            if LOG and sum_of_on_powers > 0: print(sum_of_on_powers, '', end='')
            if sum_of_on_powers > 0:
                if greatest_sum_of_on_powers is None or sum_of_on_powers > greatest_sum_of_on_powers:
                    greatest_sum_of_on_powers = sum_of_on_powers
            else:
                if greatest_sum_of_on_powers:
                    if LOG: print(greatest_sum_of_on_powers)
                    letter = ' ' if greatest_sum_of_on_powers == 27 else chr(greatest_sum_of_on_powers + ord('a') - 1)
                    print(letter, end=('\n' if LOG else ''))
                    message += letter
                    greatest_sum_of_on_powers = None
            cf = centered_frame(frame, geom.center)
            cv2.putText(cf, message, (50, frame.shape[0] - 50),
                 cv2.FONT_HERSHEY_SIMPLEX, 1.5, (200, 200, 100), 3)
            video_out.write(cf)

        read_return_code, frame = video_in.read()

    video_in.release()
    video_out.release()


def centered_frame(frame, center: Tuple[int, int]):
    'Return a new image with the CPX centered in the image'

    dy: int = (frame.shape[0] / 2) - center[1]
    dx: int = (frame.shape[1] / 2) - center[0]
    rows, cols = frame.shape[:2]
    stabilization_xform_matrix = np.float32([
        [1, 0, dx],
        [0, 1, dy]
    ])
    return cv2.warpAffine(frame, stabilization_xform_matrix, (cols, rows))


def process_image_file():
    'Display the set pixels in a single image (for testing)'
    frame = cv2.imread('media/cpx.png')
    bright_areas = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), BRIGHT_AREA_RANGE[0], BRIGHT_AREA_RANGE[1])
    cv2.imwrite('bright.png', bright_areas)
    geom = Geometry(bright_areas)
    p = [power for power in range(5) if geom.pel_on(power)]
    cv2.imshow('', bright_areas)
    cv2.waitKey(0)
    print(p)


process_video()
