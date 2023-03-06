FROM python:3.7.2-stretch
 
WORKDIR /app
 
ADD . /app
 
RUN pip install Flask 

ENV FLASK_APP=server

ENV	FLASK_RUN_HOST=0.0.0.0

CMD flask run