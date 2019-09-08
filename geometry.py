'Module containing the Geometry class'

from math import sqrt, atan2, tau, sin, cos
from typing import Tuple, Union, Iterable
import numpy as np


class Geometry:
    'Finds things in the image frames'
    def __init__(self, bright_areas):
        self.registration_pels = tuple(self._find_registration_pels(bright_areas))
        if self.registration_pels_found():
            self.bright_areas = bright_areas
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
                return -(tau / 12 * starting_twelfth) #+ self.global_rotation

            a = angle()
            return (round(self.center[0] + cos(a) * self.radius),
                    round(self.center[1] + sin(a) * self.radius))

        col, row = pel_location()
        on = self.bright_areas[row, col] > 0
        return on

    @staticmethod
    def _find_registration_pels(image):

        def bright_ranges(image, axis, limit=None, min_size=5) -> Iterable[Tuple[int, int]]:
            'Return ranges (rectangular areas) where bright pixels are found'
            range_start: Union[None, int] = None
            found = 0
            for position in range(image.shape[axis] - 1, -1, -1):
                vert_or_horz_slice = image[:, position] if axis == 1 else image[position, :]
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

        for left, right in bright_ranges(image, axis=1, limit=2):
            top, bottom = tuple(bright_ranges(image[:, left:right], axis=0, limit=1))[0]
            width:  int = right - left
            height: int = bottom - top
            pel_center: Tuple[int, int] = (round(left + width / 2), round(top + height / 2))
            yield pel_center

    @staticmethod
    def _find_center_from_registration_pels(reg0deg: Tuple[float, float], reg60deg: Tuple[float, float]):
        root3 = sqrt(3)
        x1, y1 = reg60deg
        x2, y2 = reg0deg
        # https://www.quora.com/Given-two-vertices-of-an-equilateral-triangle-what%E2%80%99s-the-formula-to-find-the-third-vertex/answer/Greg-Gruzalski
        return (x1 + x2 + root3 * (y1 - y2)) / 2, (y1 + y2 + root3 * (x2 - x1)) / 2
