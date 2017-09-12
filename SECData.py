# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:41:53 2017

@author: RAVITHEJA
"""

import logging
import os
import time
import urllib2
import json
import requests
from config import argument_config
from datetime import datetime
from os import path
from SECCrawl import SECCrawler
from SECAzure import SEC_Azure
from SECCKAN import SEC_CKAN
from azure.storage.blob import AppendBlobService, BlockBlobService


def main():
    # To make note of how much time consumed for execution
    t1 = time.time()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s.%(funcName)s %(message)s', level=logging.INFO)

    # collecting the input arguments
    azure_account_name = argument_config.get('azure_account_name')
    azure_account_key = argument_config.get('azure_account_key')
    azure_container = argument_config.get('azure_container')
    ckan_host = argument_config.get('ckan_host')
    ckan_api_key = argument_config.get('ckan_key')
    years = argument_config.get('years')
    publisher  = argument_config.get('publisher')

    # extract current year to set the range for SEC crawling
    current_year = datetime.now().strftime("%Y")
    
    # eliminating the Year, if out of range
    for year in years.split(","):
        if int(year) not in range(1993, int(current_year)+1): 
            logging.info("discarding " + str(year))
            years.remove(year)
    
    # Crawling the www.sec.gov to fetch the CIKs filed 10-K for the given years.
    secCrawler = SECCrawler()        
    cik_lists = []
    for year in years.split(","):
        cik_list = secCrawler.get10kdata(str(year))
        cik_lists.append(cik_list.values.tolist()) 

    # Storing the 10-K complete data for each CIK in Azure and metadata in CKAN.
    secAzure = SEC_Azure(azure_account_name, azure_account_key, azure_container)
    
    # fetch the Ticker data for the first time.
    # repeat the exercise if given years has current year or file not available
    if str(current_year) in years or os.path.exists("ticker_metadata.json") == False:
        makeMetadataJson(azure_container, publisher, azure_account_name, azure_account_key)
        
    secCKAN = SEC_CKAN(ckan_host, ckan_api_key, azure_container, publisher)
    for count in range(0, len(years)):
        count = store10kdata(str(years[count]), cik_lists[count], secAzure, secCKAN, 
                     azure_account_name, azure_account_key, azure_container)
    
    # A confirmation message for extraction and storage of SEC 10-K filings 
    if count > 0:
        logging.info("10-K Data for given years is downloaded into Azure & its metadata is available in CKAN.")
    
    logging.info("Total time taken :: " + str(time.time() - t1))    
    
    
# Function to create metadata in json format by extracting ticker data 
# from http://rankandfiled.com/#/data/tickers
def makeMetadataJson(azure_container, publisher, azure_account_name, azure_account_key):
    metadata = {}
    metadata['metadata'] = []
    logging.info("Creating metadata for ciks with ticker industry data.")
    i = 0
    # feed fetch every 100 ticker details every iteration.
    while i >= 0:
        # building request to rankandfiled.com 
        request = urllib2.Request('http://rankandfiled.com/data/identifiers?start='+str(i))
        response = urllib2.urlopen(request)
        resp_json = json.loads(response.read())
        
        for ticker in resp_json['list']:
            cik_data = ticker.split('|')
                        
            metadata["metadata"].append({
                "Title" : "SEC "+ cik_data[3] + " " + cik_data[4],
                "Description" : "SEC 10-K filings for '"+cik_data[4]+"'",
                "Publisher" : publisher,
                "Source" : "SEC",
                "Container" : azure_container,
                "Ticker" : cik_data[0],
                "Exchange" : cik_data[1],
                "Industry" : cik_data[2],
                "cik" : cik_data[3],
                "Name" : cik_data[4],
                "IRS Number" : cik_data[5],
                "Business" : cik_data[6],
                "Incorporated" : cik_data[7],
                "Tags" : "SEC, "+cik_data[3]+","+cik_data[4]+","+cik_data[2]
            }) 
        if len(resp_json['list']) < 100:
            break
        i += 100
    
    # writing the json formatted ticker metadata into a file for later use.
    block_blob_service = BlockBlobService(account_name=azure_account_name, 		
                                          account_key=azure_account_key)		
    
    with open("ticker_metadata.json", "w") as ticker_file:
        json.dump(metadata, ticker_file)

    block_blob_service.create_blob_from_path(azure_container, 'ticker_metadata.json', 'ticker_metadata.json')		
 
        
# Delegates the core functionality to store the obtained SEC 10-k filings
# in Azure and its metadata in CKAN 
def store10kdata(year, cik_list, secAzure, secCKAN, 
                 azure_account_name, azure_account_key, azure_container):        
    try:
        count=0
        uploaded_ciks_list = []

        # make a file to maintain a list of uploaded ciks list of data.
        filename = "uploaded_data_"+year+".txt"
        
        append_blob_service = AppendBlobService(account_name=azure_account_name, 
                                                account_key=azure_account_key)
        block_blob_service = BlockBlobService(account_name = azure_account_name, 
                                              account_key = azure_account_key)
        
        # get the list of blobs (files and folders from the container),
        # to identify the file with partially or fully uploaded list of files 
        generator = block_blob_service.list_blobs(azure_container) 
        
        licensefile = 'xbrlviewerlicense.htm'
        flag = 0
        
        # Creating License File in AZURE.
        for blob in generator:
            if blob.name != licensefile:
                flag += 1   
            else:
                flag = 0
                break
        
        if flag != 0:
            license_url = "https://www.sec.gov/spotlight/xbrl/xbrlviewerlicense.htm"
            license_file =  license_url.split("/")[-1]
            f = requests.get(license_url)
            block_blob_service.create_blob_from_text(
                            path.join(azure_container, 'License'), 
                            license_file, f.text)
        
        license_azure_url = block_blob_service.make_blob_url(azure_container, 
                                                path.join('License', licensefile))
        
        #Creating upload files for each year in AZURE
        for blob in generator:
            if blob.name == filename:
                block_blob_service.get_blob_to_path(azure_container, filename, filename)

                # make a copy of uploaded list file               
                with open(filename, 'r') as fr2:
                    uploaded_ciks_list = map(str.strip, fr2)
                os.remove(filename)
                
                # flag the availability of file
                count += 1
                break
            
        # create the file in azure to maintain the uploaded ciks list, iff not present
        if count == 0 :   
            append_blob_service.create_blob(azure_container, filename)
        
        # shows the difference of already uploaded and yet to be uploaded ciks count
        logging.info("Among "+ str(len(cik_list)) + " files, " + str(len(uploaded_ciks_list)) + " are ignored.")
            
        if not os.path.exists("ticker_metadata.json"):
            block_blob_service.get_blob_to_path(azure_container, 'ticker_metadata.json', 'ticker_metadata.json')
        
        # fetch the remaining ciks 
        for cik in cik_list[len(uploaded_ciks_list):] :
            logging.info("Download started for cik -> " + str(cik[0]))
            
            # extract and store the 10-K cik data into Azure
            azure_url, file_types = secAzure.createDocumentList(cik[0], year)
            file_types = ",".join(list(file_types))
            
            # save the metadata for ciks saved in Azure, in CKAN
            secCKAN.storeMetadata(cik[0], azure_url, file_types, year, license_azure_url)

            # update the file with extrated cik in the list
            append_blob_service.append_blob_from_text(azure_container, filename, cik[0]+'\n')

            logging.info("Download completed for cik -> " + str(cik[0]))

        os.remove('ticker_metadata.json')
        count += 1
    except:
        logging.warn("No input file Found")
        raise
    return count

    
if __name__ == '__main__':
    main()



