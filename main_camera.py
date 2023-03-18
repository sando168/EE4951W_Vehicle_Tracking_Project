
import cv2
import apriltag
import numpy as np
from bitstring import BitArray

import imgui
import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import time

#Macros that remain constant
GUI_WIDTH = 480
GUI_HEIGHT = 480
RESOLUTION_WIDTH = 1024
RESOLUTION_HEIGHT = 768
TAG_GRID_SIZE = 8
AREA_WIDTH = 4      #4ft
AREA_HEIGHT = 2.5   #2.5ft
OUTLINE_TAGS = False
OUTLINE_ANGLE = False
SHOW_TAG_IDENTIFICATION = False
video_stream_title = 'Vehicle Tracking'                 #Title of tracking window
camera = cv2.VideoCapture(0)                            #Open video camera
tag_detector = apriltag.Detector()                      #Create tag detection object

class ATag:
    descriptor = 'tag'
    id = BitArray(0)
    position = (0,0)
    angle = 0.0

    def __init__ (self, descr, id, pos, angle):
        self.descriptor = descr
        self.id = id
        self.position = pos
        self.angle = angle

#Dynamic array of detected tags including the tags outlining the boundaries of the play field
#The first three entries in the array are fixed in the order below
world_coordinate = ATag('world_coordinate', BitArray(0), (RESOLUTION_WIDTH,0), 0)
top_bound =        ATag('top_bound',        BitArray(0), (RESOLUTION_WIDTH,RESOLUTION_HEIGHT), 0)
right_bound =      ATag('right_bound',      BitArray(0), (0,0), 0)
detected_tags = [world_coordinate, top_bound, right_bound]

#Setup function for creating vehicle UI window
def setup_gui():

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
    gui = glfw.create_window(GUI_WIDTH, GUI_HEIGHT+100, "Vehicle UI", None, None)
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
        exit(1)
    else:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)

#Setup function for determining the boundary tags within the frame
#Can be called by user within the UI for resetting bounds
def auto_detect_boundaries():
    
    global detected_tags

    #Retrieve new frame from camera
    ret, new_frame = camera.read()

    #Check if new_frame is correct
    if not(ret):
        print('ERROR: Invalid new camera frame')
        exit(1)

    #Convert new frame to gray scale
    new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

    #Detect AprilTags
    tags = tag_detector.detect(new_frame_gray)

    #Iterate for each tag detected
    for tag in tags:

        cropped_tag = new_frame_gray
        
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

        #Solve tag ID by setting black squares = 0 and white squares = 1
        #Create bit string with MSB in top left, and LSB in bottom right

        #1. Using the detected corners on the tag, set target corners to warp the tag corners to
        target_corners = np.float32([[1,1],
                                        [1, RESOLUTION_HEIGHT-1],
                                        [RESOLUTION_WIDTH-1, RESOLUTION_HEIGHT-1],
                                        [RESOLUTION_WIDTH-1, 1]])
        corners_h = np.float32(corners)
        tag_homography = cv2.getPerspectiveTransform(corners_h, target_corners)
        cropped_tag = new_frame_gray
        cropped_tag = cv2.warpPerspective(cropped_tag, tag_homography, (RESOLUTION_WIDTH,RESOLUTION_HEIGHT), flags=cv2.INTER_LINEAR)
        #cropped_tag_gray = cv2.cvtColor(cropped_tag, cv2.COLOR_BGR2GRAY)

        #2. Iterate across squares on tag grid sampling from top left to bottom right
        #Iterate across rows of pixels
        height_step = int(RESOLUTION_WIDTH/TAG_GRID_SIZE)
        width_step = int(RESOLUTION_HEIGHT/TAG_GRID_SIZE)
        id = BitArray(0)
        for i in range(int(height_step/2), RESOLUTION_WIDTH-1, height_step):

            #Iterate across columns of pixels
            for j in range(int(width_step/2), RESOLUTION_HEIGHT-1, width_step):

                #White grid space
                if (cropped_tag[j][i] >= 90):
                    id.append('0b1')
                #Black grid space
                else:
                    id.append('0b0')

        #Determine world coordinate and top boundary by left most boundaries
        if center[0] < detected_tags[1].position[0] or center[0] < detected_tags[0].position[0]:

            #Top Boundary
            if center[1] < detected_tags[1].position[1]:
                detected_tags[1].id = id
                detected_tags[1].position = center
                detected_tags[1].angle = angle

            #World Coordinate
            else:
                detected_tags[0].id = id
                detected_tags[0].position = center
                detected_tags[0].angle = angle

        #Right Boundary
        elif center[0] > detected_tags[2].position[0]:
            detected_tags[2].id = id
            detected_tags[2].position = center
            detected_tags[2].angle = angle

#Bind IP address to tag ID by capturing image of tag
#Called by user when they push UI button
def bind_tag_to_IP(ip_addr):
    print(ip_addr)


#Start of Camera Code
def main_camera():
    global OUTLINE_TAGS
    global OUTLINE_ANGLE
    global SHOW_TAG_IDENTIFICATION
    global detected_tags

    #Setup functions
    setup_camera()
    gui = setup_gui()
    imgui.create_context()
    #imgui.get_io().display_size = GUI_WIDTH, GUI_HEIGHT
    imgui.get_io().fonts.get_tex_data_as_rgba32()
    impl = GlfwRenderer(gui)
    auto_detect_boundaries()

    #Time variables for measuring framerate
    previous_time = 1
    current_time = 1
    #Start of while(1) loop that runs forever
    while not(glfw.window_should_close(gui)) and camera.isOpened():

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
        id = BitArray(0)
        angle = 0
        imgui.begin_child("Detected Tags")
        for tag in tags:

            outlined_tags = new_frame
            id = BitArray(0)

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

            #Solve tag ID by setting black squares = 0 and white squares = 1
            #Create bit string with MSB in top left, and LSB in bottom right
            #1. Using the detected corners on the tag, set target corners to warp the tag corners to
            target_corners = np.float32([[1,1],
                                         [1, RESOLUTION_HEIGHT-1],
                                         [RESOLUTION_WIDTH-1, RESOLUTION_HEIGHT-1],
                                         [RESOLUTION_WIDTH-1, 1]])
            corners_h = np.float32(corners)
            tag_homography = cv2.getPerspectiveTransform(corners_h, target_corners)
            cropped_tag = outlined_tags
            cropped_tag = cv2.warpPerspective(cropped_tag, tag_homography, (RESOLUTION_WIDTH,RESOLUTION_HEIGHT), flags=cv2.INTER_LINEAR)
            cropped_tag_gray = cv2.cvtColor(cropped_tag, cv2.COLOR_BGR2GRAY)

            #2. Iterate across squares on tag grid sampling from top left to bottom right
            #Iterate across rows of pixels
            height_step = int(RESOLUTION_WIDTH/TAG_GRID_SIZE)
            width_step = int(RESOLUTION_HEIGHT/TAG_GRID_SIZE)
            for i in range(int(height_step/2), RESOLUTION_WIDTH-1, height_step):

                #Iterate across columns of pixels
                for j in range(int(width_step/2), RESOLUTION_HEIGHT-1, width_step):

                    #White grid space
                    if (cropped_tag_gray[j][i] >= 90):
                        id.append('0b1')
                    #Black grid space
                    else:
                        id.append('0b0')

                    if SHOW_TAG_IDENTIFICATION:
                        cropped_tag_gray = cv2.circle(cropped_tag_gray, (i,j), 4, (255,0,0), 2)

            #Solve for angular rotation
            x = upper_right_corner[0] - upper_left_corner[0]
            y = upper_left_corner[1] - upper_right_corner[1]
            theta = np.arctan2(y, x)
            angle = np.rad2deg(theta)

            #Transform center coordinates from (U,V) -> (X,Y)
            center_img = center
            center = (center[0], RESOLUTION_HEIGHT-center[1])

            #Transform center coordinates from (X,Y) -> Reference to origin
            origin = (detected_tags[0].position[0], RESOLUTION_HEIGHT-detected_tags[0].position[1])
            center = (center[0]-origin[0], center[1]-origin[1])

            #Transform center coordinates from pixels -> unit dimensions
            x_dimension_per_pixel = AREA_WIDTH / detected_tags[2].position[0]
            y_dimension_per_pixel = AREA_HEIGHT / detected_tags[1].position[1]
            center[0] = center[0] / x_dimension_per_pixel
            center[1] = center[1] / y_dimension_per_pixel

            #Draw the arbitrary contour from corners since the tag could be rotated
            if OUTLINE_TAGS:
                if id == detected_tags[0].id:
                    cv2.putText(outlined_tags, 'Origin', (center_img[0]+25, center_img[1]+10), cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                    cv2.drawContours(outlined_tags, [corners], 0, (0,255,0), 3)
                elif id == detected_tags[1].id:
                    cv2.putText(outlined_tags, 'Top', (center_img[0]+25, center_img[1]+10), cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                    cv2.drawContours(outlined_tags, [corners], 0, (0,255,0), 3)
                elif id == detected_tags[2].id:
                    cv2.putText(outlined_tags, 'Right', (center_img[0]+25, center_img[1]+10), cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                    cv2.drawContours(outlined_tags, [corners], 0, (0,255,0), 3)
                else:
                    cv2.drawContours(outlined_tags, [corners], 0, (255,0,0), 3)
            elif SHOW_TAG_IDENTIFICATION:
                outlined_tags = cropped_tag_gray

            #Draw red line from center of tag to indicate angle
            if OUTLINE_ANGLE:
                length = np.linalg.norm(np.array([x, y]))
                length = int(length / 2)
                end_point = (int(center_img[0] + length*np.cos(theta)), int(center_img[1] + length*np.sin(-1*theta)))
                cv2.line(outlined_tags, center_img, end_point, (0,0,255), 3)

            #Create UI information for each tag
            imgui.text("\n")
            imgui.text(str(id))
            imgui.text("Center: (" + str(center[0]) + ", " + str(center[1]) + ")")
            imgui.text("Angle: " + str(angle))
            imgui.text("\n")

        #Display video stream
        cv2.imshow(video_stream_title, outlined_tags)
        
        #Update data on vehicle UI
        fps = int(1 / (current_time - previous_time))
        previous_time = current_time
        imgui.text("Framerate: " + str(fps))

        #Re-Auto Detect Boundaries Button
        if imgui.button('Detect Bounds'):
            auto_detect_boundaries()

        ip_addr = 'IP Address'
        imgui.input_text('0.0.0.0', ip_addr, 50)
        imgui.same_line()
        if imgui.button('Capture'):
            bind_tag_to_IP(ip_addr)

        #Create vehicle UI checkboxes
        _, OUTLINE_TAGS = imgui.checkbox("Outline Tags", OUTLINE_TAGS)
        _, OUTLINE_ANGLE = imgui.checkbox("Outline Angles", OUTLINE_ANGLE)
        _, SHOW_TAG_IDENTIFICATION = imgui.checkbox("Tag Identification", SHOW_TAG_IDENTIFICATION)

        #Vehicle UI end
        imgui.end_child()
        imgui.end()
        
        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(gui)

        #Can close window on ESC
        if cv2.waitKey(1) == 27:
            break

    #Release video and close windows
    camera.release()
    cv2.destroyAllWindows()

    #Destroy vehicle UI window
    impl.shutdown()
    glfw.terminate()

if __name__ == '__main__':
    main_camera()