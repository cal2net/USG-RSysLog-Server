# USG-RSysLog-Server
Python based Remote Syslog server for Unifi USG 

This is a simple python application that accepts the events coming from the Unifi USG firewall.
The purpse is to quickly parse the event messages, convert them to JSON and then pass the messages to an ELK instance for log analysis. I wanted to a way to create a cool looking monitoring dashboard. I searched and tried several options, none were easy to use or setup. So I decided to write one. Below is one of my dashboard.

![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/Deny-Dashboard.png "Dashboard showing statistics about the deny rule")


## Prerequisite
* Python 3
* ELK instance
* Unifi UGS Firewall

## USG Remote Logging setup
The purpose of the USG-RSysLog-Server is to capture the events coming from the USG Firewall. In my case I wanted to see how many times I am being hit by bad boys of the internet. Also I wanted to know where my IoT data is going. My setup has IoT devices on their own VLAN. This allows me to watch that traffic. 
 
You need to configure your USG to send logging inforation to the USG-RSysLog-Server.  You do this by setting up remote logging.
![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/USG_Remote_Syslog_IP.png "USG Remote IP Entry")

The interesting events are the Deny events. Below is how I set my USG up. If you have your own rules, you can skipt this step.
## USG Firewall Rules Setup
### Deny Rule
Add a new firewall rule. 

![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/Deny_FW-Rule-Details.png "Details of firewall rule for Deny Rule")
 
Once saved you should see the new rule added to the list.
![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/Deny_FW-Rule.png "Firewall list in USG for WAN-IN")
 
Keep track of the rule number, because you will need it for the server configurations. In the example above the rule number is 4000

### IoT Outbound Setup (Optional)
All of my IoT devices are on their own VLAN. I did this to be able to track where my IoT devices send their data. In order to do this, I needed to setup an WLAN OUT rule to capture the newly created connections. Below is what it looks like


![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/IoT_OutBound_FW-Rule-Details.png "Details of firewall rule for IoT VLAN outboud traffic")

Once saved should have a new entry in the list of rules
![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/IoT_OutBound_FW-Rule.png "List of firewall rules for outboud traffic")

Like with the deny rule, keep track of your rule index number to configure the USG-RSysLogServer.

## Installation
Linux is my preferred runtime, but there is nothing Linux specific to the code base.
I have run successfully on Ubuntu 18.04 LTS

1. copy the code to a directory where you want to run it from. 
2. Edit the source file and the parameters to fit your environment( these will be externalizing this soon) . 
* ELK_URL = 'http://localhost:9200/' 
* DENY_KEY = 'WAN_LOCAL-4000-D'
* IOT_KEY = 'WAN_OUT-4000-A' 
 
The IOT_KEY is what I use to track my VLAN for IoT devices. If you don't have a specific VLAN for IoT devices this is useless

3. To run on the default rsyslog port type
  
>`sudo python3 USGRSysLogServer.py 514` 
  
or if you don't want to be root (good choice) type 
  
>` python3 USGRSysLogServer.py 5514` 
 
 Be sure to update your port number in the next step to reflect the port you have chosen.

4. Update your unifi USG to point to the server

![alt text](https://github.com/cal2net/USG-RSysLog-Server/blob/master/images/USG_Remote_Syslog_IP.png "USG Remote IP Entry")

5. Install an ELK instance. I followed the instructions from the link below and found it to be very easy. I only installed ElasticSearch and Kinana.
  
https://logz.io/learn/complete-guide-elk-stack/#installing-elk

In my case, I didn't have a set of machines that could run the entire ELK stack. I am using my USG for home use. So, I only installed the __Elastic Search__ part and the __Kibana__ part. I did __NOT__ install LogStash or Beats. In reality, the python server is providing this function in a very basic and specif purpose, the USG log events.

6. Now it is time to configure the ELK stack to deal with geo-location information derived from the IP address. This is what allows the maps to be generated in Kibana. I assume this is what most people want out of the dashboard. It is pretty straight forward. Below are the two things needed. One is for the Deny Rules and the other is for the IoT information. If you are not doing the IoT VLan monitoring, you don't have to do the second update.

#### Configure Kibaba for Mapping of the Deny Rule
Logon to Kibaba
Go to Dev tools
Paste snippet into the console. 
```JSON
PUT _ingest/pipeline/geoip
{
  "description" : "Add geoip info",
  "processors" : [
    {
      "geoip" : {
        "field" : "SRC"
      }
    }
  ]
}
```
#### Configure Kibaba for Mapping of the IoT VLan Rule

Paste snippet into the console. 
```JSON
PUT _ingest/pipeline/destgeoip
{
  "description" : "Add geoip info for IoT",
  "processors" : [
    {
      "geoip" : {
        "field" : "DST"
      }
    }
  ]
}
```

At this point we should be able to process inbound message and properly code them with geo-code information.

Enjoy


Cheers 
 
-Jeff
