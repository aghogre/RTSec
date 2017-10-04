# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 13:27:54 2017
@author: RAVITHEJA
"""

import logging
import json
from config import argument_config, mongo_config
from kafka import KafkaConsumer
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
            self.consumer = KafkaConsumer(self.kafka_topic, bootstrap_servers=[kafka_broker_uri],
                                          value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                          auto_offset_reset='earliest', enable_auto_commit=False)
        except:
            logging.error("Error while creating Kafka Consumer : ") 

    def initiateKafkaConsumer(self):
        
        #self.consumer.subscribe(self.kafka_topic)
        try:
            for message in self.consumer:
                object = {self.kafka_topic : message}
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
    twitter_hashtags = argument_config.get('twitter_hashtags')
    kafka_broker_uri = argument_config.get('kafka_broker_uri')
    kafka_topic = argument_config.get('kafka_topic')

    # Initiate Kafka consumer
    consumer_obj = KafkaConsumerForTwitterStream(kafka_broker_uri, kafka_topic)
    consumer_obj.initiateKafkaConsumer()