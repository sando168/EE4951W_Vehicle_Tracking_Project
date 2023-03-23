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

#include <WiFi.h>
#include "esp_wpa2.h"                     // wpa2 library for connections to Enterprise networks
#define EAP_IDENTITY "sando168@umn.edu"   // login identity for Enterprise network
#define EAP_USERNAME "sando168@umn.edu"   // oftentimes just a repeat of the identity
#define EAP_PASSWORD "NskypeCOffee44Qn"   // login password
const char* ssid = "eduroam";             // Enterprise network SSID
const uint ServerPort = 23;

WiFiServer Server(ServerPort);            // initialize server
WiFiClient RemoteClient;                  // instantiate WiFiClient to store client info

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

  Serial.print("Connecting to network: ");
  Serial.println(ssid);
  
  WiFi.disconnect(true);                  // disconnect from wifi to set new wifi connection
  WiFi.mode(WIFI_AP);                     // access point mode: stations can connect to the ESP32
  // connect to eduroam with login info
  WiFi.begin(ssid, WPA2_AUTH_PEAP, EAP_IDENTITY, EAP_USERNAME, EAP_PASSWORD);

  // waiting for sucessful connection
  int counter = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    counter++;
    if(counter>=60){ //after 30 seconds timeout - reset board
      ESP.restart();
    }
  }
  
  // connection sucessfull
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address set: ");
  Serial.println(WiFi.localIP()); //print LAN IP

  Server.begin();
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
  RemoteClient = Server.available();

  if (RemoteClient) {                             // if you get a client,
    Serial.println("New Client.");                // print a message out the serial port
    String currentLine = "";                      // make a String to hold incoming data from the client
    while (RemoteClient.connected()) {            // loop while the client's connected
      if (RemoteClient.available()) {             // if there's bytes to read from the client,
        char c = RemoteClient.read();             // read a byte, then
        Serial.write(c);                          // print it out the serial monitor
        }
      }
    }
  
  //take input of currX, currY, destY, destX from the computer 
  moveVehicle(currX, currY, destX, destY); 
}
