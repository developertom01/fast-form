FROM python:3.12-slim

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./app ./app
COPY ./bin ./bin
COPY ./internal ./internal
COPY ./lib ./lib
COPY ./public ./public
COPY ./scripts ./scripts
COPY ./templates ./templates
COPY ./utils ./utils
COPY ./config.py ./config.py
COPY ./server.py ./server.py
