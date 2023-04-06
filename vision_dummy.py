from time import sleep


def dummy(xBuf, yBuf, rBuf, endBuf):

    def updateXYR(x, y, r):
        # TODO: this only removes one element from the queue, not all
        # fix that
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

    for i in range(10):
        if(not endBuf.empty()):
            break
        updateXYR(i, i+1, i+2)
        sleep(5)
