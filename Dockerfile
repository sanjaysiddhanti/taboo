FROM python:3.8.2-buster

WORKDIR /app
ENV PYTHONPATH /app

RUN curl -sL https://deb.nodesource.com/setup_13.x | bash -
RUN apt-get install -y nodejs

COPY requirements.txt /app/requirements.txt
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
RUN npm install
RUN pip install -r /app/requirements.txt

COPY public/ /app/public/
COPY src/ /app/src/

ENV FLASK_APP src/app.py
EXPOSE 5000