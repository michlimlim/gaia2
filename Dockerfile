FROM ubuntu:latest
MAINTAINER Tim Adamson "tim.adamson@yale.edu"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
#CMD python main.py -me localhost:5000 -them localhost:5001 localhost:5002
