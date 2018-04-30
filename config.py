# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 16:48:44 2017
@author: ADMIN
"""

import os

TWITTER_ACCOUNT_IDS = { "business":"34713362",
                        "MarketFolly":"14173032",
                        "TheStreet":"15281391",
                        "MarketWatch":"624413",
                        "YahooFinance":"19546277",
                        "Schuldensuehner":"40129171",
                        "LizAnnSonders":"2961589380",
                        "NorthmanTrader":"714051110",
                        "bySamRo":"239026022",
                        "RyanDetrick":"21232827",
                        "Benzinga":"44060322",
                        "LiveSquawk":"59393368",
                        "KeithMcCullough":"18378349",
                        "FXCM":"110793585",
                        "bespokeinvest":"28571999",
                        "IBDinvestors":"21328656",
                        "DailyFXTeam":"28366310",
                        "Ukarlewitz":"37284991",
                        "Stephanie_Link":"455309376"
                        }

argument_config = {
    'consumer_key': os.getenv('CONSUMER_KEY', 'KEKRvtZRsORoPEe35eGXxD2RI'),
    'consumer_secret': os.getenv('CONSUMER_SECRET', 'ujTrT5usnEp23SlFGVOgWSmezfc7UoVxZ8WnS5KmEXsdDyPqkn'),
    'access_token': os.getenv('ACCESS_TOKEN', '262467111-ghiak79TmLJwBkQTs9C10DMqsqZPSuPXQXCjQajt'),
    'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET', 'AQuOv9iT1ofxQlNOtYHr2Ret6EnDoLcBU7iyfDDnFHSoR'),
    'twitter_hashtags': os.getenv('TWITTER_HASHTAGS', TWITTER_ACCOUNT_IDS),
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', 'localhost:9092'),
    'kafka_topic': os.getenv('KAFKA_TOPIC', 'twitterhandle')
}
