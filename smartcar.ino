#include <stdio.h>
#include <stdlib.h>

#define LEFT_A 13
#define LEFT_B 14
#define RIGHT_A 25
#define RIGHT_B 26

#define MOTOR_PWM 255
#define DELAY_TIME 600
#define LOOP_COUNT 5
#define error 200

static bool touched = false;
int destX = 2; 
int destY = 2;  
int currX = 0; 
int currY = 0; 

void IRAM_ATTR isr()
{
  touched = true;
}

void setup()
{
  Serial.begin(115200); 
  pinMode(38, INPUT_PULLUP);
  attachInterrupt(38, isr, FALLING);

  ledcAttachPin(LEFT_A, 1);  // assign LEFT_A pin to channel 1
  ledcSetup(1, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  ledcAttachPin(LEFT_B, 2);  // assign LEFT_B pin to channel 2
  ledcSetup(2, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  ledcAttachPin(RIGHT_A, 3); // assign RIGHT_A pin to channel 3
  ledcSetup(3, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  ledcAttachPin(RIGHT_B, 4); // assign RIGHT_B pin to channel 4
  ledcSetup(4, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  motor(0, 0);
}

void motor(int left, int right)
{
  if (left == 0)
  {
    ledcWrite(1, 0); // 0 - 255
    ledcWrite(2, 0); // 0 - 255
  }
  else if (left > 0)
  {
    ledcWrite(1, left); // 0 - 255
    ledcWrite(2, 0);    // 0 - 255
  }
  else
  {
    ledcWrite(1, 0);     // 0 - 255
    ledcWrite(2, -left); // 0 - 255
  }

  if (right == 0)
  {
    ledcWrite(3, 0); // 0 - 255
    ledcWrite(4, 0); // 0 - 255
  }
  else if (right > 0)
  {
    ledcWrite(3, right); // 0 - 255
    ledcWrite(4, 0);     // 0 - 255
  }
  else
  {
    ledcWrite(3, 0);      // 0 - 255
    ledcWrite(4, -right); // 0 - 255
  }
}

void moveVehicle(int currX, int currY, int destX, int destY)
{
  if ((destX - currX) > error && (destY - currY) > error)     //destination is on the right of the starting position 
  {
    motor(150, 70); 
    delay(200); 
  }
  else if ((currX - destX) > error && (destY - currY) > error)    //destination is on the left of the starting position 
  {
    motor(70, 150); 
    delay(200); 
  }
  else if (abs(destX - currX) < error && (destY - currY) > error)     //go straight if face the correct direction and x coordinate is the same
  {
    motor(100, 100); 
    delay(200); 
  }
  else if ((destX - currX) > error && abs(destY - currY) < error)     //go straight if face the correct direction and y coordinate is the same
  {
    motor(100, 100); 
    delay(200); 
  }
  else if (abs(destX - currX) < error && abs(destY - currY) < error)  //arrived at the destination 
  {
    motor(0,0);   //stop 
  }
}

void loop()
{
  //take input of currX, currY, destY, destX from the computer 
  moveVehicle(currX, currY, destX, destY); 
}
