# vim:set ft=dockerfile:
FROM schaliasos/sbuild:latest

RUN pip3 install requests BeautifulSoup4 kafka-python fasten

COPY ./entrypoint.py entrypoint.py

ENTRYPOINT ["python3", "entrypoint.py"]
