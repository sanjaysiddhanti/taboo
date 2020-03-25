FROM python:3.8.2-buster

WORKDIR /app
ENV PYTHONPATH /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY src/ /app/src/

ENV FLASK_APP src/app.py
EXPOSE 5000