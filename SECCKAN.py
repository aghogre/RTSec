# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 13:03:13 2017

@author: RAVITHEJA
"""

import logging
import json
import urllib2
import ckanapi
import re
from datetime import datetime
from config import mongo_config
from mongoDBConnection import initialize_mongo


class SEC_CKAN():

    def __init__(self, ckan_host, api_key, azure_container, publisher,
                 owner_org):
        # initializing class variables
        self.ckan_host = ckan_host
        self.api_key = api_key
        self.azure_container = azure_container
        self.publisher = publisher
        self.owner_org = owner_org  # "securities-exchange-commission"

        logging.basicConfig(format='%(asctime)s %(levelname)s \
                            %(module)s.%(funcName)s %(message)s',
                            level=logging.INFO)

        # Establishing connection with CKAN
        self.ckan_ckan = ckanapi.RemoteCKAN(ckan_host, apikey=api_key)
        
        dict_additional_fields = {
                'Sourcing Date': datetime.now().strftime("%B %d, %Y, %H:%M"),
                'Datastore': mongo_config.get('mongo_uri'),
                'Database Name': mongo_config.get('db_name'),
                'Collection': mongo_config.get('col_name'),
                }
        additional_fields = []
        for k, v in dict_additional_fields.items():
            additional_fields.append({'key': k, 'value': v})

        # attempting to create a new package
        try:
            logging.info("Creating CKAN for SEC data")
            self.ckan_ckan.action.package_create(name="sec_data1",
                                                 title="SEC Data",
                                                 owner_org=self.owner_org,
                                                 notes="SEC 10-K filings",
                                                 maintainer=self.publisher,
                                                 tags=[{'name': "SEC"},
                                                       {'name': "10K"}],
                                                 extras=additional_fields,
                                                 )
            logging.info("Created CKAN for SEC data")
        except:
            self.ckan_ckan.action.package_update(id="sec_data1",
                                                 title="SEC Data",
                                                 owner_org=self.owner_org,
                                                 notes="SEC 10-K filings",
                                                 maintainer=self.publisher,
                                                 tags=[{'name': "SEC"},
                                                       {'name': "10K"}],
                                                 extras=additional_fields,
                                                 )
        
        # Establishing Mongo collection
        self.mongo_colln = initialize_mongo()


    # To save the metadata of CIKs downloaded into Azure.
    def storeMetadata(self, cik, azure_urls, file_types, year,
                      license_azure_url):
        
        # read all metadata information from 'metadata.json'
        with open('ticker_metadata.json') as json_file:
            json_data = json_file.read()
            metadata_json = json.loads(json_data)

        # fetch the metadata info for the cik, from json
        metadata = [mdata for mdata in metadata_json["metadata"]
                    if mdata["cik"] == str(cik)]

        # flag the availability of ticker info
        tickerInfo = False
        if len(metadata) != 0:
            tickerInfo = True
            metadata = metadata[0]

        current_date = datetime.now().strftime("%B %d, %Y, %H:%M")
        tags = []
        package_title = ''
        description = ''

        # create or update the package for each artifact with latest Metadata
        # of Azure datasets.
        if tickerInfo:
            package_title = metadata["Title"].replace('.', '')
            if "Tags" in metadata:
                for tag in metadata["Tags"].split(','):
                    if str(tag).strip():
                        tags.append({'name': str(tag).strip()})
            tags.append({'name': str(year)})

            # additional fields to be added in CKAN dataset
            dict_additional_fields = {
                'Company name': metadata["Name"],
                'Title': package_title,
                'Sourcing Date': current_date,
                'SourceType': file_types,
                'Source': metadata["Source"],
                'Container': metadata["Container"],
                'License': license_azure_url,
                'Ticker': metadata["Ticker"],
                'Exchange': metadata["Exchange"],
                'Industry': metadata["Industry"],
                'cik': metadata["cik"],
                'IRS Number': metadata["IRS Number"],
                'Business': metadata["Business"],
                'Incorporated': metadata["Incorporated"],
            }
            description = metadata["Description"]
        else:
            package_title = "SEC Data"
            description = "SEC 10-K filings for " + package_title
            tags.append({'name': str(year)})
            tags.append({'name': str(cik)})

            # additional fields to be added in CKAN dataset
            dict_additional_fields = {
                'Title': package_title,
                'Sourcing Date': current_date,
                'SourceType': file_types,
                'Source': "SEC",
                'Container': self.azure_container,
                'License': license_azure_url,
                'cik': cik
            }


        prev_years = ''
        prev_json = {}
        prev_urls = {}
        toUpdate = False
        
        metadata_cursor = self.mongo_colln.find({})
        for i in metadata_cursor:
            if cik in i:
                toUpdate = True
                prev_json = json.loads(i[cik])
                
                if "Years" in prev_json:
                    prev_years = prev_json["Years"]
                    
                for key in prev_json.keys():
                    if key.startswith('url'):
                        print key, prev_json[key]
                        prev_urls[key] = prev_json[key]
                        

        # iterate the URLs of files stored in Azure to organize a dict of URLs.
        multi_url_dict = prev_urls  # {}

        for i, url in enumerate(azure_urls):
            multi_url_dict['url' + str(i + 1 + len(prev_urls))] = url

        # appending URLs to the additional fields
        dict_additional_fields.update(multi_url_dict)

        # adding extra properties to CKAN dataset using Wrapper 'extras'
        additional_fields = []
        for k, v in dict_additional_fields.items():
            additional_fields.append({'key': k, 'value': v})

        data = {}
        data['cik'] = cik
        data['title'] = package_title
        data['owner'] = self.owner_org
        data['notes'] = description
        data['maintainer'] =  self.publisher
        data['Years'] = str(year) + ',' + prev_years
        
        mongodict = dict(data.items() + dict_additional_fields.items())

        if toUpdate:
            logging.info("*** MONGO UPDATE ****")
            self.mongo_colln.update({cik : prev_json},
                                    {cik : json.dumps(mongodict)},
                                    upsert=True)
        else:
            logging.info("*** MONGO INSERT ****")
            self.mongo_colln.insert_one({cik : json.dumps(mongodict)})

