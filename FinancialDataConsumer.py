# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 09:38:57 2017

@author: ANSHUL
"""

import logging
from config import argument_config, mongo_config
from kafka import KafkaConsumer
from mongoDBConnection import initialize_mongo, insert_into_mongo
from ckanForMetadata import insert_into_ckan
import json


def main():
    """Initiate the Financial news data reading from Kafka Topics using
    Kafka Consumer."""

    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    kafka_topics = argument_config.get('kafka_topics')
    kafka_broker_uri = argument_config.get('kafka_broker_uri')
    ckan_host = argument_config.get('ckan_host')
    api_key = argument_config.get('api_key')
    publisher = argument_config.get('publisher')
    mongo_uri = mongo_config.get('mongo_uri')

    try:
        consumer = KafkaConsumer(*kafka_topics,
                                 bootstrap_servers=[kafka_broker_uri],
                                 # value_deserializer=lambda m:
                                 #   json.loads(m.decode('ascii')),
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=False)
        for message in consumer:
            try:
                source = message.key
                val_obj = message.value

                json_val_obj = json.loads(val_obj)
                post_url = json_val_obj.keys()[0]
                msg_val = json_val_obj[post_url]

                # print msg_val

                feedObject = {source: msg_val}

                mongo_colln = initialize_mongo(source)
                # part_url = "url-test"
                # feedObject = {source: message.value}
                try:
                    inserted = insert_into_mongo(mongo_colln, feedObject)

                    if inserted:
                        logging.info("Inserted " + source + " data to MongoDB")

                        # Maintain metadata for the inserted data.
                        try:
                            meta_mongo_colln = initialize_mongo("METADATA")
                            meta_feedObj = {source: post_url}
                            insert_into_mongo(meta_mongo_colln, meta_feedObj)
                        except:
                            pass

                        # Maintain CKAN information for each Web source.
                        try:
                            insert_into_ckan(ckan_host, api_key, publisher,
                                             mongo_uri, source)
                            logging.info("Updated CKAN for " + source)
                        except:
                            logging.error("Error while loading to CKAN.")
                    else:
                        logging.info(source + " data not saved in MongoDB")
                except:
                    logging.error("Error while loading to MongoDB.")
                    continue
                finally:
                    feedObject.clear
            except:
                continue
    except IOError:
        logging.error("Error while loading Topics of Kafka Consumer.")
        pass


if __name__ == '__main__':
    main()
