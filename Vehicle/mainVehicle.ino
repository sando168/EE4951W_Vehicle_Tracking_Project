#include "Arduino.h"
#include "vehicle.h"
#include <stdio.h>
#include <stdlib.h>
#include "math.h"

/* ----- Global Variables for vehicle steering algorithm ----- */
float destX = 2.0; 
float destY = 1.0;  
float currX = -9999; 
float currY = -9999; 
float currTheta = -9999; 
float distance = -9999; 
float phiValue = -9999;
float lambdaValue = -9999; 
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
float value4; 
float value5; 
char data_str[40];    // make a char array to hold incoming data from the client
char* space1;
char* space2;
char* space3;
char* space4;
char* space5;

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
    if(counter>=30){ //after 15 seconds timeout - reset board
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
  Serial.println("server connected");
  //Client.stop();
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
    
  // Serial.print("destX = ");
  // Serial.print(destX, 3);
  // Serial.print("\n");
    
  // Serial.print("destY = ");
  // Serial.print(destY, 3);
  // Serial.print("\n");
    
  // Serial.print("distance = ");
  // Serial.print(distance, 3);
  // Serial.print("\n");
    
  // Serial.print("angle = ");
  // Serial.print(angle, 3);
  // Serial.print("\n");
}

void loop()
{
  //motor(-37, 38); 
  String str = "---";
  
  Serial.println("Connecting to server....");
  if (Client.connect(server, port)){              // if ESP32 can connect to server
    Serial.println("server connected");
    while (true){
      Serial.println("sending a request...");
      Client.println("Requesting data...");       //     send a request to Server
      str = Client.readStringUntil('\n');         //     read the data sent from the server
      
      Serial.print("\nSTR: "); 
      Serial.println(str); 
      str.toCharArray(data_str, 40);              //     convert the string into a char array

      if (data_str[0] != NULL){                   // if a data has been received
        Serial.println("Started data parsing.");

        command = data_str[0];                    //     save char indicating type of command   
        space1 = strstr(data_str, " ");           //     find the first space (delimiter)
        
        value1 = strtof(space1, &space2);         //     save the first float value
        value2 = strtof(space2, &space3);         //     save the second float value
        value3 = strtof(space3, &space4);         //     save the third float value
        value4 = strtof(space4, &space5);         //     save the fourth float value
        value5 = strtof(space5, NULL);            //     save the fifth float value

        value1 = value1/3.281;                    //     convert from ft to metric
        value2 = value2/3.281;                    //     convert from ft to metric
        value4 = value4/3.281;                    //     convert from ft to metric
        value5 = value5/3.281;                    //     convert from ft to metric
          
        switch(command)   // depending on the command, save the corresponding values 
        {
          case 'u':
            getLocation = true; 
            currX = value1; 
            currY = value2; 
            currTheta = value3;
            destX = value4; 
            destY = value5; 
            break;
          case 'd': 
            getDestination = true; 
            destX = value1; 
            destY = value2;
            break;
          case 'm':
            distance = value1;
            break;
          case 'r': 
            phiValue = value1;
            break;
        }
        
        printGlobalFloats();
      }

      if (getLocation)   
      {
        distance = deltaS(currX, currY, destX, destY);          
        phiValue = optimalAngle(currX, currY, destX, destY);    //artan2 returns angle between -180 to 180 

        Serial.print("\nDelta s is ");
        Serial.println(distance); 

        Serial.print("\nAngle phi is "); 
        Serial.println(phiValue);

        if (distance < 0.05){  
          pwmM1 = 0;
          pwmM2 = 0;
        }
        else {
          lambdaValue = abs(currTheta - phiValue);   //lambda is the optimal shortest angle between theta and phi
          if (lambdaValue > 180)                     //if the lambda is above 180, the optimal angle is 360 - lambda. 
          {
            lambdaValue = 360 - lambdaValue;         
          }
          Serial.print("Lambda is: "); 
          Serial.println(lambdaValue); 

          if (currTheta < 0)                         //Changing the angle range from -180 -> 180 to 0 to 360
          {
            currTheta = currTheta + 360;  
          }
          if (phiValue < 0)
          {
            phiValue = phiValue + 360;     
          }
          
          //Determining the direction to turn
          if ( ((int(phiValue)+2) > ((int(currTheta) + int(lambdaValue)) %360)) &&  (((int(currTheta) + int(lambdaValue)) %360) > (int(phiValue) - 2)) )
          {
            //turn left                  
            if (lambdaValue > 5)
            {
              Serial.println("turn left"); 
              increase = 0.5*lambdaValue;               //get a portion of the lambdaValue
              //The value of distance is added so as the vehicle is closer, the speed decreases
              pwmM2 = 38 + distance*3 + increase;       //speed up  
              pwmM1 = -37 + distance*3 + increase*0.5;  //slow down  43 -45
            }
            else
            {
              pwmM1 = -37;      //reset speed to go straight
              pwmM2 = 38; 
            } 
          }
          else 
          {
            //turn right 
            if (lambdaValue > 5)
            {
              Serial.println("Turn right"); 
              increase = -0.7*lambdaValue;               //get a portion of the lambdaValue
              pwmM1 = -37 + distance*3 + increase;       //speed up 
              pwmM2 = 38 + distance*3 + increase*0.4;    //slow down
            }
            else
            {
              pwmM1 = -37;     //reset speed to go straight
              pwmM2 = 38; 
            } 
          }
        }
        //printing the pwm to serial monitor
        Serial.print("pwmM1 is : "); 
        Serial.println(pwmM1); 
        Serial.print("pwmM2 is : "); 
        Serial.println(pwmM2); 
        
        motor(pwmM1, pwmM2);  
        getLocation = false; 
      }
   }
    Serial.println("closing connection");
    Client.stop();
  } else {
    Serial.println("Couldn't connect to server. Retrying...");
    return;  
  }
}
