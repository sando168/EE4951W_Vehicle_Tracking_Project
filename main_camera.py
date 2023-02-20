

import cv2
import apriltag
import numpy as np

#Macros that remain constant
video_stream_title = 'Vehicle Tracking'
camera = cv2.VideoCapture(0)

#Setup function before streaming video
def setup_camera():

    #Error and stop program if not connected
    if not(camera.isOpened()):
        print('ERROR: Unable to connect to camera')


#Start of Camera Code
def main_camera():

    setup_camera()

    #Start of while(1) loop that runs forever
    while True:

        #Retrieve new frame from camera
        ret, new_frame = camera.read()

        #Check if new_frame is correct
        if not(ret):
            break

        #Convert new frame to gray scale
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

        #Create AprilTag Detector
        tag_detector = apriltag.Detector()

        #Detect AprilTags
        tags = tag_detector.detect(new_frame_gray)

        #Outline each detected tag with a square
        outlined_tags = new_frame
        for tag in tags:

            #Cast corners to tuple integer pairs
            upper_left_corner = (int(tag.corners[0][0]), int(tag.corners[0][1]))
            upper_right_corner = (int(tag.corners[1][0]), int(tag.corners[1][1]))
            bottom_right_corner = (int(tag.corners[2][0]), int(tag.corners[2][1]))
            bottom_left_corner = (int(tag.corners[3][0]), int(tag.corners[3][1]))
            corners = np.array([[upper_left_corner[0],   upper_left_corner[1]],
                                [upper_right_corner[0],  upper_right_corner[1]],
                                [bottom_right_corner[0], bottom_right_corner[1]],
                                [bottom_left_corner[0],  bottom_left_corner[1]]])
            
            #Draw the arbitrary contour from corners since the tag could be rotated
            cv2.drawContours(outlined_tags, [corners], 0, (255,0,0), 3)

        #Display video stream
        cv2.imshow(video_stream_title, outlined_tags)

        #Can close window on Ctrl+C
        if cv2.waitKey(1) == ord('q'):
            break

    #Release video and close windows
    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main_camera()