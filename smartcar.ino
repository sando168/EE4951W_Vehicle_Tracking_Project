#define LEFT_A 13
#define LEFT_B 14
#define RIGHT_A 25
#define RIGHT_B 26

#define MOTOR_PWM 255
#define DELAY_TIME 600
#define LOOP_COUNT 5

static bool touched = false;
int destiX = 2; 
int destiY = 2;  
int currX = 0; 
int currY = 0;  
int doneX = 0; 
int doneY = 0; 

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

void loop()
{
  while (doneY == 0){
    if (currY < destiY)
    {
      Serial.println("Go forward Y"); 
      currY++; 
    }
    else if (currY > destiY)
    {
      Serial.println("Go backward Y"); 
      currY--; 
    }
    else
    {
      doneY = 1; 
      Serial.println("DoneY"); 
      Serial.println("Turn right");  
    }
  }
  while (doneX == 0){
    if (currX < destiX)
    {
      Serial.println("Go forward X"); 
      currX++; 
    }
    else if (currX > destiX)
    {
      Serial.println("Go backward X"); 
      currX--; 
    }
    else
    {
      doneX = 1; 
      Serial.println("DoneX");
    }
  }
  if (doneX == 1 && doneY == 1){
    //send complete
    Serial.println("Complete");
  }
  if (destiX != currX || destiY != currY){
    doneX = 0; 
    doneY = 0; 
    Serial.println("New job!!!");  
  }
  delay(2000); 
}
