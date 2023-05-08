#ifndef vehicle
#define vehicle

//initial mapping specific pin to the motor 
void pinMapping(); 

//control the pwm signal of the motor - forward and backward
void motor(int left, int right); 

//calculate deltaS value 
float deltaS(float currX, float currY, float destX, float destY); 

//calculate the sum of v1 + v2 
float sumVelocity(float deltaS, float deltaT); 

//calculate the angle difference 
float optimalAngle(float currX, float currY, float destX, float destY); 

//calculate the difference of v1 - v2 
float diffVelocity(float theta, float factorK, float deltaT); 

//find the max between x and y 
float max(float x, float y); 

//find the min between x and y 
float min(float x, float y); 
#endif