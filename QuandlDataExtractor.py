# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 10:07:02 2017

@author: RAVITHEJA
"""

import time
import logging
import json
import os
import requests as req
from config import argument_config, mongo_config
from Quandl_API_Datasets import getCodesInCSVsForAllDatasets
from FinDataPersist import persistFinData
from mongoDBConnection import initialize_mongo
from datetime import datetime, timedelta


def saveQuandlData(resp_data, src_colln_name, dataset_descrpn,
                   metadata_cursor, src_colln, dataset_code, mongo_id,
                   data_mode, prev_count):
    try:
        # Need JSON format to save in Mongo
        json_data = json.loads(resp_data)

        if "dataset" not in json_data \
                or len(json_data["dataset"]["data"]) == 0:
            return

        # Parse the 'data' column-wise
        parsed_json_data = parseDataColumns(
                json_data["dataset"]["column_names"],
                json_data["dataset"]["data"])

        logging.info(str(len(parsed_json_data)) + " new records in "
                     + dataset_code)

        meta_updated = True
        del json_data["dataset"]["data"]

        # Add the 'created_time' field for every record.
        json_data["dataset"]["created_time"] = datetime.now()\
                                                .strftime("%Y-%m-%d %H:%M:%S")

        for sno, data in enumerate(parsed_json_data, start=1):
            # Check if historical data available and skip.
            src_cursor = src_colln.find_one({dataset_code: data})
            if src_cursor:
                continue

            # Add the 'created_time' field for every record.
            data["created_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Persist the obtained Financial Data
            persistFinData(src_colln_name, json_data, sno + prev_count, data,
                           dataset_code, dataset_descrpn, meta_updated,
                           metadata_cursor, mongo_id, data_mode)
            meta_updated = False
            
    except:
        return


def parseDataColumns(column_names, json_data_part):
    """Parses the json data from list of elements to the list of dicts with
    keys as in column_names and values of each record of Data from dataset."""

    json_data_parsed = []
    column_names = [c.replace('.', '') for c in column_names]
    for rec in json_data_part:
        json_data_parsed.append({column_names[c]: rec[c]
                                for c in range(len(column_names))})
    return json_data_parsed


def main():
    """Initiates the Financial news extraction from Quandl using API calls."""

    t1 = time.time()
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    # fetching arguments from config.
    quandl_apikey = argument_config.get('quandl_apikey')
    meta_col_name = mongo_config.get('meta_colln_name')
    quandl_codes_colln_name = mongo_config.get('quandl_codes_colln_name')

    qcodes_colln = initialize_mongo(quandl_codes_colln_name)
    qcodes_cursor = qcodes_colln.find()

    for qcur in qcodes_cursor:
        curr_date = datetime.now().strftime("%Y-%m-%d")
        
        codes_dt = datetime(*map(int, (qcur['created_time']).split("-")))
        curr_dt = datetime(*map(int, curr_date.split("-")))

        if (curr_dt - codes_dt).days > 30:
            getCodesInCSVsForAllDatasets(quandl_apikey)
        break
    else:
        getCodesInCSVsForAllDatasets(quandl_apikey)

    qcodes_cursor = qcodes_colln.find()
    for qcur in qcodes_cursor:

        try:
            base_url = qcur['base_url']
            data_URL = base_url + "?api_key={0}"
            dataset_code = qcur['dataset_code']
            dataset_descrpn = qcur['description']

            #logging.info("Dataset code :: " + dataset_code)

            src_colln_name = dataset_code.lower().split("/")[0]
            meta_obj_name = src_colln_name + "." + dataset_code.split("/")[1]

            # Check if Collection already exists in MongoDB.
            meta_mongo_colln = initialize_mongo(meta_col_name)
            metadata_cursor = meta_mongo_colln.find_one(
                     {meta_obj_name: {'$exists': 1}})

            logging.info(meta_obj_name)
            logging.info(metadata_cursor)

            src_colln = initialize_mongo(src_colln_name)

            # For every request, wait period is needed to avoid
            # Quandl server restrictions for free account.
            time.sleep(3)
            resp_data = ''
            mongo_id = ''
            data_mode = ''
            prev_count = 0

            if not metadata_cursor:
                """For first time downloading data to Mongo."""

                resp = os.popen("curl " + data_URL.format(quandl_apikey))
                resp_data = resp.read()
                data_mode = "initial"

            else:
                """If historical data is already downloaded to
                MongoDB."""

                # Find the latest available data based on 'Date'
                src_colln_cursor = src_colln.find()

                dates = []
                for cur in src_colln_cursor:
                    mongo_id = cur['_id']
                    prev_count = src_colln_cursor.count()

                    if "Date" in cur:
                        dates.append(cur["Date"])
                    elif "DATE" in cur:
                        dates.append(cur["DATE"])
                    elif "Trade Date" in cur:
                        dates.append(cur["Trade Date"])
                    elif "Month" in cur:
                        dates.append(cur["Month"])
                    elif "Year" in cur:
                        dates.append(cur["Year"])
                    elif "End of month" in cur:
                        dates.append(cur["End of month"])

                if dates:
                    """Fetch the last downloaded data and download the
                    remaining latest data."""

                    # Use the next day as part of the query to get the
                    # data available after the last fetch.
                    next_date = datetime(*map(int, max(dates).split('-')))\
                                + timedelta(days=1)
                    next_date = next_date.strftime('%Y-%m-%d')

                    # Get the data using query and its parameters.
                    resp = req.request("GET", base_url,
                                       params={"api_key": quandl_apikey,
                                               "start_date": next_date})
                    resp_data = resp.text
                    data_mode = "update"

                else:
                    """In the absence of Date fields in existing
                    historical data."""

                    resp = os.popen("curl " + data_URL.format(quandl_apikey))
                    resp_data = resp.read()
                    data_mode = "no_date"

            # Persisting functionality to Mongo.
            saveQuandlData(resp_data, src_colln_name, dataset_descrpn,
                           metadata_cursor, src_colln, dataset_code,
                           mongo_id, data_mode, prev_count)
        except:
            raise
            continue

    logging.info("Total time taken to fetch data from Quandl : " +
                 str(round(float((time.time() - t1)/60), 1)) + " minutes")


if __name__ == '__main__':
    main()
