# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 14:44:42 2017

@author: RAVITHEJA
"""

import logging
from pymongo import MongoClient
from config import mongo_config
from uuid import uuid1


def make_mongo_connection(collection_name):
    """This is to establish connection with MongoDB with provided
    authentication Credentials"""

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

    # Authenticate MongoDB (Optional)
    if requires_auth == 'true':
        client.the_database.authenticate(mongo_username,
                                         mongo_password,
                                         source=mongo_auth_source,
                                         mechanism=mongo_auth_mechanism
                                         )
    db = client[db_name]
    mongo_colln = db[collection_name]

    # Testing Index with Unique element, to avoid failure of Index creation,
    # in case of Collection doesnot exist.
    test_uuid = str(uuid1())
    try:
        mongo_colln.insert_one({'uuid': test_uuid})
        mongo_colln.delete_one({'uuid': test_uuid})
    except:
        logging.debug("Collection %s already exists" % collection_name)

    return mongo_colln


def initialize_mongo(source):
    """Initializes MongoDB Connection and returns MongoCollection for the
    given Index."""

    # Fetching config parameters.
    mongo_index_name = mongo_config.get('mongo_index_name')

    try:
        # Creating Mongo Collection
        mongo_colln = make_mongo_connection(source)

        # Create index, if it is not available.
        if mongo_index_name not in mongo_colln.index_information():
            mongo_colln.create_index(mongo_index_name, unique=False)

    except IOError:
        logging.error("Could not connect to Mongo Server")

    return mongo_colln


def insert_into_mongo(mongo_colln, feed_object, object_name):
    """To insert given JSON data into MongoDB."""
    try:
        feed_object['_id'] = object_name
        mongo_colln.insert_one(feed_object)
    except:
        raise
        logging.error("Mongo Insert Exception.")
    finally:
        feed_object.clear
    return True


def update_mongo_doc(mongo_colln, mongo_id, feedObject):
    """To update existing data into MongoDB."""
    try:
        mongo_colln.update_one({'_id': mongo_id}, {"$set": feedObject},
                               upsert=True)
    except:
        raise
        logging.error("Mongo Insert Exception.")
    finally:
        feedObject.clear
    

def update_mongo_collection(mongo_colln, mongo_id, feed_object):
    """To update existing JSON data into MongoDB."""
    try:
        new_feedobj = {}
        datasetsList = []
        datasetkey = ''
        metadata_cursor = mongo_colln.find_one({'_id': mongo_id})
        for mcur in metadata_cursor:
            if not mcur=='_id':
                datasetkey = mcur
                datasetsList.extend(metadata_cursor[mcur])
        datasetsList.extend(feed_object[datasetkey])
        new_feedobj[mcur] = datasetsList
        
        mongo_colln.update_one({'_id': mongo_id}, {"$set": new_feedobj},
                               upsert=True)
    except:
        raise
        logging.error("Mongo Update Exception.")
    finally:
        pass
        #feed_object.clear
