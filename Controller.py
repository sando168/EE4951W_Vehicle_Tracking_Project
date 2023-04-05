import socket
import threading as th
from time import sleep
import Constants
from queue import Queue

class Vehicle:
    """A class used to represent a vehicle"""

    def __init__(self, name="Vehicle 1", x=None, y=None, r=None, ipAdress=None):
        """Constructor for the Vehicle class
        
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
        self.sock.connect((self.adr, Constants.PORT))
        self.sock.sendall(data.encode())
    def recieveData(self):
        return self.sock.recv(1024)
    def setPosition(self,x,y,r):
        self.x = x
        self.y = y
        self.r = r
    def updatePosition(self,x,y,r):
        if x != self.x or y != self.y or r != self.r:
            self.setPosition(x,y,r)
    def updateVehiclePosition(self):
        # self.sendData("u {} {} {}".format(self.x,self.y,self.r))
        print("updateVehiclePosition() Sent!")
    def getPosition(self):
        return(self.x,self.y,self.r)
    def moveToPoint(self,x,y):
        # self.sendData("d {} {}".format(x,y))
        print("moveToPoint({},{}) Sent!".format(x,y))
    def moveDistance(self, distance):
        # self.sendData("m {}".format(distance))
        print("moveDistance() Sent!")
    def rotate(self, angle):
        # self.sendData("r {}".format(angle))
        print("rotate() Sent!")

def setup():
    global v1
    v1 = Vehicle(Constants.V1ADDRESS)
    global tmp 
    tmp = ""
    global mTCBuf
    mTCBuf = Queue()
    global cTMBuf
    cTMBuf = Queue()
    global xBuf 
    xBuf = Queue()
    global yBuf
    yBuf = Queue()
    global rBuf
    rBuf = Queue()
    global visionBuf
    visionBuf = Queue()
    global mainToController
    mainToController = th.Condition()
    global controllerToMain
    controllerToMain = th.Condition()
    global controlThread 
    controlThread = th.Thread(target=controller, args=(mTCBuf, cTMBuf, xBuf, yBuf, rBuf, visionBuf, v1,
                                                       mainToController, controllerToMain))
    controlThread.start()

def controller(mTCBuf, cTMBuf, xBuffer, yBuffer, rBuffer, visionBuffer, vehicle,
               mTCCond, cTMCond):
    while True:
        with mTCCond:
            mTCCond.wait()
        temp = mTCBuf.get()
        tempX = xBuffer.get() if not xBuffer.empty() else -1
        tempY = yBuffer.get() if not yBuffer.empty() else -1
        tempR = rBuffer.get() if not rBuffer.empty() else -1

        if temp == 1:
            break
        elif temp == 2:
            vehicle.moveToPoint(tempX, tempY)
        elif temp == 3:
            cTMBuf.put(vehicle.getPosition())
            with cTMCond:
                cTMCond.notify()
        elif temp == 4:
            vehicle.updatePosition(tempX, tempY, tempR)
        else:
            print("1Invalid command")
    exit()

def main():
    setup()
    global tmp
    while 1:
        tmp = input("\nValid commands are: exit, moveToPoint, getPosition\nEnter a command:")
        if tmp == "exit":
            mTCBuf.put(1)
            with mainToController:
                mainToController.notify()
            controlThread.join()
            print("Exiting peacefully")
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
            print("{}'s current position is {}.".format(v1.name, cTMBuf.get()))
        elif tmp == "updatePosition":
            mTCBuf.put(4)
            xBuf.put(input("Enter x coordinate:"))
            yBuf.put(input("Enter y coordinate:"))
            rBuf.put(input("Enter r coordinate:"))
            with mainToController:
                mainToController.notify()
        else:
            print("Invalid command")



if __name__ == "__main__":
    main()