/*
 * TCP_Server_Code
 * By: Rigo Sandoval
 * 
 * This file sets up a TCP Server on an ESP32 for WiFi communication
 */
#include <WiFi.h>
#include "esp_wpa2.h"                     // wpa2 library for connections to Enterprise networks
#define EAP_IDENTITY "sando168@umn.edu"   // login identity for Enterprise network
#define EAP_USERNAME "sando168@umn.edu"   // oftentimes just a repeat of the identity
#define EAP_PASSWORD "NskypeCOffee44Qn"   // login password
const char* ssid = "eduroam";             // Enterprise network SSID
const uint ServerPort = 23;

WiFiServer Server(ServerPort);            // initialize server
WiFiClient RemoteClient;                  // instantiate WiFiClient to store client info

void setup() {
  Serial.begin(115200);
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

void loop() {
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
}
