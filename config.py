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

        "google_fin_news",

        "financial-times",
        # "the-wall-street-journal",

        # "google_stocks",
        # "yahoo_stocks",
        ]

argument_config = {
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', '173.193.179.253:9097'),
    'kafka_topics': os.getenv('KAFKA_TOPICS', SOURCES),
    'ckan_host': os.getenv('CKAN_HOST', 'http://40.71.214.191:80'),
    'api_key': os.getenv('CKAN_API_KEY', '3474fcd0-2ebc-4036-a60a-8bf77eea161f'),
    'publisher': os.getenv('PUBLISHER', 'Randomtrees'),
}

mongo_config = {
    'mongo_uri': os.getenv('MONGO_URI', 'localhost:27017'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', False),
    'requires_auth': os.getenv('REQUIRES_AUTH', 'false'),
    'mongo_username': os.getenv('MONGO_USER', ''),
    'mongo_password': os.getenv('MONGO_PASSWORD', ''),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'dbadmin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'MONGODB-CR'),
    'db_name': os.getenv('MONGO_DB_NAME', 'fin'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'csrt'),
}
