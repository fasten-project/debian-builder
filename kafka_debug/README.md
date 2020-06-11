# Docker Image to debug kafka topic

```bash
docker run -it --net=host schaliasos/kafka-debug /bin/bash
ipython -i entrypoint.py
# Set TOPIC_CG, TOPIC_ERR, TOPIC_LOG, SERVERS
cg, err, log = get_messages()
# Do your analysis on the messages
```
