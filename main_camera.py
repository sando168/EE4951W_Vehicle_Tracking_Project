import socket
import cv2
import pupil_apriltags as apriltag
import numpy as np
import json
import os
from tkinter import *
from tkinter import filedialog
from bitstring import BitArray
from Constants import *
import threading

import imgui
import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import time

def globalSetup():
    global video_stream_title 
    video_stream_title = 'Vehicle Tracking'                 #Title of tracking window
    global camera
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)                          #Open video camera
    global tag_detector
    tag_detector = apriltag.Detector()                      #Create tag detection object
    global current_time
    current_time = 1.0
    global previous_time
    previous_time = 1.0

    #Dynamic array of detected tags including the tags outlining the boundaries of the play field
    #The first three entries in the array are fixed in the order below
    global world_coordinate
    world_coordinate = ATag('world_coordinate', BitArray(0), (RESOLUTION_WIDTH,0), 0, (0,0))
    global top_bound
    top_bound =        ATag('top_bound',        BitArray(0), (RESOLUTION_WIDTH,RESOLUTION_HEIGHT), 0, (0,0))
    global right_bound
    right_bound =      ATag('right_bound',      BitArray(0), (0,0), 0, (0,0))
    global detected_tags
    detected_tags = [world_coordinate, top_bound, right_bound]

class ATag:
    descriptor = 'tag'
    id = BitArray(0)
    position = (0,0)
    desired_pos = (0,0)
    angle = 0.0

    def __init__ (self, descr, id, pos, angle, des):
        self.descriptor = descr
        self.id = id
        self.position = pos
        self.angle = angle
        self.desired_pos = des
        self.desired_distance = 0.0
        self.desired_angle = 0.0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
    
    def sendData(self, data):
        """Helper function to send data to the vehicle.

        Parameters
        ----------
        data : str
            The data to be sent to the vehicle
        """
        if not self.connected:
            self.sock.connect((self.descriptor, PORT))
            self.connected = True
            print("Connected to {}".format(self.descriptor))
        # IDK why but the data needs to be encoded, otherwise it doesn't work
        # The current implementation of this function is leaving the connection
        # open the entire time. The alternative is to open and close the connection
        # using line 50 every time sendData() is called.
        self.sock.sendall(data.encode())
    def sendDataClose(self, data):
        """Helper function to send data to the vehicle.

        Parameters
        ----------
        data : str
            The data to be sent to the vehicle
        """
        if not self.connected:
            self.sock.connect((self.descriptor, PORT))
            self.sock.sendall(data.encode())
            self.connected = True
            self.sock.close()
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.descriptor, PORT))
            self.sock.sendall(data.encode())
            self.sock.close()
    def recieveData(self):
        """Recieves data from the vehicle.

        Returns
        -------
        str
            The data recieved from the vehicle
        """

        return self.sock.recv(1024)
    def updateVehiclePosition(self):
        """Sends the updated position of the vehicle to the vehicle."""

        self.sendData("u {x} {y} {r}".format(x=self.position[0],y=self.position[1],r=self.angle))
        # print("updateVehiclePosition() Sent!") #TODO: Remove this
    def moveToPoint(self):
        """Moves the vehicle to the specified point."""

        self.sendData("d {x} {y}".format(self.desired_pos[0],self.desired_pos[1]))
        print("moveToPoint({},{}) Sent!".format(self.desired_pos[0], self.desired_pos[1])) #TODO: Remove this
    def moveDistance(self):
        """Moves the vehicle a specified distance. FOR TESTING ONLY."""

        self.sendData("m {}".format(self.desired_distance))
        print("moveDistance() Sent!")
    def rotate(self):
        """Rotates the vehicle a specified angle. FOR TESTING ONLY."""

        self.sendData("r {}".format(self.desired_angle))
        print("rotate() Sent!")

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

#Run GUI window in a separate thread
def run_gui():

    global OUTLINE_TAGS
    global OUTLINE_ANGLE
    global SHOW_TAG_IDENTIFICATION
    global LIST_TAGS
    global USE_CAMERA
    global DETECT_BOUNDARIES
    global detected_tags
    global previous_time
    global current_time

    gui = setup_gui()

    imgui.create_context()
    imgui.get_io().fonts.get_tex_data_as_rgba32()
    impl = GlfwRenderer(gui)

    #Time variables for measuring framerate
    ip_addr = 'IP Address'
    filename = 'Filename'
    set_pos = '0,0'
    while not(glfw.window_should_close(gui)):

        #Begin UI window events
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()
        imgui.begin("Vehicle UI")

        #Update data on vehicle UI
        fps = int(1 / (current_time - previous_time + 0.00000001))
        imgui.text("Framerate: " + str(fps))

        #Re-Auto Detect Boundaries Button
        if imgui.button('Detect Bounds'):
            DETECT_BOUNDARIES = True

        #Capture and add new tag UI
        has_changed, ip_addr = imgui.input_text('##ip', ip_addr, 50, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        imgui.same_line()
        if imgui.button('Capture'):
            add_tag(ip_addr)

        #Save list and open list of tags UI
        has_changed, filename = imgui.input_text('##file', filename, 50, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        imgui.same_line()
        if imgui.button('Save'):
            save_tags(filename)
        imgui.same_line()
        if imgui.button('Open'):
            open_tags()

        #Create vehicle UI checkboxes
        _, OUTLINE_TAGS = imgui.checkbox("Outline Tags", OUTLINE_TAGS)
        _, OUTLINE_ANGLE = imgui.checkbox("Outline Angles", OUTLINE_ANGLE)
        _, SHOW_TAG_IDENTIFICATION = imgui.checkbox("Tag Identification", SHOW_TAG_IDENTIFICATION)
        _, LIST_TAGS = imgui.checkbox("List Tags", LIST_TAGS)

        #Update list of added tags
        for added_tag in detected_tags:
                
            #Display tag information on UI if selected
            if LIST_TAGS:
                imgui.text("\n")
                imgui.text(added_tag.descriptor)
                imgui.text(str(added_tag.id))

                center = (added_tag.position[0], RESOLUTION_HEIGHT-added_tag.position[1])

                #Transform center coordinates from (X,Y) -> Reference to origin
                origin = (detected_tags[0].position[0], RESOLUTION_HEIGHT-detected_tags[0].position[1])
                center = (center[0]-origin[0], center[1]-origin[1])

                #Transform center coordinates from pixels -> unit dimensions (ft, cm)
                x_dimension_per_pixel = AREA_WIDTH / (detected_tags[2].position[0] - origin[0] + 0.000001)
                y_dimension_per_pixel = AREA_HEIGHT / (detected_tags[0].position[1] - detected_tags[1].position[1] + 0.000001)
                center = (center[0]*x_dimension_per_pixel, center[1]*y_dimension_per_pixel)

                imgui.text("Center: (" + "{:.2f}".format(center[0]) + ", " + "{:.2f}".format(center[1]) + ")")
                imgui.text("Angle: " + "{:.2f}".format(added_tag.angle))

                #Display desired position on UI
                if  added_tag.id != detected_tags[0].id  and added_tag.id != detected_tags[1].id  and added_tag.id != detected_tags[2].id:
                    imgui.text("Target: (" + "{:.2f}".format(added_tag.desired_pos[0]) + ", " + "{:.2f}".format(added_tag.desired_pos[1]) + ")")

                #Retrieve and display desired position from input text box
                has_changed = False
                if  added_tag.id != detected_tags[0].id  and added_tag.id != detected_tags[1].id  and added_tag.id != detected_tags[2].id:
                    has_changed, set_pos = imgui.input_text('##target'+str(added_tag.id), 'Desired Pos x,y', 50, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
                if has_changed:
                    try:
                        coords = tuple(map(float, set_pos.split(',')))
                        #Check for valid input
                        if len(coords) == 2:
                            #Check if input is in play area bounds
                            if 0.0 <= coords[0] and coords[0] <= AREA_WIDTH and 0 <= coords[1] and coords[1] <= AREA_HEIGHT:
                                added_tag.desired_pos = coords
                                added_tag.moveToPoint()
                            else:
                                print('ERROR: Unable to set position. Not within pleay area bounds.')
                    except:
                        print('ERROR: Unable to set position. Input should be 2 numbers separated by a comma. Input: ' + set_pos)
                
                
                # Retrieve and display distance to go from input text box TESTING ONLY
                has_changed=False
                if  added_tag.id != detected_tags[0].id  and added_tag.id != detected_tags[1].id  and added_tag.id != detected_tags[2].id:
                    has_changed, go_dist = imgui.input_text('##distance'+str(added_tag.id), 'TESTING Go Distance', 50, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
                    if has_changed:
                        try:
                            dist = float(go_dist)
                            #Check for valid input
                            if dist > 0:
                                added_tag.desired_distance = dist
                                added_tag.moveDistance()
                            else:
                                print('ERROR: Unable to set go distance. Not a positive number.')
                        except:
                            print('ERROR: Unable to set go distance. Input should be a positive number.')
            
                # Retrieve and display an angle to rotate to from input text box TESTING ONLY
                has_changed=False
                if  added_tag.id != detected_tags[0].id  and added_tag.id != detected_tags[1].id  and added_tag.id != detected_tags[2].id:
                    has_changed, go_angle = imgui.input_text('##angle'+str(added_tag.id), 'TESTING Go Angle', 50, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
                    if has_changed:
                        try:
                            angle = float(go_angle)
                            #Check for valid input
                            if dist > 0 and dist < 360:
                                added_tag.desired_angle = angle
                                added_tag.rotate()
                            else:
                                print('ERROR: Unable to set go angle. Not a positive number.')
                        except:
                            print('ERROR: Unable to set go angle. Input should be a positive number.')

        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.end()
        imgui.render()
        imgui.end_frame()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(gui)

    #Destroy vehicle UI window
    impl.shutdown()
    glfw.terminate()

#Setup function before streaming video
def setup_camera():

    #Error and stop program if not connected
    if not(camera.isOpened()):
        print('ERROR: Unable to connect to camera')
        return False
    else:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS, FRAMERATE)
        # camera.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_RAW_RES[0])
        # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_RAW_RES[1])
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")) # add this line
        return True

#Iterate over AprilTags in camera frame
def process_tags(tags, new_frame):

    #Outline each detected tag with a square
    id = BitArray(0)
    angle = 0
    for tag in tags:

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
        # cropped_tag = outlined_tags
        cropped_tag = cv2.warpPerspective(new_frame, tag_homography, (RESOLUTION_WIDTH,RESOLUTION_HEIGHT), flags=cv2.INTER_LINEAR)
        # cropped_tag_gray = cv2.cvtColor(cropped_tag, cv2.COLOR_BGR2GRAY)

        #2. Iterate across squares on tag grid sampling from top left to bottom right
        #Iterate across rows of pixels
        height_step = int(RESOLUTION_WIDTH/TAG_GRID_SIZE)
        width_step = int(RESOLUTION_HEIGHT/TAG_GRID_SIZE)
        for i in range(int(height_step/2), RESOLUTION_WIDTH-1, height_step):

            #Iterate across columns of pixels
            for j in range(int(width_step/2), RESOLUTION_HEIGHT-1, width_step):

                #White grid space
                if (cropped_tag[j][i] >= 90):
                    id.append('0b1')
                #Black grid space
                else:
                    id.append('0b0')

                if SHOW_TAG_IDENTIFICATION:
                    cropped_tag = cv2.circle(cropped_tag, (i,j), 4, (255,0,0), 2)

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

        #Transform center coordinates from pixels -> unit dimensions (ft, cm)
        x_dimension_per_pixel = AREA_WIDTH / (detected_tags[2].position[0] - origin[0] + 0.000001)
        y_dimension_per_pixel = AREA_HEIGHT / (detected_tags[0].position[1] - detected_tags[1].position[1] + 0.000001)
        center = (center[0]*x_dimension_per_pixel, center[1]*y_dimension_per_pixel)

        #Update list of added tags
        for added_tag in detected_tags:
            if added_tag.id == str(id) and added_tag.id != detected_tags[0].id  and added_tag.id != detected_tags[1].id  and added_tag.id != detected_tags[2].id:
                if(added_tag.angle != angle or added_tag.position != center):
                    added_tag.angle = angle
                    added_tag.position = center
                    added_tag.updateVehiclePosition()

        #Draw the arbitrary contour from corners since the tag could be rotated
        if OUTLINE_TAGS:
            if id == detected_tags[0].id:
                cv2.putText(new_frame, 'Origin', (center_img[0]+25, center_img[1]+10), cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                cv2.drawContours(new_frame, [corners], 0, (0,255,0), 3)
            elif id == detected_tags[1].id:
                cv2.putText(new_frame, 'Top', (center_img[0]+25, center_img[1]+10), cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                cv2.drawContours(new_frame, [corners], 0, (0,255,0), 3)
            elif id == detected_tags[2].id:
                cv2.putText(new_frame, 'Right', (center_img[0]+25, center_img[1]+10), cv2.FONT_HERSHEY_DUPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                cv2.drawContours(new_frame, [corners], 0, (0,255,0), 3)
            else:
                cv2.drawContours(new_frame, [corners], 0, (255,0,0), 3)
        elif SHOW_TAG_IDENTIFICATION:
            new_frame = cropped_tag

        #Draw red line from center of tag to indicate angle
        if OUTLINE_ANGLE:
            length = np.linalg.norm(np.array([x, y]))
            length = int(length / 2)
            end_point = (int(center_img[0] + length*np.cos(theta)), int(center_img[1] + length*np.sin(-1*theta)))
            cv2.line(new_frame, center_img, end_point, (0,0,255), 3)

#Setup function for determining the boundary tags within the frame
#Can be called by user within the UI for resetting bounds
def auto_detect_boundaries():
    
    global detected_tags

    #Retrieve new frame from camera
    ret = None
    new_frame = None
    if USE_CAMERA:
        ret, new_frame = camera.read()
    else:
        new_frame = cv2.imread(PIC_TO_USE)
        ret = True

    #Check if new_frame is correct
    if not(ret):
        print('ERROR: Invalid new camera frame')
        exit(1)

    #Convert new frame to gray scale
    new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

    #Detect AprilTags
    tags = tag_detector.detect(new_frame_gray)

    #Need at least 3 tags for boundaries
    if len(tags) < 3:
        print('ERROR: Unable to detect boundaries. Only ' + str(len(tags)) + ' detected. Need at least 3 tags.')
        return

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
#Called by user when they push UI "Capture" button
def add_tag(ip_addr):

    global detected_tags

    #Retrieve new frame from camera
    ret = None
    new_frame = None
    if USE_CAMERA:
        ret, new_frame = camera.read()
    else:
        new_frame = cv2.imread(PIC_TO_USE)
        ret = True

    #Check if new_frame is correct
    if not(ret):
        print('ERROR: Invalid new camera frame')
        exit(1)

    #Convert new frame to gray scale
    new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

    #Detect AprilTags
    tags = tag_detector.detect(new_frame_gray)

    #Should only see 1 tag when adding
    if len(tags) > 1:
        print('ERROR: Unable to add tag. Multiple tags detected.')
        return
    elif len(tags) == 0:
        print('ERROR: Unable to add tag. None detected')
        return

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

    new_tag = ATag(ip_addr, id, (0,0), 0, (0,0))

    #Check if tag has already been added
    for tag in detected_tags:
        if tag.id == new_tag.id:
            print('ERROR: Unable to add tag. Already added.')
            return

    detected_tags.append(new_tag)

#Save all added tags to JSON file
#Called by user when they push UI "Save" button
def save_tags(filename):

    #Iterate over array of vehicle and boundary tags
    with open(filename + '.json', 'w') as outfile:
        outfile.write("{ \"tags\": [")

        for tag in detected_tags:
            json_data =  {
                "name" : str(tag.descriptor),
                "id" : str(tag.id),
                "position" : tag.position,
                "angle" : tag.angle,
                "desired pos": tag.desired_pos
            }
            json_data = json.dumps(json_data, indent=4)
            outfile.write(json_data)
            if tag != detected_tags[len(detected_tags)-1]:
                outfile.write(', ')

        outfile.write("]}")
    
#Open and load configuration file with already added tags
#Called by user when they push "Open" UI button
def open_tags():

    #Select file with explorer and return specific string
    config_file = filedialog.askopenfilename(title="Select a json file", filetypes=[("JSON files", "*.json*")])

    #Open selected file
    with open(config_file, "r") as openfile:
        json_object = json.load(openfile)
        json_object = json_object['tags']

        #Iterate through each tag in JSON file and add to detected_tags
        detected_tags.clear()
        for tag in json_object:
            new_tag = ATag(tag["name"], tag["id"], tag["position"], tag["angle"], tag["desired pos"])
            detected_tags.append(new_tag)
    
    print(len(detected_tags))

#Start of Camera Code
def main_camera(commBuf=None):

    global OUTLINE_TAGS
    global OUTLINE_ANGLE
    global SHOW_TAG_IDENTIFICATION
    global LIST_TAGS
    global USE_CAMERA
    global DETECT_BOUNDARIES
    global detected_tags
    global previous_time
    global current_time

    #Setup functions
    globalSetup()
    USE_CAMERA = setup_camera()
    gui_thread = threading.Thread(target=run_gui, args=())
    gui_thread.start()
    auto_detect_boundaries()

    #Start of while(1) loop that runs forever
    while True:

        #Retrieve new frame from camera
        ret = None
        new_frame = None
        if USE_CAMERA:
            ret, new_frame = camera.read()
        else:
            new_frame = cv2.imread(PIC_TO_USE)
            ret = True

        #Check if new_frame is correct
        if not(ret):
            break

        #Check UI events within separate thread
        if DETECT_BOUNDARIES:
            auto_detect_boundaries()
            DETECT_BOUNDARIES = False
        
        #Convert new frame to gray scale
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

        #Detect AprilTags
        tags = tag_detector.detect(new_frame_gray)

        #Process tags in camera frame within a non-blocking thread
        tag_processing_thread = threading.Thread(target=process_tags, args=(tags,new_frame_gray))
        tag_processing_thread.start()
        tag_processing_thread.join()

        #Display video stream
        cv2.imshow(video_stream_title, new_frame_gray)

        #Can close window on ESC
        if cv2.waitKey(1) == 27:
            break

        #Update timers for FPS
        previous_time = current_time
        current_time = time.perf_counter()

    #Release video and close windows
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_camera()
    glfw.terminate()