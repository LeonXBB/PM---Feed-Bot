# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR "/app"
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV PORT=80
EXPOSE 80

CMD [ "python3", "-m" , "main"]

