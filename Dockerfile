FROM python:3.12-bullseye

ENV PYTHONDONTWRITEBYTECODE 1 # Prevents Python from writing pyc files to disc
ENV PYTHONUNBUFFERED 1 # Prevents Python from buffering stdout and stderr
ENV SHELL /bin/bash

RUN mkdir /app
RUN mkdir -p /app/staticfiles

RUN mkdir -p /app/static
WORKDIR /app

RUN apt update

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

CMD ["/bin/bash","./start_services.sh"]
