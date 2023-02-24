
import cv2
import apriltag
import numpy as np

import imgui
import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import time

#Macros that remain constant
GUI_WIDTH = 480
GUI_HEIGHT = 480
video_stream_title = 'Vehicle Tracking' #Title of tracking window
camera = cv2.VideoCapture(0)            #Open video camera
tag_detector = apriltag.Detector()      #Create tag detection object

#Setup function for creating vehicle UI window
def impl_glfw_init():

    #Initialize GLFW and detect for any errors
    if not(glfw.init()):
        print("Unable to initialize GLFW for vehicle UI")
        exit(1)

    #Set GLFW OpenGL version
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    #Create vehicle UI window
    gui = glfw.create_window(GUI_WIDTH, GUI_HEIGHT, "Vehicle UI", None, None)
    glfw.make_context_current(gui)

    #Detect if anything went wrong when creating window
    if not(gui):
        glfw.terminate()
        print("Failed to create window for vehicle UI")
        exit(1)

    return gui

#Setup function before streaming video
def setup_camera():

    #Error and stop program if not connected
    if not(camera.isOpened()):
        print('ERROR: Unable to connect to camera')
    else:
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 0)


#Start of Camera Code
def main_camera():

    #Setup functions
    setup_camera()
    gui = impl_glfw_init()
    imgui.create_context()
    imgui.get_io().display_size = GUI_WIDTH, GUI_HEIGHT
    imgui.get_io().fonts.get_tex_data_as_rgba32()
    impl = GlfwRenderer(gui)

    #Time variables for measuring framerate
    previous_time = 1
    current_time = 1
    #Start of while(1) loop that runs forever
    while True:

        #Begin UI window events
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()
        imgui.begin("Vehicle UI")

        #Update timers
        current_time = time.perf_counter() 

        #Retrieve new frame from camera
        ret, new_frame = camera.read()

        #Check if new_frame is correct
        if not(ret):
            break

        #Convert new frame to gray scale
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

        #Detect AprilTags
        tags = tag_detector.detect(new_frame_gray)

        #Outline each detected tag with a square
        outlined_tags = new_frame
        angle = 0
        for tag in tags:

            #Cast corners to tuple integer pairs
            center = (int(tag.center[0]), int(tag.center[1]))
            upper_left_corner = (int(tag.corners[0][0]), int(tag.corners[0][1]))
            upper_right_corner = (int(tag.corners[1][0]), int(tag.corners[1][1]))
            bottom_right_corner = (int(tag.corners[2][0]), int(tag.corners[2][1]))
            bottom_left_corner = (int(tag.corners[3][0]), int(tag.corners[3][1]))
            corners = np.array([[upper_left_corner[0],   upper_left_corner[1]],
                                [upper_right_corner[0],  upper_right_corner[1]],
                                [bottom_right_corner[0], bottom_right_corner[1]],
                                [bottom_left_corner[0],  bottom_left_corner[1]]])

            #Solve for angular rotation
            x = upper_right_corner[0] - upper_left_corner[0]
            y = upper_left_corner[1] - upper_right_corner[1]
            theta = np.arctan2(y, x)
            angle = np.rad2deg(theta)

            #Draw the arbitrary contour from corners since the tag could be rotated
            cv2.drawContours(outlined_tags, [corners], 0, (255,0,0), 3)

            #Draw red line from cetner of tag to indicate angle
            length = np.linalg.norm(np.array([x, y]))
            length = int(length / 2)
            end_point = (int(center[0] + length*np.cos(theta)), int(center[1] + length*np.sin(-1*theta)))
            cv2.line(outlined_tags, center, end_point, (0,0,255), 3)

        #Display video stream
        cv2.imshow(video_stream_title, outlined_tags)
        
        #Update framerate on vehicle UI
        fps = int(1 / (current_time - previous_time))
        previous_time = current_time
        imgui.text("Framerate: " + str(fps))
        imgui.text("Angle: " + str(angle))

        #Vehicle UI end
        imgui.end()
        
        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(gui)

        #Can close window on Ctrl+C
        if cv2.waitKey(1) == ord('q'):
            break

    #Release video and close windows
    camera.release()
    cv2.destroyAllWindows()

    #Destroy vehicle UI window
    impl.shutdown()
    glfw.terminate()

if __name__ == '__main__':
    main_camera()