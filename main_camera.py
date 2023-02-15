

import cv2
import apriltag

#Macros that remain constant
video_stream_title = 'Vehicle Tracking'
camera = cv2.VideoCapture(0)

#Setup function before streaming video
def setup_camera():

    #Connect to camera
    #camera = cv2.VideoCapture(0)

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

        #Convert new frame to gray scale
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

        #Display video stream
        cv2.imshow(video_stream_title, new_frame)

        #Wait for 0 milliseconds
        #If key pressed == Esc, close window
        if cv2.waitKey(0) == 27:
            break

    #Release video and close windows
    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main_camera()