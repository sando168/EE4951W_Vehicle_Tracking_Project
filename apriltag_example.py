
# Example Code From:
# https://github.com/swatbotics/apriltag

'''Demonstrate Python wrapper of C apriltag library by running on camera frames.'''
from __future__ import division
from __future__ import print_function

from argparse import ArgumentParser
import cv2
import apriltag

# for some reason pylint complains about members being undefined :(
# pylint: disable=E1101

def main():

    '''Main function.'''

    parser = ArgumentParser(
        description='test apriltag Python bindings')

    parser.add_argument('device_or_movie', metavar='INPUT', nargs='?', default=0,
                        help='Movie to load or integer ID of camera device')

    apriltag.add_arguments(parser)

    options = parser.parse_args()

    img = cv2.imread('apriltag_test.png', cv2.IMREAD_GRAYSCALE)

    window = 'April Tag Example'
    cv2.namedWindow(window)

    # set up a reasonable search path for the apriltag DLL inside the
    # github repo this file lives in;
    #
    # for "real" deployments, either install the DLL in the appropriate
    # system-wide library directory, or specify your own search paths
    # as needed.

    detector = apriltag.Detector(options,
                                searchpath=apriltag._get_demo_searchpath())

    detections, dimg = detector.detect(img, return_image=True)

    num_detections = len(detections)
    print('Detected {} tags.\n'.format(num_detections))

    for i, detection in enumerate(detections):
        print('Detection {} of {}:'.format(i+1, num_detections))
        print()
        print(detection.tostring(indent=2))
        print()

    overlay = img // 2 + dimg[:, :] // 2

    while True:
        cv2.imshow(window, overlay)
        k = cv2.waitKey(1)

if __name__ == '__main__':
    main()