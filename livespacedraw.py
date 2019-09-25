import cv2 as cv
import numpy as np

MAX_USERS = 3

RED     = (  0,   0, 255)
GREEN   = (  0, 255,   0)
BLUE    = (255,   0,   0)
YELLOW  = (  0, 255, 255)
ORANGE  = (  0, 128, 255)

ranges = np.zeros((MAX_USERS, 2, 3), dtype=np.uint8)

colors_by_command_key = {'r': RED, 'g': GREEN, 'b': BLUE, 'y': YELLOW, 'o': ORANGE}
selected_colors = [RED, GREEN, BLUE, YELLOW, ORANGE]

cap = cv.VideoCapture(0)
accumulator_frame = None
calibrating = False
active_user = 0
calibrated_user_indexes = set()


def adjusted_mins_maxes():
    center = resized_flipped_hsv[center_row - 5:center_row + 6, center_column - 5:center_column + 6, :]
    mins  = [center[:, :, c].min() for c in range(3)]
    maxes = [center[:, :, c].max() for c in range(3)]
    for i in range(3):
        mins[i] = max(0, mins[i] - 3)
        maxes[i] = min(255, maxes[i] + 3)
    return np.array(mins), np.array(maxes)


def calibrate():
    global calibrating
    calibrated_user_indexes.add(active_user)
    l, u = adjusted_mins_maxes()
    if not calibrating:
        ranges[active_user, 0], ranges[active_user, 1] = l, u
    else:
        for n in range(3):
            if l[n] < ranges[active_user, 0, n]:
                ranges[active_user, 0, n] = l[n]
            if u[n] > ranges[active_user, 1, n]:
                ranges[active_user, 1, n] = u[n]
    calibrating = True


p = cv.SimpleBlobDetector_Params()
p.filterByColor = False
p.filterByConvexity = False
p.filterByArea = True
p.minArea = 100
detector = cv.SimpleBlobDetector_create(p)

while True:
    ret, large_frame = cap.read()
    resized_unflipped = cv.resize(large_frame, (0, 0), fx=0.5, fy=0.5)
    resized_flipped = cv.flip(resized_unflipped, 1)
    resized_flipped_hsv = cv.cvtColor(resized_flipped, cv.COLOR_BGR2HSV)
    fs = resized_flipped_hsv.shape
    center_row = fs[0] // 2
    center_column = fs[1] // 2
    cv.rectangle(resized_flipped, (center_column - 5, center_row - 5), (center_column + 5, center_row + 5), (255, 255, 255), 1)

    def mask_for_user(i): return cv.inRange(resized_flipped_hsv, ranges[i, 0], ranges[i, 1])
    players_and_masks = [(i, mask_for_user(i)) for i in calibrated_user_indexes]
    mask_all = players_and_masks[0][1] if players_and_masks else None
    if len(players_and_masks) > 1:
        for i in range(1, len(players_and_masks)):
            mask_all = cv.bitwise_or(mask_all, players_and_masks[i][1])
    masked_input = None if mask_all is None else cv.bitwise_and(resized_flipped, resized_flipped, mask=mask_all)
    if accumulator_frame is None:
        accumulator_frame = np.zeros(fs, dtype=np.uint8)

    if players_and_masks:
        for player_index, mask in players_and_masks:
            key_points = detector.detect(mask)

            if key_points:
                pt = key_points[0].pt
                if pt[0] < 100 and pt[1] < 100:
                    accumulator_frame[:, :, :] = 0
                cv.circle(accumulator_frame, (round(pt[0]), round(pt[1])), 5, selected_colors[player_index], -1)

        cv.imshow('Masked', masked_input)
        cv.imshow('Drawing', accumulator_frame)
    cv.imshow('Input', resized_flipped)
    key = cv.waitKey(50)
    if key == -1:
        if calibrating:
            print('Calibration done')
            print(ranges)
            calibrating = False
    else:
        key_char = chr(key)
        if key_char == 'q':
            break
        if key_char == 'c':
            calibrate()
        else:
            if ord('1') <= key <= ord(str(MAX_USERS)):
                active_user = key - ord('1')
                print('Active user:', key_char)
            color = colors_by_command_key.get(key_char)
            if color:
                selected_colors[active_user] = color

cap.release()
cv.destroyAllWindows()
