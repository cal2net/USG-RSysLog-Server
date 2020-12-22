# set base image (host OS)
FROM python:3.8-slim

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# Environment Variable
ENV Cal2_USGRsyslog_JSON=/tmp/syslog/rsyslog.json

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local directory to the working directory
COPY src/ .

# command to run on container start
CMD [ "python3", "./USGRSysLogServer.py" ]
