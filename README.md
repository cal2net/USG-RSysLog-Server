# USG-RSysLog-Server
Python based Remote Syslog server for Unifi USG 

This is a simple python application that accepts the events coming from the Unifi USG firewall.
The purpse is to quickly parse the event messages, convert them to JSON and then pass the messages to an ELK instance for log analysis

## Prerequisite
..* Python 3
..* ELK instance
--* Unifi UGS Firewall

## Installation
Linux is my preferred runtime, but there is nothing Linux specific to the code base.
I have run successfully on Ubuntu 18.04 LTS

1. copy the code to a directory where you want to run it from. 
2. Edit the source file and change the location of the ELK server location. (will be externalizing this soon)
3. To run on the default rsyslog port type sudo python3 USGRSysLogServer.py 514

In future releases there will be external configuration file for the options.

I will create a screen shot approach to setting up the overall solution.

Enjoy


Cheers 
-Jeff
