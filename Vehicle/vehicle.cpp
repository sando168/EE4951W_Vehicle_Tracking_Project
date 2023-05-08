#include "Arduino.h"
#include "math.h"
#include <cmath>

//pin mapping for the motor
#define LEFT_A 33
#define LEFT_B 14
#define RIGHT_A 21
#define RIGHT_B 22

#define error 200

void pinMapping()
{
    ledcAttachPin(LEFT_A, 1);  // assign LEFT_A pin to channel 1
    ledcSetup(1, 12000, 8);    // 12 kHz PWM, 8-bit resolution
    ledcAttachPin(LEFT_B, 2);  // assign LEFT_B pin to channel 2
    ledcSetup(2, 12000, 8);    // 12 kHz PWM, 8-bit resolution
    ledcAttachPin(RIGHT_A, 3); // assign RIGHT_A pin to channel 3
    ledcSetup(3, 12000, 8);    // 12 kHz PWM, 8-bit resolution
    ledcAttachPin(RIGHT_B, 4); // assign RIGHT_B pin to channel 4
    ledcSetup(4, 12000, 8);    // 12 kHz PWM, 8-bit resolution
}

void motor(int left, int right)
{
    if (left == 0)
    {
        ledcWrite(1, 0); 
        ledcWrite(2, 0); 
    }
    else if (left > 0)
    {
        ledcWrite(1, left); 
        ledcWrite(2, 0);    
    }
    else
    {
        ledcWrite(1, 0);     
        ledcWrite(2, -left); 
    }

    if (right == 0)
    {
        ledcWrite(3, 0); 
        ledcWrite(4, 0); 
    }
    else if (right > 0)
    {
        ledcWrite(3, right); 
        ledcWrite(4, 0);     
    }
    else
    {
        ledcWrite(3, 0);     
        ledcWrite(4, -right); 
    }
}

float deltaS(float currX, float currY, float destX, float destY)
{
    float xDifference = pow((abs(currX - destX)), 2); 
    float yDifference = pow((abs(currY - destY)), 2);
    return (sqrt(xDifference + yDifference)); 
}

float sumVelocity(float deltaS, float deltaT)
{
    return (2*deltaS) / deltaT; 
}

float diffVelocity(float theta, float factorK, float deltaT)
{
    return (2*theta) * factorK / deltaT; 
}

float optimalAngle(float currX, float currY, float destX, float destY)
{
    return atan2((destY-currY),(destX-currX))*180/PI; 
}

float max(float x, float y){
    if (x > y){
        return x; 
    }
    return y; 
}

float min(float x, float y){
    if (x > y){
        return y; 
    }
    return x; 
}