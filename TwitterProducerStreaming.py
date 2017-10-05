# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:15:15 2017
@author: ANSHUL
"""

import sys
import math
import logging
import tweepy
import json
import time
from config import argument_config
from kafka import KafkaProducer


class TwitterStreamListener(tweepy.StreamListener):
    """This is the stream listener, resposible for listeneing from Twitter
    and receiving data using countinuously Streaming."""

    def __init__(self, hashtags, twitter_ids, kafka_broker_uri, kafka_topic):
        self.t = 60
        self.hashtags = hashtags
        self.twitter_ids = twitter_ids
        self.siesta = 0
        self.nightnight = 0
        self.kafka_topic = kafka_topic
        try:
            self.producer = KafkaProducer(bootstrap_servers=[kafka_broker_uri], value_serializer=lambda m: json.dumps(m).encode('ascii'))
        except:
            logging.error("Error while creating Kafka producer.")

    def on_data(self, response):
        """ This method is invoked on obtaining response data from the
        Twitter stream """

        self.siesta = 0

        # parsing response to JSON format
        json_resp = json.loads(response)

        if (json_resp["retweeted"] is 'true') or ('RT @' in json_resp["text"]):
            return True

        # Writing tweet to specific topic in Kafka.
        user_mentions = json_resp["entities"]["user_mentions"]
        user_mention = user_mentions[len(user_mentions)-1]

        if user_mention["screen_name"] in self.hashtags:

            # Writing Tweet to Kafa Topics into producer
            self.producer.send(self.kafka_topic, {user_mention["screen_name"] : response})
            self.producer.flush()
            logging.info("-- TWEET :: " + json_resp["text"])

    def on_error(self, status_code):
        
        if status_code == 420:
            sleepy = 60 * math.pow(2, self.siesta)
            logging.warn("A reconnection attempt will occur in {0} minutes,\
                         due to ERROR: {1}."
                         .format(str(sleepy/60), str(status_code)))
            time.sleep(sleepy)
            self.siesta += 1
        elif status_code == 401:
            logging.error("INVALID KEY/ACCESS TOKEN(S).")
            sys.exit()
        else:
            sleepy = 5 * math.pow(2, self.nightnight)
            logging.warn("A reconnection attempt will occur in {0} seconds,\
                         due to ERROR: {1}."
                         .format(str(sleepy), str(status_code)))
            time.sleep(sleepy)
            self.nightnight += 1
        return True


if __name__ == '__main__':
    """ Twitter Streaming program execution begins from here."""

    # Declaring logger.
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s %(message)s',
                        level=logging.INFO)

    twitter_hashtags = {}
    
    # Collecting Authentication and other details from arguments.
    consumer_key = argument_config.get('consumer_key')
    consumer_secret = argument_config.get('consumer_secret')
    access_token = argument_config.get('access_token')
    access_token_secret = argument_config.get('access_token_secret')
    twitter_hashtags = argument_config.get('twitter_hashtags')
    kafka_broker_uri = argument_config.get('kafka_broker_uri')
    kafka_topic = argument_config.get('kafka_topic')

    # OAuth authentication functionality for Twitter
    twitter_auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    twitter_auth.set_access_token(access_token, access_token_secret)

    try:
        # Instantiating listener class.
        listener = TwitterStreamListener(twitter_hashtags.keys,
                                         twitter_hashtags.values,
                                         kafka_broker_uri, kafka_topic)
    except:
        logging.error("Error while creating Stream Listener : ")

    # Accessing StreamingAPI using tweepy to Authenticate as Step 1.
    stream = tweepy.Stream(twitter_auth, listener)
    logging.info("Twitter authenticated.")

    while True:
        try:
            # Initializing Streaming for the given Twitter Accounts
            stream.filter(follow=twitter_hashtags.values)
            logging.info("Twitter Streaming initiated...")
        except:
            continue
