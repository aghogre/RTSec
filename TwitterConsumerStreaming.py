# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 13:27:54 2017
@author: Anshul
"""

import logging
import json
from config import argument_config, mongo_config
#from kafka import KafkaConsumer
from confluent_kafka import Consumer, KafkaError
from mongoconnection import make_mongo_connection


class KafkaConsumerForTwitterStream():
    """ This class initiates and starts Kafka Consumer Thread. """

    def __init__(self, kafka_broker_uri, kafka_topic):
        self.kafka_topic = kafka_topic
        self.col = make_mongo_connection(mongo_config.get('col_name'))
        index_name = mongo_config.get('mongo_index_name')
        if index_name not in self.col.index_information():
            self.col.create_index(index_name, unique=False)
        try:
            self.consumer = Consumer({'bootstrap.servers': kafka_broker_uri, 'group.id': 'mygroup',
                  'default.topic.config': {'auto.offset.reset': 'earliest'}})
    

            """KafkaConsumer(self.kafka_topic, bootstrap_servers=[kafka_broker_uri],
                                          value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                          auto_offset_reset='earliest', enable_auto_commit=False)"""
        except:
            logging.error("Error while creating Kafka Consumer : ") 

    def initiateKafkaConsumer(self):
        
        #self.consumer.subscribe(self.kafka_topic)
        try:
            self.consumer.subscribe([self.kafka_topic])
            
            running = True
            
            while running:
                msg = self.consumer.poll()
                if not msg.error():
                    record = json.loads(msg.value().decode('ascii'))
            
                    object = {self.kafka_topic : record}
                    logging.info("Loading Consumer message in Mongo")
                    self.col.insert_one(object)
                    object.clear
        except:
            logging.error("Error in loading data to Mongo")
    

if __name__ == '__main__':
    """ Twitter Streaming towards Kafka Consumer."""

    # Declaring logger.
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s %(message)s',
                        level=logging.INFO)

    # Collecting Authentication and other details from arguments.
    kafka_broker_uri = argument_config.get('kafka_broker_uri')
    kafka_topic = argument_config.get('kafka_topic')

    # Initiate Kafka consumer
    consumer_obj = KafkaConsumerForTwitterStream(kafka_broker_uri, kafka_topic)
    consumer_obj.initiateKafkaConsumer()
