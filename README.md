# Invendor Task Application

## How to run
	The docker Image can be obtained at https://hub.docker.com/r/stg1l/invendor-task/tags
	To run, create internal docker network (e.g. invendor-net)  and run the invendor app image:
		docker container run -d --name gpshost --network invendor-net invendorapp/embedded-linux-task:0.0.1
		docker container run -d --name gpsclient --network invendor-net stg1l/invendor-task:0.0.1
	To  attach to the container: docker exec -it  gpsclient bash

## Description
	BufferFile.py:
		Represents a circular buffer where the coordinate data is stored

	SwaggerSession.py:
		Thread for handling communication with the backend

	Application consists of main loop, which:
		1. Connects to the coordinate data source
		2. Pushes obtained coordinates to the circular buffer
		3. Runs buffer backup to file every 1 seconds



## Known problems:
	Persistent storage solution is not very scalable, there is definitely a better solution out there:
		1. if network is out for a long time, the data will overflow
		2. Syncing data to file gets slow quite fast (order of seconds after 1 hour without network).
		3. On the event of suddent power cut, a couple of coordinate sets may be lost or resent to the backend
	All docker ports are open, potentially not secure
	Client secret committed to git, normally this would be securely stored on a machine
	
