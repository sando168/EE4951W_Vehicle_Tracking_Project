# This is just a test server setup so Logan can get responses from the client code

from machine import Pin
from time import sleep_ms
import time
import network
import socket

# Simple HTTP Server Example
# Control an LED and read a Button using a web browser

ledState = 'LED State Unknown'

ssid = 'Bill Wi the Science Fi'
password = 'BBbb052221'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)
    
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
    
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1] #sets self as client?
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('listening on', addr)

# Listen for connections, serve client
while True:
    try:       
        cl, addr = s.accept() #something happened on the page
        print('client connected from', addr)
        request = cl.recv(1024)
        print("request: {}".format(request))
        request = str(request)
        
        # Create and send response
        response = 1 # TODO: change this to the actual response
        cl.send(response)
        # cl.close()
        
    except OSError as e:
        cl.close()
        print('connection closed')

        