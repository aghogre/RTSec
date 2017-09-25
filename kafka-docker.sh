docker run -d -p 2181:2181 --name zookeeper jplock/zookeeper

docker run -d --name kafka --link zookeeper:zookeeper ches/kafka

docker ZK_IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' zookeeper)
docker KAFKA_IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' kafka)

docker run --rm ches/kafka