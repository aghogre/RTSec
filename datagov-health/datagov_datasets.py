# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:50:27 2018

@author: RAVITHEJA
"""

import requests
import json
import urllib2
import os.path
import pandas as pd
import csv
from config import argument_config, mongo_config
from MongodbConnector import mongodbConnector


try:
    mongo = mongodbConnector()
except:
    raise


def fetchGovData(domain, dataset_count, datasets_colln):

    url = "http://catalog.data.gov/api/3/action/package_list?" + \
          "q=" + domain + "&rows=" + str(dataset_count)
    r = requests.get(url)
    
    with open(domain + "100.json", 'w') as d_file_w:
        json.dump(r.json(), d_file_w)
        
    json_resp = r.json()
    results = json_resp["result"]["results"]
    
    datasets_count = datasets_colln.count()

    if datasets_count > 0:
        mongo.bulk_mongo_update(datasets_colln, results)
    else:
        mongo.bulk_mongo_insert(datasets_colln, results)


def extractFromJSON(domain, datasets_colln):
    """with open(domain + ".json", 'r') as dfile_r:
        d_data = json.load(dfile_r)
        datalist = []
        for d in d_data['result']['results']:
            data = {}"""
    
    datasets_cursor = datasets_colln.find()
    for dataset in datasets_cursor:
        dataset_name = dataset["name"]
        data_colln = mongo.initialize_mongo(dataset_name)
        
        if data_colln.count() > 0:
            print dataset_name + " is skipped, as it has " + str(data_colln.count()) + " records."
            continue
            
        data_documents = []
        
        for res in dataset["resources"]:
            res_format = res["format"]
            res_url = res["url"]
            
            file_name = (dataset_name + "_" + (res["name"]).replace(" ", "")
                        + "." + res_format).lower()
            #print file_name
            
            try:
                if not os.path.isfile(file_name):
                    print "DOWNLOADING..."
                    resp = urllib2.urlopen(res_url)
                    resp_content = resp.read()
                    
                    with open(file_name, 'wb') as res_file:
                        res_file.write(resp_content)
        
                if res_format == "JSON" or res_format == "json":
                    try:
                        with open(file_name, "r") as res_file_r:
                            data_documents.append(json.load(res_file_r))
                            print res_format + " :: " + file_name + " :: " \
                                  + dataset_name + " :: " + str(len(data_documents))
                            mongo.bulk_mongo_insert(data_colln, data_documents)
                            
                    except:
                        raise

                elif res_format == "CSV" or res_format == "csv":
                    
                    file = open(file_name, 'rU')
                    reader = csv.DictReader(file, dialect=csv.excel) 
                    for row in reader:
                        data_documents.append(row)
                    try:
                        mongo.bulk_mongo_insert(data_colln, data_documents)
                        print res_format + " :: " + file_name + " :: " \
                                    + str(len(data_documents)) 
                    except:
                        raise
                    
                    """
                    converted_file_name = file_name.replace(".csv", "_converted.json")
                    if not os.path.isfile(converted_file_name):
                        csv_file = pd.DataFrame(pd.read_csv(file_name,
                                                            sep = ",",
                                                            header = 0,
                                                            index_col = False))
                        csv_file.to_json(converted_file_name,
                                         orient = "records",
                                         date_format = "epoch",
                                         double_precision = 10,
                                         force_ascii = True,
                                         date_unit = "ms",
                                         default_handler = None)
                    try:
                        with open(converted_file_name, 'r') as res_file_r:
                            mongo.bulk_mongo_insert(data_colln, json.load(res_file_r))
                    except:
                        continue"""
                        
            except:
                continue

        """if data_documents:
            print str(len(data_documents)) + " documents inserting into " + dataset_name
            mongo.bulk_mongo_insert(data_colln, data_documents)"""


def main():

    domains = argument_config.get('domains')
    datasets_colln_name = mongo_config.get('datasets_colln_name')
    
    domains = ["health"]
    datasets_colln = mongo.initialize_mongo(datasets_colln_name)
        
    for d in domains:
        #fetchGovData(d, 100, datasets_colln)

        extractFromJSON(d, datasets_colln)


if __name__ == "__main__":
    main()
