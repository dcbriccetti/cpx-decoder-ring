import cv2
import numpy as np

SHOW = True
video_in = cv2.VideoCapture('media/drawing2.mov')
read_return_code, frame = video_in.read()
height, width = frame.shape[:2]
video_out = cv2.VideoWriter('media/time_image.mov', cv2.VideoWriter_fourcc(*'avc1'),
                            24, (width, height))
time_image = None
while read_return_code:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only selected colors
    mask = cv2.inRange(hsv, (5, 128, 128), (30, 255, 255))
    # Bitwise-AND mask and original image
    masked = cv2.bitwise_and(hsv, hsv, mask=mask)
    if time_image is None:
        time_image = masked

    p = cv2.SimpleBlobDetector_Params()
    p.filterByColor = False
    p.filterByConvexity = False
    p.filterByArea = True
    p.minArea = 2000
    detector = cv2.SimpleBlobDetector_create(p)
    key_points = detector.detect(mask)  # Blob detection here for future enhancements
    print([p.pt for p in key_points])
    if len(key_points) != 1:
        if SHOW:
            cv2.imshow('Original', frame)
            cv2.imshow('Mask', mask)
            cv2.imshow('Pen cap', masked)
            cv2.imshow('Timelapsed', time_image)
            cv2.waitKey(0)


    time_image = cv2.bitwise_or(time_image, masked)
    video_out.write(time_image)
    read_return_code, frame = video_in.read()

video_in.release()
video_out.release()
