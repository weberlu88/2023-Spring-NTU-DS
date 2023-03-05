FROM python:3.9-slim
WORKDIR /app
COPY . .

ENV FLASK_APP server/server.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 5000
ENV FLASK_RUN_HOST 0.0.0.0

RUN apt-get update
RUN pip install flask requests

EXPOSE 5000

CMD "python client/client.py" 
# 怎麼不執行這行 QQ
    
# CMD ["flask", "run"] # ok
# CMD ["python", "server/server.py"]
# https://github.com/docker/awesome-compose/tree/master/nginx-flask-mysql