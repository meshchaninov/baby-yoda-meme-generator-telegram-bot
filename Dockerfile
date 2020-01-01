FROM python:3.7.4-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY env /app/env

RUN source /app/env

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev

RUN apk add  --no-cache ffmpeg

COPY files /app/files

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apk del build-deps

COPY src /app/src

RUN ["python", "/app/src/main.py"]

EXPOSE 80
