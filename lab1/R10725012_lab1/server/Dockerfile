FROM python:3.9-slim

RUN mkdir /backend
WORKDIR /backend

RUN pip install --upgrade pip && \
    pip install flask
COPY . .

EXPOSE 5000
