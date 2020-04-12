# USG-RSysLog-Server
Python based Remote Syslog server for Unifi USG 

This is a simple python application that accepts the events coming from the Unifi USG firewall.
The purpse is to quickly parse the event messages, convert them to JSON and then pass the messages to an ELK instance for log analysis

## Prerequisite
* Python 3
* ELK instance
* Unifi UGS Firewall

## Installation
Linux is my preferred runtime, but there is nothing Linux specific to the code base.
I have run successfully on Ubuntu 18.04 LTS

1. copy the code to a directory where you want to run it from. 
2. Edit the source file and change the location of the ELK server location. (will be externalizing this soon)
3. To run on the default rsyslog port type
  
>`sudo python3 USGRSysLogServer.py 514` 
  
or if you don't want to be root (good choice) type 
  
>` python3 USGRSysLogServer.py 5514` 
 
 Be sure to update your port number in the next step to reflect the port you have chosen.

4. Update your unifi USG to point to the server

![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/USG_Remote_Syslog_IP.png "USG Remote IP Entry")

5. Install an ELK instance. I followed the followin instructions and found it to be very easy
  
https://logz.io/learn/complete-guide-elk-stack/#installing-elk

In my case, I didn't have a set of machines that could run the entire ELK stack. I am using my USG for home use. So, I only installed the __Eleastic Search__ part and the __Kibana__ part. I did __NOT__ install LogStash. In reality, the python server is serving this function in a very basic and specif purpose, the USG log events.

In future releases there will be external configuration file for the options.

I will create a screen shot approach to setting up the overall solution.

Enjoy


Cheers 
 
-Jeff
