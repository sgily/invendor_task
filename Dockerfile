FROM debian:latest

RUN apt-get update
RUN apt-get -y install python3 python3-pip python3.11-venv vim net-tools
RUN python3 -m venv /opt/venv 
ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m pip install requests-oauthlib

ADD *.py /invendor-task/

WORKDIR /invendor-task/

ENTRYPOINT ["python3", "main.py"]
#CMD /bin/bash