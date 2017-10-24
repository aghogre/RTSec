# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:25:49 2017

@author: RAVITHEJA
"""

import os

SOURCES = [
        "thomson_reuters",
        "wall_street_journal",
        "cnbc",
        "cnn_money",
        "morning_star",
        "rtt_news",
        "seeking_alpha",
        "yahoo_finance",
        "motley_fool",
        "zacks_investment",
        "bloomberg",
        "market_watch",
        "forbes",
        "the_street",
        "msci_dataset",
        "ceic_dataset",
        "finviz",
        "googleFinanceNews",
        "googleStocks",
        "yahooStocks",
        #"financial_times",
         ]


argument_config = {
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', '173.193.179.253:9097'),
    'kafka_topics': os.getenv('KAFKA_TOPICS', SOURCES)
}

mongo_config = {
    'mongo_uri': os.getenv('MONGO_URI', 'localhost:27017'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', False),
    'requires_auth': os.getenv('REQUIRES_AUTH', 'false'),
    'mongo_username': os.getenv('MONGO_USER', ''),
    'mongo_password': os.getenv('MONGO_PASSWORD', ''),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'dbadmin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'MONGODB-CR'),
    'db_name': os.getenv('MONGO_DB_NAME', 'financenews'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'csrt'),
}
