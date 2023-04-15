# Author: Logan O'Connell
# Date created: 4/3/2023
# Date modified: 4/4/2023
# Description: The controller for the vehicle. Handles all communication
#              with the vehicle(s) and the vision system.
# Dependencies: Constants.py

import socket
import threading as th
import cv2
import pupil_apriltags as apriltag
import numpy as np
import json
import os
import imgui
import glfw
import OpenGL.GL as gl
import time
from tkinter import *
from tkinter import filedialog
from bitstring import BitArray
from Constants import *
from queue import Queue
from imgui.integrations.glfw import GlfwRenderer
from main import *
from Examples.vision_dummy import * # TODO: Remove this

class Vehicle:
    """A class used to represent a vehicle"""

    def __init__(self, name="Vehicle 1", x=None, y=None, r=None, ipAdress=None):
        """Constructor for the Vehicle class.
        
        Parameters
        ----------
        ipAdress : str
            The ip address of the vehicle(Defaults to None)
        x : int
            The x coordinate of the vehicle(Defaults to None)
        y : int
            The y coordinate of the vehicle(Defaults to None)
        r : int
            The rotation of the vehicle(Defaults to None)
        """

        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.adr = ipAdress
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendData(self, data):
        """Helper function to send data to the vehicle.

        Parameters
        ----------
        data : str
            The data to be sent to the vehicle
        """

        self.sock.connect((self.adr, PORT))
        # IDK why but the data needs to be encoded, otherwise it doesn't
        # work
        self.sock.sendall(data.encode())
    def recieveData(self):
        """Recieves data from the vehicle.

        Returns
        -------
        str
            The data recieved from the vehicle
        """

        return self.sock.recv(1024)
    def setPosition(self,x,y,r):
        """Sets the local position of the vehicle.

        Parameters
        ----------
        x : int
            The x coordinate of the vehicle
        y : int
            The y coordinate of the vehicle
        r : int
            The rotation of the vehicle
        """
        
        self.x = x
        self.y = y
        self.r = r
    def updatePosition(self,x,y,r):
        """Updates the position of the vehicle if it has changed.
        
        Parameters
        ----------
        x : int
            The x coordinate of the vehicle
        y : int
            The y coordinate of the vehicle
        r : int
            The rotation of the vehicle
        """

        if x != self.x or y != self.y or r != self.r:
            self.setPosition(x,y,r)
    def updateVehiclePosition(self):
        """Sends the updated position of the vehicle to the vehicle."""

        self.sendData("u {x} {y} {r}".format(x=self.x,y=self.y,r=self.r))
        # print("updateVehiclePosition() Sent!") #TODO: Remove this
    def getPosition(self):
        """Returns the position of the vehicle."""
        return(self.x,self.y,self.r)
    def moveToPoint(self,x,y):
        """Moves the vehicle to the specified point.
        
        Parameters
        ----------
        x : int
            The x coordinate of the point
        y : int
            The y coordinate of the point
        """

        # self.sendData("d {x} {y}".format(x,y))
        print("moveToPoint({},{}) Sent!".format(x,y)) #TODO: Remove this
    def moveDistance(self, distance):
        """Moves the vehicle a specified distance. FOR TESTING ONLY.
        
        Parameters
        ----------
        distance : int
            The distance to move the vehicle
        """

        # self.sendData("m {}".format(distance))
        print("moveDistance() Sent!")
    def rotate(self, angle):
        """Rotates the vehicle a specified angle. FOR TESTING ONLY.
        
        Parameters
        ----------
        angle : int
            The angle to rotate the vehicle
        """

        # self.sendData("r {}".format(angle))
        print("rotate() Sent!") #TODO: Remove this

def setup():
    """Sets up the controller and vehicle. Starts Controller Thread.
    
    Global is used here to make the variables accessible to main()."""

    #TODO: Make modular
    global v1 # Vehicle 1
    v1 = Vehicle(ipAdress=V1ADDRESS)
    global tmp # Input storage variable
    tmp = ""
    global mTCBuf # Main to Controller Queue
    mTCBuf = Queue()
    global cTMBuf # Controller to Main Queue
    cTMBuf = Queue()
    global xBuf # X coordinate Queue
    xBuf = Queue()
    global yBuf # Y coordinate Queue
    yBuf = Queue()
    global rBuf # Rotation Queue
    rBuf = Queue()
    global visionBuf # Vision Queue TODO: implement vision
    visionBuf = Queue()
    global mainToController # Main to Controller Condition
    mainToController = th.Condition()
    global controllerToMain # Controller to Main Condition
    controllerToMain = th.Condition()
    global controlThread # Controller Thread
    controlThread = th.Thread(target=controller, args=(mTCBuf, cTMBuf, xBuf,
                                                        yBuf, rBuf, visionBuf,
                                                        v1, mainToController,
                                                        controllerToMain))
    controlThread.start()

    global xComBuf # x coordinate communication buffer
    xComBuf = Queue()
    global yComBuf # y coordinate communication buffer
    yComBuf = Queue()
    global rComBuf # rotation communication buffer
    rComBuf = Queue()
    xComBuf.put(-1)
    yComBuf.put(-1)
    rComBuf.put(-1)

    global endBuf # End Condition for communication thread
    endBuf = Queue()
    global dummyThread # Dummy Thread
    dummyThread = th.Thread(target=dummy, args=(xComBuf, yComBuf, rComBuf, endBuf))
    dummyThread.start()
    
    global communicationThread # Communication Thread
    communicationThread = th.Thread(target=communicate, args=(v1, xComBuf, yComBuf, rComBuf, endBuf))
    communicationThread.start()

def communicate(vehicle, xComBuf, yComBuf, rComBuf, endBuf):
    """Line of communication between the vision system and the vehicle.
    
    Parameters
    ----------
    vehicle : Vehicle
        The vehicle object to communicate with
    xComBuf : Queue
        The x coordinate communication buffer
    yComBuf : Queue
        The y coordinate communication buffer
    rComBuf : Queue
        The rotation communication buffer
    endBuf : Queue
        The end condition for the thread
    """

    oldTempx, oldTempy, oldTempr = -2, -2, -2 # Initialize old values

    while endBuf.empty():
        # Gets new values and updates the vehicle if they have changed
        tempx = xComBuf.get() if not xComBuf.empty() else oldTempx
        tempy = yComBuf.get() if not yComBuf.empty() else oldTempy
        tempr = rComBuf.get() if not rComBuf.empty() else oldTempr

        if tempx != oldTempx or tempy != oldTempy or tempr != oldTempr:
            vehicle.updatePosition(tempx, tempy, tempr)
            vehicle.updateVehiclePosition()
            oldTempx = tempx
            oldTempy = tempy
            oldTempr = tempr

def controller(mTCBuf, cTMBuf, xBuffer, yBuffer, rBuffer, visionBuffer, vehicle,
               mTCCond, cTMCond):
    #TODO: Make modular
    """The controller thread. Handles all communication with the
    vehicle(s) and the vision system?
    
    Parameters
    ----------
    mTCBuf : Queue
        The queue for commands from main to controller
    cTMBuf : Queue
        The queue for data from controller to main
    xBuffer : Queue
        The queue for x coordinates from main to controller
    yBuffer : Queue
        The queue for y coordinates from main to controller
    rBuffer : Queue
        The queue for rotations from main to controller
    visionBuffer : Queue
        The queue for vision data from main to controller
    vehicle : Vehicle
        The vehicle object
    mTCCond : Condition
        The condition for main to controller
    cTMCond : Condition
        The condition for controller to main
    """
    
    while True:
        with mTCCond:
            mTCCond.wait()
        temp = mTCBuf.get()
        tempX = xBuffer.get() if not xBuffer.empty() else -1
        tempY = yBuffer.get() if not yBuffer.empty() else -1
        tempR = rBuffer.get() if not rBuffer.empty() else -1
        # Waits for an input and stores it in temps
        
        if temp == 1: # Exit
            break
        elif temp == 2: # Move to point
            vehicle.moveToPoint(tempX, tempY)
        elif temp == 3: # Get position
            cTMBuf.put(vehicle.getPosition())
            with cTMCond:
                cTMCond.notify()
        elif temp == 4: # Update position
            vehicle.updatePosition(tempX, tempY, tempR)
        elif temp == 5: # Move distance
            vehicle.moveDistance(tempX)
        elif temp == 6: # Rotate
            vehicle.rotate(tempX)
        else: # Invalid command, should never hit this, will error
            print("Invalid command")
    exit()

def main():
    setup()
    global tmp # Input storage variable, have to redeclare it here
    while 1:
        tmp = input("\nValid commands are: exit, moveToPoint, getPosition, "+
                    "updatePosition, moveDistance, rotate\nEnter a command:")
        # Waits for an input and stores it in tmp
        if tmp == "exit":
            mTCBuf.put(1)
            endBuf.put(1)
            with mainToController:
                mainToController.notify()
            controlThread.join()
            communicationThread.join()
            dummyThread.join()
            print("Exiting peacefully, all threads closed")
            exit()
        elif tmp == "moveToPoint":
            mTCBuf.put(2)
            xBuf.put(input("Enter x coordinate:"))
            yBuf.put(input("Enter y coordinate:"))
            with mainToController:
                mainToController.notify()
        elif tmp == "getPosition":
            mTCBuf.put(3)
            with mainToController:
                mainToController.notify()
            with controllerToMain:
                controllerToMain.wait()
            print("{vehicle_name}'s current position is {xy}.".format(
                vehicle_name=v1.name, xy=cTMBuf.get()))
        elif tmp == "updatePosition": # FOR TESTING ONLY #TODO: Remove this
            mTCBuf.put(4)
            xBuf.put(input("Enter x coordinate:"))
            yBuf.put(input("Enter y coordinate:"))
            rBuf.put(input("Enter r angle:"))
            with mainToController:
                mainToController.notify()
        elif tmp == "moveDistance": # FOR TESTING ONLY #TODO: Remove this
            mTCBuf.put(5)
            xBuf.put(input("Enter distance:"))
            with mainToController:
                mainToController.notify()
        elif tmp == "rotate": # FOR TESTING ONLY #TODO: Remove this
            mTCBuf.put(6)
            xBuf.put(input("Enter angle:"))
            with mainToController:
                mainToController.notify()
        else:
            print("Invalid command")



if __name__ == "__main__":
    main()