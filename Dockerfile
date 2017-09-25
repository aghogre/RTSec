FROM alpine:3.6

RUN  apk add --no-cache --update bash
RUN apk --update add python py-pip gcc openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip 
     
ADD . /TwitterStreaming

WORKDIR /TwitterStreaming

docker run -d -p 2181:2181 --name zookeeper jplock/zookeeper

docker run -d --name kafka --link zookeeper:zookeeper ches/kafka

docker ZK_IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' zookeeper)
docker KAFKA_IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' kafka)

docker run --rm ches/kafka

RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c","source arguments.env && python TwitterStreaming.py"]