# vim:set ft=dockerfile:
FROM schaliasos/sbuild-cscout:latest

RUN pip3 install requests BeautifulSoup4 kafka-python fasten==0.0.2

COPY ./entrypoint.py entrypoint.py

ENTRYPOINT ["python3", "entrypoint.py"]
