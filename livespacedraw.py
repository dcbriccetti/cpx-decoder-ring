import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)
accumulator_frame = None
while True:
    ret, frame = cap.read()
    fs = frame.shape
    flipped = cv.flip(frame, 1)
    mask = cv.inRange(flipped, (0, 120, 120), (20, 255, 255))
    masked_input = cv.bitwise_and(flipped, flipped, mask=mask)
    if accumulator_frame is None:
        accumulator_frame = np.zeros(fs, dtype=np.uint8)

    p = cv.SimpleBlobDetector_Params()
    p.filterByColor = False
    p.filterByConvexity = False
    p.filterByArea = True
    p.minArea = 200
    detector = cv.SimpleBlobDetector_create(p)
    key_points = detector.detect(mask)  # Blob detection here for future enhancements

    if key_points:
        pt = key_points[0].pt
        if pt[0] < 100 and pt[1] < 100:
            accumulator_frame[:, :, :] = 0
        cv.circle(accumulator_frame, (round(pt[0]), round(pt[1])), 30, (0, 255, 255), -1)

    cv.imshow('Input', flipped)
    cv.imshow('Yellow', mask)
    cv.imshow('Time-Lapse', accumulator_frame)
    if cv.waitKey(1) == ord('q'):
        break
cap.release()
cv.destroyAllWindows()
