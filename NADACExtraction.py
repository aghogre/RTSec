# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 15:30:48 2017

@author: ANSHUL
"""
from datetime import datetime, timedelta
import logging
from sodapy import Socrata
from mongoDBConnection import update_mongo_collection
from config import argument_config


def data_Extractor(mongo_colln):
    # This method is about to collect NADAC historical and new data using API
    try:
        client = Socrata("data.medicaid.gov",
                         argument_config.get('my_app_token'),
                         argument_config.get('user_id'),
                         argument_config.get('password'))
        counter = 0
        results = '1'
        # Until API returns zero data loop will run, till present.
        while len(results) != 0:
            # If mongo collection already contains some data , will start from there onwards.
            if mongo_colln.count() != 0:
                logging.info('NADAC Update Loading.')
                Newest_ele = mongo_colln.find().sort('_id', -1).limit(1)
                for element in Newest_ele:
                    AODString_increment = datetime.strptime(
                        str(element['as_of_date']),
                        "%m/%d/%Y") + timedelta(days=1)
                    AODString = AODString_increment.strftime('%Y-%m-%dT%H:%M:%S')
            # If collection is empty, fresh data from beginning will store to mongo
            else:
                logging.info('NADAC Archive Loading.')
                AODString = '2013-11-01T00:00:00'
            today = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
            # API call from last stored data to collection till at present.
            results = client.get("tau9-gfwr", where="as_of_date between '"+str(AODString)+"' and '"+str(today)+"'", order='as_of_date ASC', limit=50000, offset=counter)
            counter += 1
            if len(results) != 0:
                for feedObject in results:
                    current_time = datetime.today().strftime('%Y-%d-%m %H:%M:%S')
                    ndc = feedObject['ndc']
                    AOD = feedObject['as_of_date']
                    # Creating mongo id by appending ndc and as_of_date
                    _id = ndc+str(AOD).replace("-", "")\
                                      .replace(":", "")\
                                      .replace("/", "")\
                                      .replace(".", "")\
                                      .replace("T", "")
                    feedObject['Created_Time'] = current_time
                    feedObject['as_of_date'] = datetime.strptime(
                            str(feedObject['as_of_date'])+'000',
                            "%Y-%m-%dT%H:%M:%S.%f").strftime('%m/%d/%Y')
                    logging.info("Inserting into Mongo - "+ndc)
                    # Upserting to Mongo to avoid duplications.
                    update_mongo_collection(mongo_colln, _id, feedObject)
            else:
                break
    except:
        raise
        logging.error("Issue while getting NADAC Data")
