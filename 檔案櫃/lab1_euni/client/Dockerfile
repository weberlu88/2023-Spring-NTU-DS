FROM python:3.9-slim

RUN mkdir /frontend
WORKDIR /frontend

RUN pip install --upgrade pip && \
    pip install requests
COPY . .

# CMD ["python","client.py"]

