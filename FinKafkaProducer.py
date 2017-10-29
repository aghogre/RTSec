# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 13:22:38 2017

@author: RAVITHEJA
"""

import logging
import json
from config import argument_config
from kafka import KafkaProducer



class finKafkaProducer():
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s \
                            %(module)s.%(funcName)s %(message)s',
                            level=logging.INFO)
        kafka_broker_uri = argument_config.get('kafka_broker_uri')
        self.producer = KafkaProducer(bootstrap_servers=[kafka_broker_uri],
                                      value_serializer=lambda v:
                                          json.dumps(v).encode('utf-8'))

    def kafkaSend(self, feedName, part_url, response):
        """Sends the message to the given Kafka topic."""
        data = {part_url: response}
        json_data = json.dumps(data)

        try:
            # Kafka producer writing Post/Webpage content to Kafka Topics.
            self.producer.send(feedName, key=feedName,  # value=response)
                               value=json.loads(json_data))
            self.producer.flush()
            logging.info("-- FEED :: " + feedName)
        except:
            logging.info("KafkaError in producer:: "+ feedName)
        