#!/usr/bin/env python

## Tiny Unifi USG Remote Syslog Server in Python.
## USG-RSysLog-Server
## There are a few configuration parameters.

LOG_FILE = 'unifi_syslog.log'
HOST, PORT = "0.0.0.0", 514


## Json file with the configuration information
global config

import logging, logging.config
import socketserver
import json
import requests
import uuid
import os
from datetime import datetime


logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')
logger = logging.getLogger(__name__)

class USGRSyslogUDPHandler(socketserver.BaseRequestHandler):

	jdata = None
	logger = None
	## Just for screen logging no code execution. Helps for to make sure the server is getting message from USG
	JUST_LOGGING = False

	## Log information to the screen to see debugging information to the screen while server is running
	screenlog = False

	## Log messages that server doesn't process to send to ELK
	LOG_UNKNOWN_MSG = False


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



	def __init__(self, request, client_address, server):
		self.logger = logging.getLogger('USGRSyslogUDPHandler')
		self.logger.debug('__init__')
		socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
		return



	def handle(self):
		self.logger.debug("Handle")
		data = bytes.decode(self.request[0].strip())
		socket = self.request[1]

		# used to make sure we understand what is being sent from the ubiquiti server
		if self.JUST_LOGGING:
			self.logger.info(data)
			return

		if str(data).startswith(self.KERNEL_ID):
			self.parseKernelMessageg(str(data))
		else:
			if self.LOG_UNKNOWN_MSG:
				self.logger.info( "No winner" )
				self.logger.info(str(data))
				self.logger.info( "End of no Winner")

	def setup(self):
		self.logger.debug("Setup Method")
		if config is not None:
			self.jdata = config
			self.logger.debug(self.jdata)
			self.setEnv(self.jdata)


	def parseKernelMessageg(self,line):
		if self.DENY_KEY in line:
			return self.parseKernelDenyMessage(line)
		if "LAN_IN-2003-A" in line:
			return self.parseKernelAllowMessage(line)
		if self.IOT_KEY in line:
			return self.parseKernelIoTAllowMessage(line)
		return

	def parseKernelDenyMessage(self,line):
		self.parseKernelMessage(line,self.DENY_KEY, self.DENY_RULE,self.DENY_INDEX,self.DENY_PIPELINE)
		self.logger.debug(line)
		return

	def parseKernelAllowMessage(self,line):
		linelist = line.split()
		self.logger.debug(line)
		return

	def parseKernelIoTAllowMessage(self,line):
		self.parseKernelMessage(line,self.IOT_KEY, self.IOT_RULE, self.IOT_INDEX, self.IOT_PIPELINE)
		self.logger.debug(line)
		return


	def parseKernelMessage(self,line,key,rule,index,pipeline):
		if self.screenlog:
			print("Parsing Kernel Message")
		offset = line.index(key)
		if self.screenlog:
			print("offset is ")
			print(offset)
		msg = line[offset +len(key)+1:len(line)]
		msglist = msg.split()
		if self.screenlog:
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
			if "SRC" in key_value and self.GEOIP_LOOKUP and rule is self.DENY_RULE:
				output['geoip'] = self.checkGeoIP(key_value)
			if "DST" in key_value and self.GEOIP_LOOKUP and rule is self.IOT_RULE:
				output['geoip'] = self.checkGeoIP(key_value)
			if "SRC" in key_value and self.IOT_Client_LOOKUP and rule is self.IOT_RULE:
				output['iot_hostname'] = self.checkIoTDeviceIP(key_value)

			key, value = key_value.split('=')
			#output['_id'] = uid
			output[key]=value

		output['bus_rule'] = rule
		resp_json = json.dumps(output)
		if self.screenlog:
			print(resp_json)

		url = self.genURL(index,uid,pipeline)
		self.sendHttp(resp_json,url)

	def checkGeoIP(self,key_value):
		key, value = key_value.split('=')
		if self.screenlog:
			print("IP Address is " +value)
		url = self.GEOIP_LOOKUP_URL+"cityByIP?ipaddr=" + value
		r = self.getHttp(url)
		return r

	def checkIoTDeviceIP(self,key_value):
		key, value = key_value.split('=')
		if self.screenlog:
			print("IP Address is " +value)
		url = self.IoTClient_LOOKUP_URL+"client?ip=" + value
		r = self.getHttp(url)
		if "hostname" in r:
			return r["hostname"]
		else:
			return 'n/a'

	def genURL(self,INDEX, uuid,pipeline):
		url = self.ELK_URL + INDEX + "/_doc/" + uuid #+"?pipeline=" + pipeline
		if self.screenlog:
			print("URL Generated")
			print(url)
		return url

	def getHttp(self,url):
		print(url)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		r = requests.get(url, headers=headers)
		if self.screenlog:
			print("Http Response")
			print(r.json())
		return r.json()


	def sendHttp(self,data, url):
		print(url)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		r = requests.put(url, data, headers=headers)
		self.logger.info(r)
		if self.screenlog:
			print("data sent")
			print(data)
			print("Http Response")
			print(r.json())

	def setEnv(self,jdata):
		self.logger.debug("In ENV")
		if "HOST" in self.jdata:
			self.HOST = self.jdata["HOST"]

		if "PORT" in self.jdata:
			self.PORT = self.jdata["PORT"]

		if "KERNEL_ID" in self.jdata:
			self.KERNEL_ID = self.jdata["KERNEL_ID"]

		if "DENY_INDEX" in self.jdata:
			self.DENY_INDEX = self.jdata["DENY_INDEX"]

		if "DENY_KEY" in self.jdata:
			self.DENY_KEY = self.jdata["DENY_KEY"]

		if "DENY_RULE" in self.jdata:
			self.DENY_RULE= self.jdata["DENY_RULE"]

		if "DENY_PIPELINE" in self.jdata:
			self.DENY_PIPELINE = self.jdata["DENY_PIPELINE"]

		if "IOT_INDEX" in self.jdata:
			self.IOT_INDEX= self.jdata["IOT_INDEX"]

		if "IOT_KEY" in self.jdata:
			self.IOT_KEY = self.jdata["IOT_KEY"]

		if "IOT_RULE" in self.jdata:
			self.IOT_RULE = self.jdata["IOT_RULE"]

		if "IOT_PIPELINE" in self.jdata:
			self.IOT_PIPELINE = self.jdata["IOT_PIPELINE"]

		if "ELK_URL" in self.jdata:
			self.ELK_URL = self.jdata["ELK_URL"]

		if "GEOIP_LOOKUP" in self.jdata:
			self.GEOIP_LOOKUP = self.jdata["GEOIP_LOOKUP"]

		if "GEOIP_LOOKUP_URL" in self.jdata:
			self.GEOIP_LOOKUP_URL = self.jdata["GEOIP_LOOKUP_URL"]

		if "IOT_Client_LOOKUP" in self.jdata:
			self.IOT_Client_LOOKUP = self.jdata["IOT_Client_LOOKUP"]

		if "IoTClient_LOOKUP_URL" in self.jdata:
			self.IoTClient_LOOKUP_URL = self.jdata["IoTClient_LOOKUP_URL"]

		if "JUST_LOGGING" in self.jdata:
			self.JUST_LOGGING = self.jdata["JUST_LOGGING"]

		if "LOG_UNKNOWN_MSG" in jdata:
			self.LOG_UNKNOWN_MSG = self.jdata["LOG_UNKNOWN_MSG"]

def loadJson(js):
    jd = {}
    with open(js) as f:
        jd = json.load(f)
    return jd

if __name__ == "__main__":

	try:
		if 'Cal2_USGRsyslog_JSON' in os.environ:
			main_json = os.environ["Cal2_USGRsyslog_JSON"]
			config = loadJson(main_json)

			logging.config.dictConfig(config["logging_config"])
			logger = logging.getLogger("main")
		else:
			print("JSON file not in ENV using the hard coded values ")

		logger.info("Starting the UDPService listening on " + str(PORT))
		server = socketserver.UDPServer((HOST,PORT), USGRSyslogUDPHandler)
		server.serve_forever(poll_interval=0.5)
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print ("Crtl+C Pressed. Shutting down USG rSyslog Server.")
