from time import sleep


def dummy(xBuf, yBuf, rBuf):

    def updateXYR(x, y, r):
        if(xBuf.empty()):
            xBuf.put(x)
        else:
            xBuf.get()
            xBuf.put(x)
        if(yBuf.empty()):
            yBuf.put(y)
        else:
            yBuf.get()
            yBuf.put(y)
        if(rBuf.empty()):
            rBuf.put(r)
        else:
            rBuf.get()
            rBuf.put(r)

    print("x: {x}, y: {y}, r: {r} in dummy".format(x=xBuf.get(), y=yBuf.get(), 
                                                   r=rBuf.get()))
    for i in range(10):
        updateXYR(i, i+1, i+2)
        sleep(5)
