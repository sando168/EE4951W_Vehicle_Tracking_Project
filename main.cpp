#include "Arduino.h"
//#include "vehicle.h"
#include <stdio.h>
#include <stdlib.h>

#define MOTOR_PWM 255
#define factorK 100
#define steps 1000
#define deltaT 100

/* ----- Global Variables for vehicle steering algorithm ----- */
float destX = -9999;
float destY = -9999;
float currX = -9999;
float currY = -9999;
float thetaValue = -9999;
float phiValue = -9999;

float s = -9999;
float sum = -9999;
float diff = -9999;; 

/* ----- Global Variables for Wifi command parsing ----- */
 
                 // "u 2.435 5.687 113.09" ---> updatePosistion(value1, value2, value3) 
char command;    // first char of command determines what command it is (ex. 'u' correspond to updatePostion command)
float value1;    // parsing will update these values  
float value2; 
float value3; 
char data_str[21];    // make a char array to hold incoming data from the client

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


void printGlobalFloats(void){
  
  Serial.print("currX = ");
  Serial.print(currX, 3);
  Serial.print("\n");
    
  Serial.print("currY = ");
  Serial.print(currY, 3);
  Serial.print("\n");

  //Serial.print("currR = ");
  //Serial.print(currR, 3);
  //Serial.print("\n");
    
  Serial.print("destX = ");
  Serial.print(destX, 3);
  Serial.print("\n");
    
  Serial.print("destY = ");
  Serial.print(destY, 3);
  Serial.print("\n");
    
  //Serial.print("distance = ");
  //Serial.print(distance, 3);
  //Serial.print("\n");
    
  //Serial.print("angle = ");
  //Serial.print(angle, 3);
  //Serial.print("\n");
}

void setup()
{
  Serial.begin(115200); 
  pinMode(38, INPUT_PULLUP);
  //pinMapping(); 
  //motor(0,0); 

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

void loop()
{
  /* ----- Getting the new values from the camera ----- */

  RemoteClient = Server.available();              // Instatiate object for storing remote client info

  if (RemoteClient) {                             // if you get a client,
    Serial.println("\nNew Client.");
    String str = "";                              //    create temporary string
    while (RemoteClient.connected()) {            //    loop while there is a data stream connection
      if (RemoteClient.available()) {             //    if there's bytes to read from the client,
        char c = RemoteClient.read();             //        save byte/char to data char array
        Serial.write(c);                          //        print char out the serial monitor
        str += c;                                 //        append char to string variable
        RemoteClient.write("packet recieved");    //        acknowledge to client that packet was received by ESP32
      }
    }
    str.toCharArray(data_str, 21);                //    convert string to char array

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
        currX = value1; 
        currY = value2; 
        //currR = value3;
        break;
      case 'd': 
        destX = value1; 
        destY = value2;
        break;
      case 'm':
        //distance = value1;
        break;
      case 'r': 
        //angle = value1;
        break;
    }
  
    printGlobalFloats();
    
    RemoteClient.stop();
    Serial.println("Client Disconnected.");
  }  

  
  // s = deltaS(currX, currY, destX, destY, steps); 

  // sum = sumVelocity(s, deltaT); 

  // diff = diffVelocity(thetaValue, factorK, deltaT); 

  // Serial.println(sum); 
  while(1){
    //motor(-180,125); //usb side is the first argurement 
  }

}
