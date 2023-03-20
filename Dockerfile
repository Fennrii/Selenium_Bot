FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /selenium
RUN mkdir /selenium/txtFiles
RUN mkdir /selenium/csvFiles
COPY ./selenium /selenium
WORKDIR /selenium