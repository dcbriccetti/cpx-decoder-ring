from time import sleep, time
from typing import Tuple, Union
from math import cos, sin, pi, tau, atan2, sqrt, pow
import cv2
import numpy as np

LOG = False


def find_1d_ranges(img, axis, limit=None, min_size=5):
    range_start: Union[None, int] = None
    found = 0
    for position in range(img.shape[axis] - 1, -1, -1):
        vert_or_horz_slice = img[:, position] if axis == 1 else img[position, :]
        any_nonzero_pels = np.any(vert_or_horz_slice > 0)
        if range_start:
            if not any_nonzero_pels:
                if range_start - position >= min_size:
                    found += 1
                    yield position, range_start

                if limit and found >= limit:
                    return

                range_start = None
        else:  # Not in a range
            if any_nonzero_pels:
                range_start = position


def find_registration_pels(img):
    for start, end in find_1d_ranges(img, 1, 2):
        y_start, y_end = tuple(find_1d_ranges(img[:, start:end], 0, 1))[0]
        yield round(start + (end - start) / 2), round(y_start + (y_end - y_start) / 2)


def find_center(reg0deg: Tuple[float, float], reg60deg: Tuple[float, float]):
    root3 = sqrt(3)
    x1, y1 = reg60deg
    x2, y2 = reg0deg
    # https://www.quora.com/Given-two-vertices-of-an-equilateral-triangle-what’s-the-formula-to-find-the-third-vertex/answer/Greg-Gruzalski
    return (x1 + x2 + root3 * (y1 - y2)) / 2, (y1 + y2 + root3 * (x2 - x1)) / 2


def process_frames():
    cap = cv2.VideoCapture('cpx.mov')
    ret, frame = cap.read()
    height, width, layers = frame.shape
    video = cv2.VideoWriter('decoded.mov', cv2.VideoWriter_fourcc(*'avc1'), 60, (width, height))

    best_letter_value = None
    message = ''

    while ret:
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bright_areas = cv2.inRange(gray_img, 250, 255)
        reg_pels = tuple(find_registration_pels(bright_areas))
        if len(reg_pels) == 2:
            reg0deg, reg60deg = reg_pels
            center = find_center(reg0deg, reg60deg)
            dx = reg0deg[0] - center[0]
            dy = reg0deg[1] - center[1]
            radius = sqrt(pow(dx, 2) + pow(dy, 2))
            global_rotation = atan2(dy, dx)
            twelfth = tau / 12
            def angle(power): return twelfth * (power + 4) + global_rotation
            bits = ((round(center[0] + cos(angle(power)) * radius),
                       round(center[1] + sin(angle(power)) * radius)) for power in range(5))
            parts = (int(pow(2, 4-i)) * (1 if bright_areas[b[1], b[0]] > 0 else 0) for i, b in enumerate(bits))
            v = sum(parts)
            if LOG and v > 0:
                print(v, '', end='')
            if v:
                if best_letter_value is None or v > best_letter_value:
                    best_letter_value = v
            else:
                if best_letter_value:
                    largest = best_letter_value
                    if LOG: print(largest)
                    c = ' ' if largest == 27 else chr(largest + ord('a') - 1)
                    end = '\n' if LOG else ''
                    print(c, end=end)
                    message += c
                    best_letter_value = None
            move_y = (frame.shape[0] / 2) - center[1]
            move_x = (frame.shape[1] / 2) - center[0]
            stabilization_xform_matrix = np.float32(
                [[1, 0, move_x],
                 [0, 1, move_y]]
            )
            stabilized_frame = cv2.warpAffine(frame, stabilization_xform_matrix, frame.shape[:2])
            cv2.putText(stabilized_frame, message, (50, frame.shape[0] - 50),
                 cv2.FONT_HERSHEY_SIMPLEX, 1.5, (200, 200, 100), 3)
            video.write(stabilized_frame)

        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()
    video.release()
    return


process_frames()
