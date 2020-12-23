#!/bin/bash
export Cal2_USGRsyslog_JSON=./src/rsyslog.json
source src/env/bin/activate
python3 ./src/USGRSysLogServer.py
