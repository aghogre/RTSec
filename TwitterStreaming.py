# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:15:15 2017

@author: ANSHUL
"""

import logging
import tweepy
import json
import datetime
import time
import requests
import re
from config import argument_config
from kafka import KafkaProducer
from bs4 import BeautifulSoup


class TwitterStreamListener(tweepy.StreamListener):
    """This is the stream listener, resposible for listeneing from Twitter
    and receiving data using countinuously Streaming."""

    def __init__(self, hashtags, twitter_ids, kafka_broker_uri):
        self.t = 60
        self.hashtags = hashtags
        self.twitter_ids = twitter_ids
        self.producer = KafkaProducer(bootstrap_servers=[kafka_broker_uri])

    def on_data(self, response):
        """ This method is invoked on obtaining response data from the
        Twitter stream """

        # parsing response to JSON format
        json_resp = json.loads(response)

        if (json_resp["retweeted"] is 'true') or ('RT @' in json_resp["text"]):
            return True

        # Writing the Twitter response tweets to a file
        filename = "twitter_" + str(datetime.date.today()).replace('-', '') +\
            ".json"
        with open(filename, 'a+') as response_file:
            json.dump(json_resp, response_file, sort_keys=True, indent=4)

        # Writing tweet to specific topic in Kafka.
        user_mentions = json_resp["entities"]["user_mentions"]
        for user_mention in user_mentions:
            if user_mention["screen_name"] in self.hashtags:
                account_name = user_mention["screen_name"]
                with open(account_name+'.json', 'a+') as acc_file:
                    json.dump(json_resp, acc_file, sort_keys=True, indent=4)
                # Writing Topics into producer
                self.producer.send(account_name, json.dumps(json_resp))
                self.producer.flush()
                logging.info("-- TWEET :: " + json_resp["text"])

    def on_error(self, status):
        """ Handles the response error status. """
        print status
        if status is '420':
            print 'Retrying after' + self.t + 'secs'
            self.t = self.t*2
            time.sleep(self.t)
            stream.filter(follow=self.twitter_ids)


def getTwitterIds(twitter_accounts):
    """ Fetches the twitter Ids for the Twitter accounts based on Hashtags."""

    twitter_ids = []
    getIdUrl = "http://gettwitterid.com/?submit=GET+USER+ID&user_name={0}"

    for ta in twitter_accounts:
        r = requests.get(getIdUrl.format(ta))
        soup = BeautifulSoup(r.content, "html.parser")
        p_list = soup.find_all('p')
        for p_val in p_list:
            if 'Twitter User ID:' in p_val:
                id_line = p_list[p_list.index(p_val)+1]
                id_val = re.split('[< >]', str(id_line))[2]
                twitter_ids.append(id_val)
    return twitter_ids


if __name__ == '__main__':
    """ Twitter Streaming program execution begins from here."""

    # Declaring logger.
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s %(message)s',
                        level=logging.INFO)

    # Collecting Authentication and other details from arguments.
    consumer_key = argument_config.get('consumer_key')
    consumer_secret = argument_config.get('consumer_secret')
    access_token = argument_config.get('access_token')
    access_token_secret = argument_config.get('access_token_secret')
    twitter_hashtags = argument_config.get('twitter_hashtags')
    kafka_broker_uri = argument_config.get('kafka_broker_uri')

    # OAuth authentication functionality for Twitter
    twitter_auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    twitter_auth.set_access_token(access_token, access_token_secret)

    # Fetching Ids for Twitter accounts.
    twitter_ids = getTwitterIds(twitter_hashtags)

    # Instantiating listener class.
    listener = TwitterStreamListener(twitter_hashtags, twitter_ids,
                                     kafka_broker_uri)

    # Accessing StreamingAPI using tweepy to Authenticate as Step 1.
    stream = tweepy.Stream(twitter_auth, listener)
    logging.info("Twitter authenticated.")

    while True:
        try:
            # Initializing Streaming for the given Twitter Accounts
            stream.filter(follow=twitter_ids)
            logging.info("Twitter Streaming initiated...")
        except:
            continue
