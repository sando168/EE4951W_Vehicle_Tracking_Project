# Author: Logan O'Connell
# Date created: 4/3/2023
# Date modified: 4/3/2023
# Description: A file to store constants used throughout the
#              Controller.py file
# Dependencies: None

# The following constants are used in main_camera.py
HOST = "10.131.91.207"              # Server IP Address
PORT = 65432                        # Server Port

GUI_WIDTH = 480                     #Pixels
GUI_HEIGHT = 480                    #Pixels
RESOLUTION_WIDTH = 1920             #Pixels
RESOLUTION_HEIGHT = 768             #Pixels
FRAMERATE = 30                      #Frames Per Second
TAG_GRID_SIZE = 8                   #Number of grid spaces along edge of AprilTag
AREA_WIDTH = 4                      #Feet
AREA_HEIGHT = 2.0                   #Feet

OUTLINE_TAGS = False                #On screen, mark detected tags
OUTLINE_ANGLE = False               #On screen, mark orientation vector on detected tags
SHOW_TAG_IDENTIFICATION = False     #On screen, show sampled points of 1 detected tag
LIST_TAGS = True                    #On GUI, list the relevant tag information of added tags

#Don't change these variables
#Dynamically change within main_camera.py
USE_CAMERA = True                   
PIC_TO_USE = "Examples/apriltag_test.png"
DETECT_BOUNDARIES = False
ADD_TAG_FUNC = False
added_tag_ip = ""