# vim:set ft=dockerfile:
FROM python:3

WORKDIR /root

RUN mkdir -p /root/sources

RUN pip install kafka-python

COPY ./entrypoint.py entrypoint.py

ENTRYPOINT ["python", "entrypoint.py"]
