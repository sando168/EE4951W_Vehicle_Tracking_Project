/* Spring 2023 CSci4211: Introduction to Computer Networks
** This program serves as the server of DNS query.
** Written in Java. */

/*
 * DNSServer.java
 * This file creates a DNS Server which will service DNS request from a 
 * client that provides a hostname. It has a cache that will store a request's
 * hostname, address pair and writes it to a file in named "DNS_Mapping.txt".
 * This Server also creates a CSV file that logs a client's every request to 
 * a file named "dns-server-log.csv"
 * 
 * Modified By: Rigo Sandoval
 */

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.Random;
import java.util.Scanner;
import java.io.FileWriter;

class DNSServer {
	
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
		//Open an input stream and an output stream for the socket
		//Read requested query from socket input stream
		//Parse input from the input stream
		//Check the requested query

			//Output Stream
			//Input Stream
	    	PrintWriter sendOut = new PrintWriter(sSock.getOutputStream(), true);
	    	BufferedReader readIn = new BufferedReader(
	    	new InputStreamReader(sSock.getInputStream()));

			//Read requested query from client
			String request = readIn.readLine();
			System.out.println(request);

			//Parsing query
			
			//Check the requested query
            boolean hostFound = false;
            try {
			//check the DNS_mapping.txt to see if the host name exists
			//set local file cache to predetermined file.
            //create file if it doesn't exist 

				
				
			//if it does exist, read the file line by line to look for a
            //match with the query sent from the client
            //If match, use the entry in cache.
            //However, we may get multiple IP addresses in cache, so call IPselection to select one. 
			//If no lines match, query the local machine DNS lookup to get the IP resolution
			//write the response in DNS_mapping.txt
				
				String host = request;
				String ip = "";
				String resolved = "";

				//look for a match for the requested hostname in the cache
				
				//if no match, try to do a DNS lookup given the requested hostname
				if(!hostFound) {
					try {
						//dnsLookup will return: hostname/ipaddress
						//string so use a Scanner object with "/" delimiter
						//to seperate hostname and ipaddress
						InetAddress dnsLookup = InetAddress.getByName(request);
						Scanner dnsScan = new Scanner(dnsLookup.toString()).useDelimiter("/");
						hostFound = true;

						host = dnsScan.next();		// host = hostname
						ip = dnsScan.next();		// ip = ipaddress

						//write hostname and ipaddress to DNS_mapping.txt

					} catch (Exception e) {

					}
					if(!hostFound) {
						System.out.println("requested hostname does not exist");
						ip = "AddressNotFound";
					}
					//write hostname and ipaddress to local cache

					//request resolved by API
					resolved = "API";
				}

			//print response to the terminal
			//send the response back to the client
			//Close the server socket.
				System.out.println(host + ":" + ip + ":" + resolved);
				sendOut.println(host + ":" + ip + ":" + resolved);
				sSock.close();
            
            } catch (Exception e) {
                System.out.println("exception: " + e);
            }
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
                System.exit(0);
            }
        }
	}
}
