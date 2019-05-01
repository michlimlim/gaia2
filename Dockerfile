FROM ubuntu:latest
MAINTAINER Tim Adamson "tim.adamson@yale.edu"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["python main.py -me 5000 -them 5001"]