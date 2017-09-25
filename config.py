# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 16:48:44 2017

@author: ADMIN
"""

import os

HASHTAGS = ["WSJ", "business", "Forbes", "FT", "Reuters", "nytimes",
            "TheStreet", "TheEconomist", "WSJMarkets", "CNNMoney",
            "MarketWatch", "YahooFinance", "jimcramer", "bySamRo",
            "BrianSozzi", "TruthGundlach", "MarketFolly", "Carl_C_Icahn",
            "ReformedBroker", "Northman Trader", "Samir_Madani"]

argument_config = {
    'consumer_key': os.getenv('CONSUMER_KEY', 'TjniEtqN8FumhX7BsnmN9GUhL'),
    'consumer_secret': os.getenv('CONSUMER_SECRET', 'T62bKQcKgFlctabY63eTxQ0WlGc8GOV4AkvnMaAM87NRFw726m'),
    'access_token': os.getenv('ACCESS_TOKEN', '140517807-YTwIXlHvEKIRKxxTLm0USi9rYzbi2DMfu8dFOCqa'),
    'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET', 'Qp3pvMcVF9ka4AmhgeNHzN9k918X8ALqcXjOkXLQHY1no'),
    'twitter_hashtags': os.getenv('TWITTER_HASHTAGS', HASHTAGS),
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', '173.193.179.253:9092'),
}
