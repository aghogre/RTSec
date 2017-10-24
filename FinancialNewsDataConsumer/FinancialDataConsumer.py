# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 09:38:57 2017

@author: ANSHUL
"""
import logging
from config import argument_config
from kafka import KafkaConsumer
from mongoDBConnection import initialize_mongo, insert_into_mongo


kafka_broker_uri = argument_config.get('kafka_broker_uri')


def main():
    """Initiate the Financial news extraction functionality.
    To make calls to RSS feed parser, Sitemap parser, Scrapy extractor and
    API calls, if any."""

    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    kafka_topics = argument_config.get('kafka_topics')

    try:
        consumer = KafkaConsumer(*kafka_topics,
                                 bootstrap_servers=[kafka_broker_uri],
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=False)
        for message in consumer:
            print message.key
            mongo_colln = initialize_mongo(message.key)
            feedObject = {message.key: message.value}
            if insert_into_mongo(mongo_colln, feedObject):
                    logging.info("Inserted " + message.key + " data to Mongo"
                                 + " successfully")
                    feedObject.clear
    except IOError:
        logging.info("Error while loading to consumer/mongo ")
        pass


if __name__ == '__main__':
    main()
