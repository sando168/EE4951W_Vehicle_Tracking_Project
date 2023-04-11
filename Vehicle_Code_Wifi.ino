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

float destX = -9999; 
float destY = -9999;  
float currX = -9999; 
float currY = -9999; 
float currR = -9999; 
float distance = -9999; 
float angle = -9999;

/* ----- Global Variables for Wifi command parsing ----- */
 
                 // "u 2.435 5.687 113.09" ---> updatePosistion(value1, value2, value3) 
char command;    // first char of command determines what command it is (ex. 'u' correspond to updatePostion command)
float value1;    // parsing will update these values  
float value2; 
float value3; 
char data_str[21];    // make a char array to hold incoming data from the client

/* ----- Global Variables for WiFi Functionality (Normal Network) ----- */
///*
#include <WiFi.h>                         // wifi library for setting up ESP32 client
const char* ssid     = "XR";              // wifi network ssid (name)
const char* password = "quandang";        // wifi network password
//*/
/* ----- Global Variables for WiFi Functionality (Enterprise Network) ----- */
/*
#include <WiFi.h>
#include "esp_wpa2.h"                     // wpa2 library for connections to Enterprise networks
#define EAP_IDENTITY "sando168@umn.edu"   // login identity for Enterprise network
#define EAP_USERNAME "sando168@umn.edu"   // oftentimes just a repeat of the identity
#define EAP_PASSWORD "NskypeCOffee44Qn"   // login password
const char* ssid = "eduroam";             // Enterprise network SSID
*/
/* ----- Objects for setting ESP32 as server ----- */
/*
const uint ServerPort = 23;
WiFiServer Server(ServerPort);            // initialize server
WiFiClient Client;                        // instantiate WiFiClient to store client info
*/
/* ----- Objects for setting ESP32 as a client ----- */

IPAddress server(10,185,61,74);           // server computer IP address
const int port = 23;                      // port that ESP32 client will operate on (23 = Telnet)
WiFiClient Client;                        // object for setting up ESP32 as a client

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

  /* ----- Code to connect ESP32 to normal network ----- */
  ///*
  // connect to wifi network
  WiFi.begin(ssid, password);
  //*/
  /* ----- Code to connect ESP32 to Enterprise Network ----- */
  /*
  //WiFi.mode(WIFI_AP);                     // access point mode: stations can connect to the ESP32
  // connect to eduroam with login info
  WiFi.begin(ssid, WPA2_AUTH_PEAP, EAP_IDENTITY, EAP_USERNAME, EAP_PASSWORD);
  */

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
  Serial.println("Server connected");

  /* ----- Code to set up ESP32 as a server ----- */
  //Server.begin();

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

void loop()
{ 
  ESP32asClient();
}


void ESP32asClient()
{
  String str = "";
  Serial.println("writing www.google.com to server");
  Client.println("www.google.com");
  Serial.println("wrote www.google.com to server"); 
  if(Client.available()){
    while(Client.available()) {
      //Serial.println("\nClient receiving data");
      char c = Client.read();                   //        save byte/char to data char array
      Serial.write(c);                          //        print char out the serial monitor
      str += c;                                 //        append char to string variable
      //Client.println("packet recieved");          //        acknowledge to client that packet was received by ESP32
    }
    Serial.println(str); 
    /*
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
    
    printGlobalFloats();
    */
    Serial.println();
    Serial.println("closing connection");
  }
  delay(5000);
  
  //moveVehicle(currX, currY, destX, destY); 

  motor(value1, value2);
}
/*
void ESP32asServer()
{
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
  
    printGlobalFloats();
    
    RemoteClient.stop();
    Serial.println("Client Disconnected.");
  }
  
  //moveVehicle(currX, currY, destX, destY); 

  motor(value1, value2);
}
*/

/*
 * 
 * 
static bool touched = false;

void IRAM_ATTR isr()
{
  touched = true;
}
*/
