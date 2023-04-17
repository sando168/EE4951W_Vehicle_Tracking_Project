#include "Arduino.h"
#include "vehicle.h"
#include <stdio.h>
#include <stdlib.h>
#include "math.h"

#define MOTOR_PWM 255
#define factorK 100
#define steps 1000
#define deltaT 0.5

/* ----- Global Variables for vehicle steering algorithm ----- */
float destX = -9999; 
float destY = -9999;  
float currX = -9999; 
float currY = -9999; 
float currTheta = -9999; 
float distance = -9999; 
float phiValue = -9999;
float lambdaValue = -9999; 

float s = -9999;
float increase; 

bool getDestination = false; 
bool getLocation = false; 
int pwmM1 = -45; 
int pwmM2 = 43; 

/* ----- Global Variables for Wifi command parsing ----- */
 
                 // "u 2.435 5.687 113.09" ---> updatePosistion(value1, value2, value3) 
char command;    // first char of command determines what command it is (ex. 'u' correspond to updatePostion command)
float value1;    // parsing will update these values  
float value2; 
float value3; 
char data_str[21];    // make a char array to hold incoming data from the client

/* ----- Global Variables for WiFi Functionality (Normal Network) ----- */
/*
#include <WiFi.h>                         // wifi library for setting up ESP32 client
const char* ssid     = "XR";              // wifi network ssid (name)
const char* password = "quandang";        // wifi network password
*/
/* ----- Global Variables for WiFi Functionality (Enterprise Network) ----- */
///*
#include <WiFi.h>
#include "esp_wpa2.h"                     // wpa2 library for connections to Enterprise networks
#define EAP_IDENTITY "sando168@umn.edu"   // login identity for Enterprise network
#define EAP_USERNAME "sando168@umn.edu"   // oftentimes just a repeat of the identity
#define EAP_PASSWORD "NskypeCOffee44Qn"   // login password
const char* ssid = "eduroam";             // Enterprise network SSID
//*/
/* ----- Objects for setting ESP32 as server ----- */
/*
const uint ServerPort = 23;
WiFiServer Server(ServerPort);            // initialize server
WiFiClient Client;                        // instantiate WiFiClient to store client info
*/
/* ----- Objects for setting ESP32 as a client ----- */

IPAddress server(10,131,111,155);           // server computer IP address
const int port = 65432;                    // port that ESP32 client will operate on (23 = Telnet)
WiFiClient Client;                         // object for setting up ESP32 as a client

void setup()
{
  Serial.begin(115200); 
  pinMode(38, INPUT_PULLUP);
  pinMapping(); 
  motor(0, 0);

  /* ----- Wifi Initialization Starts Here ----- */

  Serial.print("Connecting to network: ");
  Serial.println(ssid);
  
  WiFi.disconnect(true);                  // disconnect from wifi to set new wifi connection

  /* ----- Code to connect ESP32 to normal network ----- */
  /*
  // connect to wifi network
  WiFi.begin(ssid, password);
  */
  /* ----- Code to connect ESP32 to Enterprise Network ----- */
  ///*
  //WiFi.mode(WIFI_AP);                     // access point mode: stations can connect to the ESP32
  // connect to eduroam with login info
  WiFi.begin(ssid, WPA2_AUTH_PEAP, EAP_IDENTITY, EAP_USERNAME, EAP_PASSWORD);
  //*/

  // waiting for sucessful connection to wifi network
  int counter = 0;
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
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

  /* ----- Code to set up ESP32 as a client ----- */
  /*
  Serial.print("Connecting to server: ");
  Serial.println(server);
  
  counter = 0;
  while (!Client.connect(server, port)) {
    delay(500);
    Serial.print(".");
    counter++;
    if(counter>=60){ //after 30 seconds timeout - reset board
      ESP.restart();
    }
  }
  Serial.println("");
  Serial.println("Server connection working, closing client");
  Client.stop();
  */
  /* ----- Code to set up ESP32 as a server ----- */
  //Server.begin();

}

void printGlobalFloats(void){
  
  Serial.print("currX = ");
  Serial.print(currX*3.281, 3);
  Serial.print("\n");
    
  Serial.print("currY = ");
  Serial.print(currY*3.281, 3);
  Serial.print("\n");

  Serial.print("currTheta = ");
  Serial.print(currTheta, 3);
  Serial.print("\n");
    
  Serial.print("destX = ");
  Serial.print(destX*3.281, 3);
  Serial.print("\n");
    
  Serial.print("destY = ");
  Serial.print(destY*3.281, 3);
  Serial.print("\n");
    
  // Serial.print("distance = ");
  // Serial.print(distance, 3);
  // Serial.print("\n");
    
  // Serial.print("angle = ");
  // Serial.print(angle, 3);
  // Serial.print("\n");
}

void ESP32asClient()
{
  String str = "";
  
  if (Client.connect(server, port)){             // if ESP32 can connect to server
    Client.println("www.google.com");            //    send a request to Server

    while (Client.connected()) {                 //    loop while there is a data stream connection
      while (Client.available()) {                  //    if there's bytes to read from the client,
        char c = Client.read();                  //        save byte/char to data char array
        Serial.write(c);                         //        print char out the serial monitor
        str += c;                                //        append char to string variable
        //Client.println("packet recieved");          //        acknowledge to client that packet was received by ESP32
      }
    }
    Serial.print("\nSTR: "); 
    Serial.println(str); 
    
    str.toCharArray(data_str, 21);
  
    char* space1;
    char* space2;
    char* space3;
      
    command = data_str[0];                    // save char indicating type of command
    space1 = strstr(data_str, " ");           // find the first space (delimiter)
    
    value1 = strtof(space1, &space2);         // save the first float value
    value2 = strtof(space2, &space3);         // save the second float value
    value3 = strtof(space3, NULL);            // save the third float value
      
    switch(command)   // depending on the command, save the corresponding values 
    {
      case 'u':
        getLocation = true; 
        currX = value1/3.281; 
        currY = value2/3.281; 
        currTheta = value3;
        break;
      case 'd': 
        getDestination = true; 
        destX = value1/3.281; 
        destY = value2/3.281;
        break;
      case 'm':
        distance = value1;
        break;
      case 'r': 
        phiValue = value1;
        break;
    }
    
    printGlobalFloats();
    
    Serial.println("closing connection");
    Client.stop();
  } else {
    Serial.println("Couldn't connect to server. Retrying...");
    return;  
  }
  
  if (getLocation)   // && getDestination - recieve both values to start going so hard coding destination is not required
  {
    distance = deltaS(currX, currY, (2/3.281), (1/3.281));
    phiValue = optimalAngle(currX, currY, (2/3.281), (1/3.281));    //artan2 returns angle between -180 to 180 
    Serial.print("\nAngle phi is"); 
    Serial.println(phiValue);
    Serial.print("\nDelta s is");
    Serial.println(s); 
    if (distance < 0.1){  //0.05 check if the vehicle is at the destination
      pwmM1 = 0;
      pwmM2 = 0;
    }
    else {
      //determine which direction 
      lambdaValue = abs(currTheta - phiValue);   //lambda is the optimal shortest angle between theta and phi
      if (lambdaValue > 180)
      {
        lambdaValue = 360 - lambdaValue;     //if the lambda is above 180, the optimal angle is 360 - lambda. 
      }
      //turning theta to phi from -180 -> 180 to 0 -> 360  //lambda is 200 degrees -> optimal angle is 160 degrees, turn left
      currTheta = currTheta + 180;   //if theta is 70 degrees, add 180 -> 240 degrees
      phiValue = phiValue + 180;     //if phi is -130 degrees, add 180 -> 50 degrees
      /*
      if (currTheta < 0)             //theta = 90 phi = 120 -> lambda = 30 
      {
        currTheta = currTheta + 360;   //currTheta is still 70 degrees
      }
      if (phiValue < 0)
      {
        phiValue = phiValue + 360;     //phi is -130 + 360 = 230 degrees    //70 + 160 = 230 = phi -> turn left
      }
      */
      if ( ((int(phiValue)+1) > (int(currTheta) + int(lambdaValue)) %360) &&  ((int(currTheta) + int(lambdaValue)) %360) > (int(phiValue) - 1))
      {
        //turn left                  //240 + 160 = 400 % 360 = 40 is not equal to 50, turn right. 
        if (lambdaValue > 5)
        {
          increase = 0.5*lambdaValue; 
          pwmM2 = 43 + increase/2; //speed up    pwmM2 += 43 + increase/2;
          //pwmM2 = 43 + increase*0.7; 
          pwmM1 = -45 + increase/2; //slow down
          //pwmM1 = -45 + increase*0.3; 
        }
        else
        {
          pwmM1 = -45;
          pwmM2 = 43; 
        } 
      }
      else 
      {
        //turn right 
        if (lambdaValue > 5)
        {
          increase = -0.2+lambdaValue; 
          pwmM1 = -45 + increase/2; //speed up pwmM1 += -45 + increase/2;
          //pwmM1 = -45 + increase*0.7; 
          pwmM2 = 43 - increase/2;   //slow down
          //pwmM2 = 43 - increase*0.3; 
        }
        else
        {
          pwmM1 = -45;
          pwmM2 = 43; 
        } 
      }
    }
    motor(pwmM1, pwmM2);  //going straight at a constant speed
    getLocation = false; 
  }
}

void loop()
{ 
  ESP32asClient();
}
