class Vehicle:
    def __init__(self):
        self.x = 0
        self.y = 0
    def setPosition(x,y):
        x = x
        y = y
        print("Car position is (" + x + ", " + y+ ")")
    def getPosition(self):
        return(self.x,self.y)
    def moveTo(x,y):
        #algorithm to move to a certain point
        print("moveTo")
    def move(vis,x,y):
        #send move x in the x and y in the y
        vis.updatePosition(self,x,y)
        print("move")

class Board:
    def setSize(x,y):
        x = x
        y = y

class Vision:
    def updatePosition(vehicle, xin, yin):
        x,y = vehicle.getPosition()
        vehicle.setPosition(x+xin, y+yin)
        

v1 = Vehicle()
vi = Vision()

v1.move(vi,10,20)
