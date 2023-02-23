/**
 * DNS Client
 * CSci 4211 - Spring 2023
 */
import java.io.*;
import java.net.*;
import java.util.*;

/*
 * Class DNSClient is one of three distributed programs. The client sends DNS
 * inquiries to the server. The server does a lookup of the information and
 * returns it.
 */

public class DNSClient{
    public static void main(String[]args)
            throws UnknownHostException, IOException{
	//Change the host String to recognize the address where the server
	
	//Change the port number to match the port number opened on the server.

	
	while(true){
        Scanner inLine = new Scanner(System.in);
        String query = "";

        //Request DNS query from user
        System.out.println("Type in a domain name to query, or 'q' to quit:");

        //send DNS query to the server. Change the URL to whatever you want to
        //query (ex. google.com, microsoft.com, umn.edu)
        query = inLine.nextLine();

        if (query.equalsIgnoreCase("q") || query.equalsIgnoreCase("quit")) {
            System.exit(0);
        }
        else{
	    	int port = 23;
    		String host = "10.130.96.92";   // IP address of ESP32
            
    		//Create new client socket and connect to the server.
	    	Socket cSock = new Socket(host, port);

	    	//Output Stream
	    	PrintWriter sendOut = new PrintWriter(cSock.getOutputStream(), true);
	    	//Input Stream
	    	BufferedReader readIn = new BufferedReader(
	    	new InputStreamReader(cSock.getInputStream()));
            
            //Send query to the server
            sendOut.println(query);
            //Read in the returned information
            String data = readIn.readLine();

            //close all open Objects
            //print query information.
		    sendOut.close();
            readIn.close();
            cSock.close();
            System.out.println("Received: '" + data + "'\n");
        }
            
    }
    }
}
