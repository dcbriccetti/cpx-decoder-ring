from math import cos, sin, pi
import cv2
import numpy as np

cap = cv2.VideoCapture('cpx.mov')


def consolidate(hits):
    result = []
    n = None
    for h in hits:
        if n and h == n + 1:
            n += 1
        else:
            n = h
            result.append(h)
    return result


# 60 -1.7320508075688776

def slopes_powers():
    def d2r(d): return d / 360 * 2 * pi

    x1 = cos(0)
    y1 = sin(0)

    for power in range(5):
        pos = 120 + power * 30
        x2 = cos(d2r(pos))
        y2 = sin(d2r(pos))
        yield (y2 - y1) / (x2 - x1), power


def power_at_slope(slope: float):
    closest_slope: tuple[float, int] = sp[0]
    for s in sp[1:]:
        if abs(slope - s[0]) < abs(slope - closest_slope[0]):
            closest_slope = s
    return closest_slope[1]


sp = list(slopes_powers())
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret: break
    frame_count += 1
    if frame_count % 1 == 0:
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(gray_img, (0, 0), fx=0.5, fy=0.5)
        # img[img < 240] = 0
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 15, param1=255, param2=30, minRadius=5, maxRadius=50)
        if circles is not None:
            print(circles)
            if circles.shape[1] >= 2:
                xf = circles[0, :, 0:2]
                xf2 = xf[xf[:, 0].argsort()]
                reg1 = xf2[-1]
                reg2 = xf2[-2]
                diff = reg2 - reg1
                slope = diff[1] / diff[0]

                lsum = 0
                for light in xf2[:-2]:
                    diff = light - reg1
                    slope = diff[1] / diff[0]
                    pas = power_at_slope(-slope)
                    lsum += 2**pas

                print(lsum, end=' ')
        cv2.imshow('Image', img)
        cv2.waitKey(0)
        # break

cap.release()
cv2.destroyAllWindows()
