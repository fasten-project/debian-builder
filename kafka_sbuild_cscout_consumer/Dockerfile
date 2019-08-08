# vim:set ft=dockerfile:
FROM sbuild_cscout:latest

WORKDIR /root

RUN pip3 install requests BeautifulSoup4 kafka-python

COPY ./entrypoint.py entrypoint.py

COPY ./fstab /etc/schroot/sbuild/fstab

COPY ./analyzer /usr/local/bin/analyzer
RUN chmod 777 /usr/local/bin/analyzer

# DIRECTORY TO SAVE CALL-GRAPHS
RUN mkdir -p /callgraph

ENTRYPOINT ["python3", "entrypoint.py"]
