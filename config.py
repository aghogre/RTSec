# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 16:48:44 2017
@author: ADMIN
"""

import os

HASHTAGS = ["business", "WSJ", "WSJMarkets", "Forbes", "TheEconomist", "FT",
            "Reuters", "nytimes", "MarketFolly", "CNNMoney", "TheStreet",
            "MarketWatch", "YahooFinance", "jimcramer", "TruthGundlach",
            "Carl_C_Icahn", "ReformedBroker", "Schuldensuehner",
            "LizAnnSonders", "NorthmanTrader", "Frances_Coppola", "bySamRo",
            "BrianSozzi", "Wu_Tang_Finance", "TheStalwart", "RyanDetrick",
            "zerohedge", "Amena_Bakr", "kitjuckes", "Benzinga",
            "CiovaccoCapital", "JLyonsFundMGMT", "jasonzweigwsj",
            "Samir_Madani", "Brenda_Kelly", "LiveSquawk", "vexmark",
            "Sassy_SPY", "StockTwits", "KeithMcCullough", "FXCM", "JoelKruger",
            "bespokeinvest", "IBDinvestors", "PaulKrugman", "JustinWolfers",
            "jessefelder", "DailyFXTeam", "Ukarlewitz", "Stephanie_Link"]

argument_config = {
    'consumer_key': os.getenv('CONSUMER_KEY', '2a3ZB5yDRj1KsRVN46ScMfjMM'),
    'consumer_secret': os.getenv('CONSUMER_SECRET', 'MBhC08qXb2ooynexboPWNdVCVzYnWfUl0IZCXQzHTDNDXII2hK'),
    'access_token': os.getenv('ACCESS_TOKEN', '912282441276055552-8ZR1KVdWtbNzlgHkQlPzQtYJqgGrOZd'),
    'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET', 'X2axJM3ETUfu2wEBjl2XWZ5Dr9yy5j3luwm4FkWWJFRun'),
    'twitter_hashtags': os.getenv('TWITTER_HASHTAGS', HASHTAGS),
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', 'localhost:9092'),
    'kafka_topic': os.getenv('KAFKA_TOPIC', 'tweeter')
}

