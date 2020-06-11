# vim:set ft=dockerfile:
FROM python:3

WORKDIR /root

RUN pip install kafka-python ipython ipdb
COPY ./entrypoint.py entrypoint.py
RUN touch __init__.py
