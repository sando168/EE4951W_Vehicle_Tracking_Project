/*
 * ServerCode.java
 * This java code creates a simple Server for testing the ESP32 Wifi communication
 * 
 * By: Rigo Sandoval
 */

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.Random;
import java.util.Scanner;
import java.io.FileWriter;

class ServerCode {
	
	public static void main(String[] args) throws Exception {
		int port = 23;
		ServerSocket sSock = null;

		try {
			sSock = new ServerSocket(port); // Try to open server socket 5001.
		} catch (Exception e) {
			System.out.println("Error: cannot open socket");
			System.exit(1); // Handle exceptions.
		}

		System.out.println("Server is listening...");
		System.out.println("type 'exit' to stop server\n");
		new monitorQuit().start(); // Start a new thread to monitor exit signal.

		while (true) {
			new dnsQuery(sSock.accept()).start();
		}

	}
}

class dnsQuery extends Thread {
	Socket sSock = null;

    dnsQuery(Socket sSock) {
    	this.sSock = sSock;
    }

	@Override public void run(){
		BufferedReader inputStream;
        PrintWriter outStream;

        try {
			//Output Stream
			//Input Stream
	    	PrintWriter sendOut = new PrintWriter(sSock.getOutputStream(), true);
	    	BufferedReader readIn = new BufferedReader(
	    	new InputStreamReader(sSock.getInputStream()));

			//Read requested query from client
			String request = readIn.readLine();
			System.out.println("Server received: " + request);

			//print response to the terminal
			//send the response back to the client
			//Close the server socket.
			String response = "Gotcha bro";
			System.out.println("Server sent: " + response + "'\n");
			sendOut.println(response);
			sSock.close();        
            
			//Close the input and output streams.
			sendOut.close();
        	readIn.close();

        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Host not found.\n" + e);
        }
	}
}

class monitorQuit extends Thread {
	@Override
	public void run() {
		BufferedReader inFromClient = new BufferedReader(new InputStreamReader(System.in)); // Get input from user.
		String st = null;
		while(true){
			try{
				st = inFromClient.readLine();
			} catch (IOException e) {
			}
            if(st.equalsIgnoreCase("exit")){
				System.out.println("Server is closing...");
                System.exit(0);
            }
        }
	}
}
