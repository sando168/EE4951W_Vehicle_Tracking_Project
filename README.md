# Requirements
- Design a single prototype of a vehicle which can connect to a WiFi network and receive commands from the network moving accordingly.
- ESP32 architecture is recommended to keep the vehicle small. 
- Replicate the prototype to build at least one additional vehicle.
- Realize a video processing system that can monitor the positions of the vehicles which are assumed to move on a limited rectangular area on the floor of a lab.
- The video processing system should be able to output the coordinates of the positions of the vehicles and send instructions to them on how to move.
- The vehicles should be able to follow a specified path.

# Prerequisites
- Linux or [Virtual Box](https://www.virtualbox.org/)
- [Python 3](https://www.python.org/downloads/)
- [Pip3](https://www.geeksforgeeks.org/how-to-install-pip-on-windows/)

# Installation: Linux
Run these commands in a Linux terminal.
```
sudo apt install cmake
sudo apt-get install python3-tk
pip3 install opencv-python
pip3 install imgui[all]

git clone https://github.com/swatbotics/apriltag.git
cd apriltag
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
sudo make install
pip3 install apriltag
```

# Installation: Windows
Run these commands in a Windows terminal.
```
sudo apt install cmake
pip3 install tk
pip3 install opencv-python
pip3 install imgui[all]
pip3 install glfw
pip install PyOpenGL


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

# VirtualBox
For anyone using a Windows based machine that wants to run this project, VirtualBox is the recommended
means of installation and execution. VirtualBox is a program that can deploy different operating systems within separate windows. Below is a series of steps for getting the project running on VirtualBox.

## Download
[VirtualBox Link](https://www.virtualbox.org/wiki/Downloads)
1. Click the "Windows hosts" button
2. Open the executable and step through the setup wizard without changing anything
3. Under "VirtualBox Extension Box" click "All Platforms" and step through the setup wizard

[Linux OS Link](https://ubuntu.com/download/desktop)

4. Click "Download" under Ubuntu 22.04 LTS

## Virtual Machine Setup
5. Click Machine->New
6. Name the virtual machine and click on the Linux download for "ISO image"
7. Edit the unattended guest username and password to something memorable
8. Increasing the amount of RAM to at least 8GB is recommended
9.  A standard 25GB virtual disk is more than plenty
10. Hit "Finish"

## Linux Setup
11. After hitting "Finsh" the Linux OS should start setting itself up. After it finishes, step through the initial options pages and login
12. Open a terminal anywhere and run:
```
su -
usermod -a -G sudo YOUR_USER_NAME
```
13. Restart the virtual machine
14. Log back in to the virtual machine and run in terminal:
```
sudo apt-get update
sudo apt upgrade
```
15. Close the virtual machine
16. In VirtualBox, go to Machine->Settings->USB and click "USB 3.0"

## Running the Project
17. Run in terminal:
```
sudo apt install python3-pip
sudo apt install git
sudo apt install cmake
pip3 install opencv-python
pip3 install bitstring

git clone https://github.com/swatbotics/apriltag
cd apriltag
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
sudo make install
pip3 install apriltag

git clone https://github.umn.edu/bensc010/EE4951W_Vehicle_Tracking_Project
cd EE4951W_Vehicle_Tracking_Project
python3 apriltag_example.py
```
