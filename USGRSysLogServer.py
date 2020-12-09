#!/usr/bin/env python

## Tiny Unifi USG Remote Syslog Server in Python.
## USG-RSysLog-Server
## There are a few configuration parameters.

LOG_FILE = 'unifi_syslog.log'
HOST, PORT = "0.0.0.0", 514

## Seems my lessage types for Kernel Message are
KERNEL_ID = '<4>'

## Deny information. These are for messages that the USG blocks at the firewall
DENY_INDEX = 'unifi-deny'
DENY_KEY = 'WAN_LOCAL-4000-D'
DENY_RULE= 'FW-DENY'
DENY_PIPELINE = 'geoip'

## These are the message coming from the VLan for the IoT Devices
IOT_INDEX= 'unifi-iot'
IOT_KEY = 'WAN_OUT-4000-A'
IOT_RULE = 'IoT'
IOT_PIPELINE = 'destgeoip'

## ELK base url and port
ELK_URL = 'http://localhost:9200/'

GEOIP_LOOKUP = True
GEOIP_LOOKUP_URL = 'http://localhost:5000/'

IOT_Client_LOOKUP = True
IoTClient_LOOKUP_URL = 'http://localhost:5002/'

import logging
import socketserver
import json
import requests
import uuid
from datetime import datetime


logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')
## Just for screen logging no code execution. Helps for to make sure the server is getting message from USG
justlogging = False

## Log information to the screen to see debugging information to the screen while server is running
screenlog = False

## Log to the screen message that server doesn't process to send to ELK
logUnknownMsg = False

## Log to a file the messages
file_log = True

class USGRSyslogUDPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = bytes.decode(self.request[0].strip())
		socket = self.request[1]
		if justlogging:
			print(data)
			logging.info(data)
			return
		if str(data).startswith(KERNEL_ID):
			parseKernelMessageg(str(data))
		else:
			if screenlog or logUnknownMsg:
				print( "No winner" )
				print(str(data))
				print( "End of no Winner")

def parseKernelMessageg(line):
	if DENY_KEY in line:
		return parseKernelDenyMessage(line)
	if "LAN_IN-2003-A" in line:
		return parseKernelAllowMessage(line)
	if IOT_KEY in line:
		return parseKernelIoTAllowMessage(line)
	return

def parseKernelDenyMessage(line):
	parseKernelMessage(line,DENY_KEY, DENY_RULE,DENY_INDEX,DENY_PIPELINE)
	if file_log:
		logging.info(line)
	return

def parseKernelAllowMessage(line):
	linelist = line.split()
	if file_log:
		logging.info(line)
	return

def parseKernelIoTAllowMessage(line):
	parseKernelMessage(line,IOT_KEY, IOT_RULE, IOT_INDEX, IOT_PIPELINE)
	if file_log:
		logging.info(line)
	return


def parseKernelMessage(line,key,rule,index,pipeline):
	if screenlog:
		print("Parsing Kernel Message")
	offset = line.index(key)
	if screenlog:
		print("offset is ")
		print(offset)
	msg = line[offset +len(key)+1:len(line)]
	msglist = msg.split()
	if screenlog:
		print("printing attrs" + key)
		print(msglist)
	output = {}
	uid = str(uuid.uuid4())

	now = datetime.utcnow()
	output['@timestamp']=now.strftime("%Y-%m-%dT%H:%M:%S.%f")

	for key_value in msglist:
		if "eth0=" in key_value:
			continue
		if "=" not in key_value:
			continue
		if "SRC" in key_value and GEOIP_LOOKUP and rule is DENY_RULE:
			output['geoip'] = checkGeoIP(key_value)
		if "DST" in key_value and GEOIP_LOOKUP and rule is IOT_RULE:
			output['geoip'] = checkGeoIP(key_value)
		if "SRC" in key_value and IOT_Client_LOOKUP and rule is IOT_RULE:
			output['iot_hostname'] = checkIoTDeviceIP(key_value)

		key, value = key_value.split('=')
		#output['_id'] = uid
		output[key]=value

	output['bus_rule'] = rule
	resp_json = json.dumps(output)
	if screenlog:
		print(resp_json)

	url = genURL(index,uid,pipeline)
	sendHttp(resp_json,url)

def checkGeoIP(key_value):
	key, value = key_value.split('=')
	if screenlog:
		print("IP Address is " +value)
	url = GEOIP_LOOKUP_URL+"cityByIP?ipaddr=" + value
	r = getHttp(url)
	return r

def checkIoTDeviceIP(key_value):
	key, value = key_value.split('=')
	if screenlog:
		print("IP Address is " +value)
	url = IoTClient_LOOKUP_URL+"client?ip=" + value
	r = getHttp(url)
	if "hostname" in r:
		return r["hostname"]
	else:
		return 'n/a'

def genURL(INDEX, uuid,pipeline):
	url = ELK_URL + INDEX + "/_doc/" + uuid #+"?pipeline=" + pipeline
	if screenlog:
		print("URL Generated")
		print(url)
	return url

def getHttp(url):
	print(url)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.get(url, headers=headers)
	if screenlog:
		print("Http Response")
		print(r.json())
	return r.json()


def sendHttp(data, url):
	print(url)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.put(url, data, headers=headers)
	if screenlog:
		print("data sent")
		print(data)
		print("Http Response")
		print(r.json())



if __name__ == "__main__":
	try:
		server = socketserver.UDPServer((HOST,PORT), USGRSyslogUDPHandler)
		server.serve_forever(poll_interval=0.5)
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print ("Crtl+C Pressed. Shutting down USG rSyslog Server.")
