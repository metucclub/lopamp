FROM python:3-alpine

RUN mkdir -p /app
WORKDIR /app

RUN apk add --upgrade  \
    build-base \
    libffi-dev \
    mariadb-dev \
    libxml2-dev \
    libxslt-dev \
    py2-psycopg2 \
    zlib-dev \
    jpeg-dev \
    gettext \
    nodejs \
    npm \
    libsass \
    git \
    zip \
    unzip \
    nano \
	vim \
	bash

ENV LIBRARY_PATH=/lib:/usr/lib
ENV PYTHONUNBUFFERED 1

COPY package.json .
RUN npm install .

COPY requirements.txt .

RUN pip install cffi && \
    pip install -r requirements.txt && \
    pip install gunicorn

COPY . .

RUN git clone https://github.com/oznakn/docker-scripts && \
	mv docker-scripts/*.sh . && \
	rm -rf docker-scripts && \
	mkdir -p ./db

RUN chmod a+x backup-data.sh restore-data.sh docker-wait-for-it.sh
