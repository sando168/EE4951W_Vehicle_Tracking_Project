#include "Arduino.h"
//#include "vehicle.h"
#include <stdio.h>
#include <stdlib.h>

#define MOTOR_PWM 255
#define factorK 100
#define steps 1000
#define deltaT 100

//keep track of current position of the vehicle and destination
int destX, destY, currX, currY, thetaValue, phiValue; 

int s, sum, diff; 

void setup()
{
  Serial.begin(115200); 
  pinMode(38, INPUT_PULLUP);
  //pinMapping(); 
  //motor(0,0); 
}

void loop()
{
  //getting the new values from the camera 
  // s = deltaS(currX, currY, destX, destY, steps); 

  // sum = sumVelocity(s, deltaT); 

  // diff = diffVelocity(thetaValue, factorK, deltaT); 

  // Serial.println(sum); 
  while(1){
    //motor(-180,125); //usb side is the first argurement 
  }

}
