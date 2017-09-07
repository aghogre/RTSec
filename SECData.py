# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:41:53 2017

@author: RAVITHEJA
"""

import os
import time
import urllib2
import json
from azure.storage.blob import AppendBlobService, BlockBlobService
from SECCrawl import SECCrawler
from SECAzure import SEC_Azure
from SECCKAN import SEC_CKAN
from config import argument_config


def main():
    # collecting the input arguments
    azure_account_name = argument_config.get('azure_account_name')
    azure_account_key = argument_config.get('azure_account_key')
    azure_container = argument_config.get('azure_container')
    ckan_host = argument_config.get('ckan_host')
    ckan_api_key = argument_config.get('ckan_key')
    years = argument_config.get('years')
    
    years = map(str, years)
    if len(years)==1:
        years = map(str.strip, years[0].split(','))
    print(years)
    
    t1 = time.time()
    
    # Crawling the www.sec.gov to fetch the CIKs filed 10-K filings with SEC in the givens years.
    secCrawler = SECCrawler()    
    cik_lists = []
    
    for year in years:
        print(year)
        if int(year) not in range(1993, 2017): 
            print("discarding " + year)
            years.remove(year)
        cik_list = secCrawler.get10kdata(year)
        cik_lists.append(cik_list)
    
    if '2017' in years or os.path.exists("metadata.json") == False:
        makeMetadataJson(azure_container)
        
    # Storing the 10-K complete data for each CIK in Azure.
    secAzure = SEC_Azure(azure_account_name, azure_account_key, azure_container)
    secCKAN = SEC_CKAN(ckan_host, ckan_api_key)
    
    for count in range(0, len(years)):
        store10kdata(years[count], cik_lists[count], secAzure, secCKAN, azure_account_name, azure_account_key, azure_container)
        
    print("10-K Data Downloaded into Azure & its metadata is available in CKAN.")
    print("Total time taken :: " + str(time.time() - t1))    
    
    
def makeMetadataJson(azure_container):
    metadata = {}
    metadata['metadata'] = []
    print("Creating metadata for cik with ticker industry data.")
    i=0
    while i>=0:
        request = urllib2.Request('http://rankandfiled.com/data/identifiers?start='+str(i))
        response = urllib2.urlopen(request)
        resp_json = json.loads(response.read())
        
        for ticker in resp_json['list']:
            cik_data = ticker.split('|')
                        
            metadata["metadata"].append({
                "Title" : "SEC "+ cik_data[3] + " " + cik_data[4],
                "Description" : "SEC 10-K filings for '"+cik_data[4]+"'",
                "Publisher" : "RandomTrees",
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
        print(i)                       
        if len(resp_json['list']) < 100:
            break
        i += 100
            
    with open("metadata.json", "w") as ticker_file:
        json.dump(metadata, ticker_file)
 #       ticker_file.write(str(metadata))
    ticker_file.close()
        
     
def store10kdata(year, cik_list, secAzure, secCKAN, azure_account_name, azure_account_key, azure_container):
    try:
        filename = "uploaded_data_"+year+".txt"
        append_blob_service = AppendBlobService(account_name=azure_account_name, account_key=azure_account_key)
        block_blob_service = BlockBlobService(account_name = azure_account_name, account_key = azure_account_key)
        uploaded_ciks = ''
        uploaded_ciks_list = []
        
        generator = block_blob_service.list_blobs(azure_container)
        
        for blob in generator:
            
            if (blob.name == filename):
                
                uploaded_ciks = append_blob_service.get_blob_to_text(azure_container, filename)
               
                for cik_list_copy in uploaded_ciks:
                    uploaded_ciks_list.add(cik_list_copy)
                append_blob_service.append_blob_from_text(azure_container, filename, uploaded_ciks + '\n')
                
                print("Among "+ str(len(cik_list)) + " files, " 
                + str(len(uploaded_ciks_list)) + " are ignored.")
                
                for cik in cik_list[len(uploaded_ciks_list):] :
                    print("Download started for cik -> " + str(cik[0]))
                    
                    azure_url, file_types = secAzure.createDocumentList(cik[0], year)
                    
                    secCKAN.storeMetadata(cik[0], azure_url, file_types, year)
                                    
                    append_blob_service.append_blob_from_text(azure_container, filename, cik[0] + '\n')
        
                    print("Download completed for cik -> " + str(cik[0]))
                
            else:
                append_blob_service.create_blob(azure_container, filename)
                
                print("Among "+ str(len(cik_list)) + " files, " 
                + str(len(uploaded_ciks_list)) + " are ignored.")
                
                for cik in cik_list[len(uploaded_ciks_list):] :
                    print("Download started for cik -> " + str(cik[0]))
                    
                    azure_url, file_types = secAzure.createDocumentList(cik[0], year)
                    
                    secCKAN.storeMetadata(cik[0], azure_url, file_types, year)
                                    
                    append_blob_service.append_blob_from_text(azure_container, filename, cik[0] + '\n')
        
                    print("Download completed for cik -> " + str(cik[0]))
                
            
    
            
        
        
    except:
        print ("No input file Found")
        raise
    
    
if __name__ == '__main__':
    main()


