# Requirements
- Design a single prototype of a vehicle which can connect to a WiFi network and receive commands from the network moving accordingly.
- ESP32 architecture is recommended to keep the vehicle small. 
- Replicate the prototype to build at least one additional vehicle.
- Realize a video processing system that can monitor the positions of the vehicles which are assumed to move on a limited rectangular area on the floor of a lab.
- The video processing system should be able to output the coordinates of the positions of the vehicles and send instructions to them on how to move.
- The vehicles should be able to follow a specified path.

# Prerequisites
- [Python 3](https://www.python.org/downloads/)
- [Pip3](https://www.geeksforgeeks.org/how-to-install-pip-on-windows/)
- Linux or [Linux Subsystem for Windows](https://developerinsider.co/stepwise-guide-to-enable-windows-10-subsystem-for-linux/#:~:text=To%20enable%20the%20Windows%20Subsystem,list%20here%20and%20click%20OK.)

# Installation
Run these commands in a Linux terminal.
```
pip3 install cmake
pip3 install opencv-python

git clone https://github.com/swatbotics/apriltag.git
cd apriltag
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
sudo make install
pip3 install apriltag
```

# Execution
```
python3 apriltag_example.py
```



