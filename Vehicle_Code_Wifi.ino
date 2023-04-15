#include "Arduino.h"
#include "vehicle.h"
#include <stdio.h>
#include <stdlib.h>

#define MOTOR_PWM 255
#define factorK 100
#define steps 1000
#define deltaT 0.5

/* ----- Global Variables for vehicle steering algorithm ----- */
float destX = -9999; 
float destY = -9999;  
float currX = -9999; 
float currY = -9999; 
float currR = -9999; 
float distance = -9999; 
float angle = -9999;

float s = -9999;
float sum = -9999;
float diff = -9999;

bool getDestination = false; 
bool getLocation = false; 
int pwmValueM1; 
int pwmValueM2; 

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
  Serial.print(currX, 3);
  Serial.print("\n");
    
  Serial.print("currY = ");
  Serial.print(currY, 3);
  Serial.print("\n");

  Serial.print("currR = ");
  Serial.print(currR, 3);
  Serial.print("\n");
    
  Serial.print("destX = ");
  Serial.print(destX, 3);
  Serial.print("\n");
    
  Serial.print("destY = ");
  Serial.print(destY, 3);
  Serial.print("\n");
    
  Serial.print("distance = ");
  Serial.print(distance, 3);
  Serial.print("\n");
    
  Serial.print("angle = ");
  Serial.print(angle, 3);
  Serial.print("\n");
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
        currR = value3;
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
        angle = value1;
        break;
    }
    
    printGlobalFloats();
    
    Serial.println("closing connection");
    Client.stop();
  } else {
    Serial.println("Couldn't connect to server. Retrying...");
    return;  
  }
  
  if (getDestination && getLocation)
  {
    s = deltaS(currX, currY, destX, destY);
    Serial.println(s); 
    if (s < 0.05){
      motor(0, 0); 
    }
    else {
      motor(-50, 55);  //going straight at a constant speed 
    }
    
    getLocation = false; 
  }
}

void loop()
{ 
  ESP32asClient();
}
