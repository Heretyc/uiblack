# syntax=docker/dockerfile:1
FROM python:3.10.0b4
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt