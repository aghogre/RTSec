# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 16:48:44 2017
@author: ADMIN
"""

import os

argument_config = {
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', 'localhost:9092'),
    'kafka_topic': os.getenv('KAFKA_TOPIC', 'twitterhandle')
   
}

mongo_config = {
    'requires_auth': os.getenv('REQUIRES_AUTH', 'false'),
    'mongo_uri': os.getenv('MONGO_URI', 'localhost:27017'),
    'mongo_username': os.getenv('MONGO_USER', ''),
    'mongo_password': os.getenv('MONGO_PASSWORD', ''),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'dbadmin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'MONGODB-CR'),
    'db_name': os.getenv('MONGO_DB_NAME', 'twitter'),
    'col_name': os.getenv('MONGO_COL_NAME', 'tweets'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'csrt'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', False)
}
