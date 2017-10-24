# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 14:44:42 2017

@author: RAVITHEJA
"""

from pymongo import MongoClient
from config import mongo_config


def make_mongo_connection(collection_name):
    """This is to establish connection with MongoDB with desired Credentials"""

    # Fetching config parameters.
    mongo_uri = mongo_config.get('mongo_uri')
    ssl_required = mongo_config.get('ssl_required')
    requires_auth = mongo_config.get('requires_auth')
    mongo_username = mongo_config.get('mongo_username')
    mongo_password = mongo_config.get('mongo_password')
    mongo_auth_source = mongo_config.get('mongo_auth_source')
    mongo_auth_mechanism = mongo_config.get('mongo_auth_mechanism')
    db_name = mongo_config.get('db_name')

    # Instantiating MongoClient
    client = MongoClient(mongo_uri, ssl=ssl_required)

    if requires_auth == 'true':
        client.the_database.authenticate(mongo_username,
                                         mongo_password,
                                         source=mongo_auth_source,
                                         mechanism=mongo_auth_mechanism
                                         )
    db = client[db_name]
    return db[collection_name]


def initialize_mongo(source):
    # Creating Mongo Collection
    mongo_colln = make_mongo_connection(source)
    mongo_index_name = mongo_config.get('mongo_index_name')
    if mongo_index_name not in mongo_colln.index_information():
        mongo_colln.create_index(mongo_index_name, unique=False)
    return mongo_colln


def insert_into_mongo(mongo_colln, feed_object):
    """To insert a news feed/post, given in JSON format, into MongoDB."""
    mongo_colln.insert_one(feed_object)
    feed_object.clear
    return True
