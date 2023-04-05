#include <stdio.h>
#include <stdlib.h>

#define LEFT_A 33
#define LEFT_B 14
#define RIGHT_A 21
#define RIGHT_B 22

#define MOTOR_PWM 255
#define DELAY_TIME 600
#define LOOP_COUNT 5
#define error 200

float destX; 
float destY;  
float currX; 
float currY; 
float currR; 
float distance; 
float angle; 
                 // "u 2.435 5.687 113.09" ---> updatePosistion(value1, value2, value3) 
char command;    // first char of command determines what command it is (ex. 'u' correspond to updatePostion command)
float value1;    // parsing will update these values  
float value2; 
float value3; 

/* ----- Global Variables for WiFi Functionality (Enterprise Network) ----- */

#include <WiFi.h>
#include "esp_wpa2.h"                     // wpa2 library for connections to Enterprise networks
#define EAP_IDENTITY "sando168@umn.edu"   // login identity for Enterprise network
#define EAP_USERNAME "sando168@umn.edu"   // oftentimes just a repeat of the identity
#define EAP_PASSWORD "NskypeCOffee44Qn"   // login password
const char* ssid = "eduroam";             // Enterprise network SSID
const uint ServerPort = 23;

WiFiServer Server(ServerPort);            // initialize server
WiFiClient RemoteClient;                  // instantiate WiFiClient to store client info

void setup()
{
  Serial.begin(115200); 
  pinMode(38, INPUT_PULLUP);
  //attachInterrupt(38, isr, FALLING);

  ledcAttachPin(LEFT_A, 1);  // assign LEFT_A pin to channel 1
  ledcSetup(1, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  ledcAttachPin(LEFT_B, 2);  // assign LEFT_B pin to channel 2
  ledcSetup(2, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  ledcAttachPin(RIGHT_A, 3); // assign RIGHT_A pin to channel 3
  ledcSetup(3, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  ledcAttachPin(RIGHT_B, 4); // assign RIGHT_B pin to channel 4
  ledcSetup(4, 12000, 8);    // 12 kHz PWM, 8-bit resolution
  motor(0, 0);

  /* ----- Wifi Initialization Starts Here ----- */

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
  /*else if (abs(destX - currX) < error && (destY - currY) > error)     //go straight if face the correct direction and x coordinate is the same
  {
    motor(100, 100); 
    delay(200); 
  }*/
  else if (abs(destX - currX) > error && abs(destY - currY) < error)     //go straight if face the correct direction and y coordinate is the same
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
  RemoteClient = Server.available();              // Instatiate object for storing remote client info
  char data[21];                                  // make a char array to hold incoming data from the client

  if (RemoteClient) {                             // if you get a client,
    int i = 0;                                    // start index at 0
    Serial.println("\nNew Client.");
    while (RemoteClient.connected()) {            //    loop while there is a data stream connection
      if (RemoteClient.available()) {             //    if there's bytes to read from the client,
        data[i] = RemoteClient.read();            //        save byte/char to data char array
        Serial.write(data[i]);                    //        print char out the serial monitor
        i++;
        RemoteClient.write("packet recieved");    //        acknowledge to client that packet was received by ESP32
      }
    }
  }

  char* space1;
  char* space2;
  char* space3;
  
  command = data[0];                        // save char indicating type of command
  space1 = strstr(data, " ");               // find the first space (delimiter)

  value1 = strtof(space1, &space2);         // save the first float value
  value2 = strtof(space2, &space3);         // save the second float value
  value3 = strtof(space3, NULL);            // save the third float value
  
  switch(command)   // depending on the command, save the corresponding values 
  {
    case 'u':
      currX = value1; 
      currY = value2; 
      currR = value3;
      break;
    case 'd': 
      destX = value1; 
      destY = value2;
      break;
    case 'm':
      distance = value1;
      break;
    case 'r': 
      angle = value1;
      break;
  }
  moveVehicle(currX, currY, destX, destY); 
}



/*
 * 
 * 
static bool touched = false;

void IRAM_ATTR isr()
{
  touched = true;
}
*/
