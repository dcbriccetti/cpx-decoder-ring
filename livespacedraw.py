import cv2 as cv
import numpy as np

YELLOW = (0, 255, 255)
ORANGE = (0, 128, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

YELLOW_MIN = (0, 240, 240)
YELLOW_MAX = (200, 255, 255)
ORANGE_MIN = (50, 50, 235)
ORANGE_MAX = (130, 130, 255)

colors_by_command_key = {"r": RED, "g": GREEN, "b": BLUE}
selected_color = RED

cap = cv.VideoCapture(0)
accumulator_frame = None
while True:
    ret, large_frame = cap.read()
    frame = cv.resize(large_frame, (0, 0), fx=0.5, fy=0.5)
    fs = frame.shape
    flipped = cv.flip(frame, 1)
    mask_orange = cv.inRange(flipped, ORANGE_MIN, ORANGE_MAX)
    mask_yellow = cv.inRange(flipped, YELLOW_MIN, YELLOW_MAX)
    mask_all = cv.bitwise_or(mask_yellow, mask_orange)
    masked_input = cv.bitwise_and(flipped, flipped, mask=mask_all)
    if accumulator_frame is None:
        accumulator_frame = np.zeros(fs, dtype=np.uint8)

    p = cv.SimpleBlobDetector_Params()
    p.filterByColor = False
    p.filterByConvexity = False
    p.filterByArea = True
    p.minArea = 100
    detector = cv.SimpleBlobDetector_create(p)

    for mask, _ in ((mask_orange, ORANGE), (mask_yellow, YELLOW)):
        key_points = detector.detect(mask)

        if key_points:
            pt = key_points[0].pt
            if pt[0] < 100 and pt[1] < 100:
                accumulator_frame[:, :, :] = 0
            cv.circle(accumulator_frame, (round(pt[0]), round(pt[1])), 5, selected_color, -1)

    cv.imshow('Input', flipped)
    cv.imshow('Masked', masked_input)
    cv.imshow('Time-Lapse', accumulator_frame)
    key = cv.waitKey(10)
    if key != -1:
        if chr(key) == 'q':
            break
        color = colors_by_command_key.get(chr(key))
        if color:
            selected_color = color

cap.release()
cv.destroyAllWindows()
