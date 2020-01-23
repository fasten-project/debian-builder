# vim:set ft=dockerfile:
FROM schaliasos/sbuild_cscout:latest

RUN pip3 install requests BeautifulSoup4 kafka-python

COPY ./entrypoint.py entrypoint.py

ENTRYPOINT ["python3", "entrypoint.py"]