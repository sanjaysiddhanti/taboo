FROM python:3.8.2-buster

WORKDIR /app
ENV PYTHONPATH /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY src/ app/src/