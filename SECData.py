# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:41:53 2017

@author: RAVITHEJA
"""

import os
import time
import urllib2
import json
from datetime import datetime
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
        store10kdata(years[count], cik_lists[count], secAzure, secCKAN)
        
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
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for ticker in resp_json['list']:
            cik_data = ticker.split('|')
                        
            metadata["metadata"].append({
                "Title" : "SEC "+ cik_data[3] + " " + cik_data[4],
                "Description" : "SEC 10-K filings for '"+cik_data[4]+"'",
                "Publisher" : "RandomTrees",
                "Source" : "SEC",
                "Created" : current_date,
                "Last Updated" : current_date,
                "Sourcing_Date" : current_date,
                #"version" : year,
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
        
     
def store10kdata(year, cik_list, secAzure, secCKAN):
    try:
        filename = "uploaded_data_"+year+".txt"
        
        uploaded_ciks = ''
        uploaded_ciks_list = []
        if os.path.exists(filename):
            fr1 = open(filename, 'r')
            uploaded_ciks = fr1.read()
            fr1.close()
            
            fr2 = open(filename, 'r')
            uploaded_ciks_list = map(str.strip, fr2)
            fr2.close()
            
        with open(filename, 'w+') as fw:
            fw.write(uploaded_ciks)
            print("Among "+ str(len(cik_list)) + " files, " 
                  + str(len(uploaded_ciks_list)) + " are ignored.")
            
            for cik in cik_list[len(uploaded_ciks_list):] :
                print("downloading cik -> " + str(cik[0]))
                url = secAzure.createDocumentList(cik[0], year)
                fw.write(cik[0] + '\n')
                
                secCKAN.storeMetadata(cik[0], url, year)
        fw.close()
    except:
        raise
        print ("No input file Found")
    
    
if __name__ == '__main__':
    main()


