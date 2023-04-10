# Author: Logan O'Connell
# Date created: 4/3/2023
# Date modified: 4/3/2023
# Description: A file to store constants used throughout the
#              Controller.py file
# Dependencies: None

HOST = "192.168.0.1" # The ip address of the host, possibly unnecessary
V1ADDRESS = "10.131.105.157" # The ip address of vehicle 1
PYADDRESS = "10.0.0.72"
PYPORT = 80
PORT = 23 # The port to connect to

# The following constants are used in main_camera.py
GUI_WIDTH = 480
GUI_HEIGHT = 480
RESOLUTION_WIDTH = 1920
RESOLUTION_HEIGHT = 768
FRAMERATE = 30
TAG_GRID_SIZE = 8
AREA_WIDTH = 4      #4ft
AREA_HEIGHT = 2.5   #2.5ft
OUTLINE_TAGS = False
OUTLINE_ANGLE = False
SHOW_TAG_IDENTIFICATION = False
LIST_TAGS = True
USE_CAMERA = True
PIC_TO_USE = "apriltag_test.png"

DETECT_BOUNDARIES = False