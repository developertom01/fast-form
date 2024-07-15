FROM Python:3.10-slim

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./applications dest
