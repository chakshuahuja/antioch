FROM python:3.4

RUN mkdir /app
WORKDIR /app

RUN apt-get install libxml2-dev libxslt1-dev libssl-dev

ADD requirements.txt /app/
RUN pip3 install -r requirements.txt


