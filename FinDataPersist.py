# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 10:07:02 2017

@author: RAVITHEJA
"""

import logging
from config import mongo_config
from mongoDBConnection import initialize_mongo, insert_into_mongo
from mongoDBConnection import update_mongo_doc
from ckanForMetadata import insert_into_ckan


def persistFinData(source, json_data, sno, data, dataset_code, description,
                   meta_updated, metadata_cursor, mongo_id, data_mode):
    """Collects the Quandl JSON response data and inserts into mongo collection
    and updates CKAN."""

    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    # fetching arguments from config.
    mongo_uri = mongo_config.get('mongo_uri')
    meta_col_name = mongo_config.get('meta_colln_name')

    try:
        # Build object for storing in MongoDB.
        data["dataset_code"] = dataset_code
        mongo_colln = initialize_mongo(source)
        code_part = dataset_code.split("/")[1]

        #logging.info(data_mode)
        if data_mode == "initial":
            #logging.info(mongo_colln data, code_part + "_" + str(sno))
            insert_into_mongo(mongo_colln, data,
                              code_part + "_" + str(sno))
            if meta_updated:
                # METADATA Collection
                meta_mongo_colln = initialize_mongo(meta_col_name)
                meta_feedObj = json_data["dataset"]
                insert_into_mongo(meta_mongo_colln, meta_feedObj,
                                  source + "." + code_part)
                # CKAN
                refresh_rate = json_data["dataset"]["frequency"]
                insert_into_ckan(mongo_uri, source, description,
                                 refresh_rate)
        elif data_mode == "update":
            insert_into_mongo(mongo_colln, data,
                              code_part + "_" + str(sno))

        elif data_mode == "no_date":
            insert_into_mongo(mongo_colln, data,
                              code_part + "_" + str(sno))
            #update_mongo_doc(mongo_colln, mongo_id, data)
    except:
        raise
        logging.error("Error while Initializing Mongo.")
    finally:
        data.clear

    return meta_updated
