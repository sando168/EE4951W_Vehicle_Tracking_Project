/*
 * ClientCode.java
 * This java code creates a simple Client for testing the ESP32 Wifi communication
 * 
 * By: Rigo Sandoval
 */

import java.io.*;
import java.net.*;
import java.util.*;

public class ClientCode{
    public static void main(String[]args)
            throws UnknownHostException, IOException{
	//Change the host String to recognize the address where the server
	
	//Change the port number to match the port number opened on the server.

	
	while(true){
        Scanner inLine = new Scanner(System.in);
        String message = "";

        System.out.println("Type in a message for the server, or 'q' to quit:");
        //send message to the server.
        message = inLine.nextLine();

        if (message.equalsIgnoreCase("q") || message.equalsIgnoreCase("quit")) {
            System.exit(0);
        }
        else{
	    	int port = 23;
    		String host = "10.185.61.122";   // IP address of ESP32
            
    		//Create new client socket and connect to the server.
	    	Socket cSock = new Socket(host, port);

	    	//Output Stream
	    	PrintWriter sendOut = new PrintWriter(cSock.getOutputStream(), true);
	    	//Input Stream
	    	BufferedReader readIn = new BufferedReader(
	    	new InputStreamReader(cSock.getInputStream()));
            
            //Send message to the server
            sendOut.println(message);
            //Read in the returned information
            String data = readIn.readLine();

            //close all open Objects
            //print message information.
		    sendOut.close();
            readIn.close();
            cSock.close();
            System.out.println("Received: '" + data);
        }
            
    }
    }
}
