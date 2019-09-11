'Module containing the Geometry class'

from math import sqrt, atan2, tau, sin, cos
from time import time
from typing import Sequence, Tuple, List, Union, Iterable
import cv2
import numpy as np


class Geometry:
    'Finds things in the image frames'
    def __init__(self, frame, reg_points_image):
        self.registration_pels = tuple(self._find_registration_pels(reg_points_image))
        if self.registration_pels_found():
            self.frame = frame
            self.bright_areas = reg_points_image
            reg0deg, reg60deg = self.registration_pels
            self.center = self._find_center_from_registration_pels(reg0deg, reg60deg)
            dx = reg0deg[0] - self.center[0]
            dy = reg0deg[1] - self.center[1]
            self.radius = sqrt(pow(dx, 2) + pow(dy, 2))
            self.global_rotation = atan2(dy, dx)

    def registration_pels_found(self) -> bool:
        'return whether the two registration pels at 0° and 60° were found'
        return len(self.registration_pels) == 2

    def pel_on(self, power: int) -> bool:
        'Examine the bright areas image and return whether there’s a lit pel for the given power'

        def pel_location() -> Tuple[int, int]:
            'Return the coordinates of the pel representing the given power of 2'

            def angle() -> float:
                'return the angle, in radians, of the pel corresponding to the given power of 2'
                starting_twelfth = power + 4
                return -(tau / 12 * starting_twelfth) + self.global_rotation

            a = angle()
            return (round(self.center[0] + cos(a) * self.radius),
                    round(self.center[1] + sin(a) * self.radius))

        col, row = pel_location()
        on = np.all(self.frame[row, col] > 240)
        return on

    @staticmethod
    def _find_registration_pels(image) -> List[Tuple[int, int]]:
        'Find the objects in the image and return the coordinates of the rightmost two'
        p = cv2.SimpleBlobDetector_Params()
        p.filterByColor = p.filterByConvexity = False
        p.filterByArea = True
        p.minArea = 100
        detector = cv2.SimpleBlobDetector_create(p)
        key_points = detector.detect(image)
        def r(kp, i): return round(kp.pt[i])
        coords = [(r(kp, 0), r(kp, 1)) for kp in key_points]
        coords.sort(key=lambda t: t[0], reverse=True)
        return coords[:2]


    @staticmethod
    def _find_center_from_registration_pels(reg0deg: Tuple[float, float], reg60deg: Tuple[float, float]):
        root3 = sqrt(3)
        x1, y1 = reg60deg
        x2, y2 = reg0deg
        # https://www.quora.com/Given-two-vertices-of-an-equilateral-triangle-what%E2%80%99s-the-formula-to-find-the-third-vertex/answer/Greg-Gruzalski
        return (x1 + x2 + root3 * (y1 - y2)) / 2, (y1 + y2 + root3 * (x2 - x1)) / 2
