
# Example Code From:
# https://github.com/swatbotics/apriltag

import apriltag
import cv2
img = cv2.imread('apriltag_photo.png', cv2.IMREAD_GRAYSCALE)
detector = apriltag.Detector()
result = detector.detect(img)
print(result)