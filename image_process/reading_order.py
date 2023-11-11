"""
sort the ocr bbox according to reading order
from top-to-bottom and left-to-right.
y tolerance supported.
"""

import cv2

from functools import cmp_to_key

def cmp_default(pt1, pt2):
    tolerance = 32
    if abs(pt1[1] - pt2[1]) < tolerance:
        return -1 if pt1[0] < pt2[0] else 1
    else:
        return -1 if pt1[1] < pt2[1] else 1

img = cv2.imread("a.png", 0)

_, img = cv2.threshold(img, 70, 255, cv2.THRESH_BINARY)

contours, h = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

pts = [cv2.boundingRect(contour)[:2] for contour in contours]
pts = sorted(pts, key=cmp_to_key(cmp_default))

# For debugging purposes.
for i in range(len(pts)):
    img = cv2.putText(img, str(i), pts[i], cv2.FONT_HERSHEY_COMPLEX, 1, [125])

cv2.imwrite("output.png", img)
