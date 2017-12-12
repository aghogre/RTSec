# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 12:23:37 2017

@author: RAVITHEJA
"""

import os
import logging
import requests
import zipfile
import urllib2
from config import mongo_config
from mongoDBConnection import initialize_mongo, insert_into_mongo
from os import walk
from datetime import datetime


DEFAULT_DATA_PATH = os.path.abspath(os.path.join(
    os.path.dirname('__file__'), '', 'Quandl'))


def getCodesInCSVsForAllDatasets(quandl_apikey):
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                    %(module)s.%(funcName)s :: %(message)s',
                    level=logging.INFO)

    q_db_base_url = "https://www.quandl.com/api/v3/databases"
    q_databases_url = q_db_base_url + "?api_key={0}&page={1}"
    q_codes_url = q_db_base_url + "/{0}/codes.json?api_key={1}"

    page = 0
    database_codes = []
    premium_codes = []
    total_codes = 0
    json_data = {}

    try:
        while len(database_codes) == 0 \
                or json_data['meta']['total_count'] > total_codes:
            page += 1
            q_db_URL = q_databases_url.format(quandl_apikey, str(page))

            json_data = (requests.get(q_db_URL)).json()

            for d in json_data['databases']:
                if not d['premium']:
                    database_codes.append(d['database_code'])
                if d['premium']:
                    premium_codes.append(d['database_code'])

            total_codes = len(database_codes) + len(premium_codes)

        for code in database_codes[:4]:
            zip_filename = code + '-datasets-codes.zip'

            resp = urllib2.urlopen(q_codes_url.format(code, quandl_apikey))
            zipcontent = resp.read()

            with open(zip_filename, 'wb') as zfw:
                zfw.write(zipcontent)

            with zipfile.ZipFile(zip_filename, "r") as zfr:
                zfr.extractall(DEFAULT_DATA_PATH)

            saveCodesInMongo()
            os.remove(zip_filename)
    except:
        pass


def saveCodesInMongo():

    quandl_codes_colln_name = mongo_config.get('quandl_codes_colln_name')

    q_data_base_URL = "https://www.quandl.com/api/v3/datasets/{0}"

    filenamesList = []
    for (dirpath, dirnames, filenames) in walk(DEFAULT_DATA_PATH):
        filenamesList.extend(filenames)

    qcodes_colln = initialize_mongo(quandl_codes_colln_name)
    for fn in filenamesList:
        logging.info(fn + " extracted.")
        codesFile = os.path.abspath(os.path.join(DEFAULT_DATA_PATH, fn))
        with open(codesFile, 'r') as csv_file:
            csvlines = csv_file.readlines()

            for num, line in enumerate(csvlines):
                codeline = line.split(',')
                dataset_code = codeline[0]
                dataset_descrpn = codeline[1]
                created_time = datetime.now().strftime("%Y-%m-%d")

                code_doc = {"dataset": fn,
                            "dataset_code": dataset_code,
                            "description": dataset_descrpn,
                            "base_url": q_data_base_URL.format(dataset_code),
                            "created_time":	created_time
                            }

                insert_into_mongo(qcodes_colln, code_doc, dataset_code)
        os.remove(codesFile)
