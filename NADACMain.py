# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 16:50:40 2017

@author: ANSHUL
"""
import time
from datetime import datetime 
from NADACExtraction import data_Extractor
import logging
from mongoDBConnection import initialize_mongo
from config import mongo_config


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)
    # Initializing mongo db and collection
    mongo_colln = initialize_mongo(mongo_config.get('col_name'))
    logging.info("Loading NADAC data")
    try:
        # Calling DATA EXTRACTOR
        data_Extractor(mongo_colln)
        today = datetime.today().strftime('%d/%m/%Y')
        logging.info('No more new/updated data available for- '+today)
        logging.info('Program is completed, Auto-restart in 24 hrs')
        time.sleep(86400)
    except:
        raise
        logging.error("Error occurred while loading NADAC data.")

if __name__ == "__main__":
    main()
