# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:24:51 2018

@author: ANSHUL
"""


import requests
from bs4 import BeautifulSoup
from MongodbConnector import mongodbConnector
from config import mongo_config
import logging
from datetime import datetime
from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen
import csv
import os



def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                     %(module)s.%(funcName)s :: %(message)s',
                     level=logging.INFO)
    
       #description = "Drugs.com is the most popular, comprehensive and up-to-date source of drug information online. Providing free, peer-reviewed, accurate and independent data on more than 24,000 prescription drugs, over-the-counter medicines & natural products."
    # inserting metadata details into CKAN
    #insert_into_ckan(mongo_config.get('mongo_uri'), description)
    original_url = ''
    resp = requests.get('https://www.crowdflower.com/data-for-everyone/')
    soup = BeautifulSoup(resp.content, "html.parser")
    # fetching all the alphabet wise urls of drugs
    listOfLinks = soup.find_all("div",
                                {"class": "item"})

    for url in listOfLinks:
        alphaURL = url.find_all('a', {"class": "download"}, href=True)
        names = url.find_all('h3')
        
        for r in alphaURL:
            for n in names:
                original_url = r['href']
                name = n.text
                if name  and original_url:
                    print original_url
                    print name
                    filename = name.split(".")[0].replace("(", "").replace(")", "").replace("-", "").replace(":", "").replace(" ", "").replace("/", "").replace("'", "").replace("?", "").replace('"', "").replace(",", "").replace("`", "")
                   
                    if original_url.split(".")[-1] == 'csv':
                        response = requests.get(original_url)
                        data = response.text
                        with open(filename+'.csv', 'w') as f:
                            f.write(data.encode("utf-8").strip())
                           
                    elif original_url.split(".")[-1] == 'zip':
                        url = urlopen(original_url)
                        zipfile = ZipFile(StringIO(url.read()))
                        files = zipfile.namelist()
                        fopen = open(filename+'.csv', 'w')
                        for f in files:
                            for line in zipfile.open(f).readlines():
                                fopen.writelines(line)
                        fopen.close()
                    csv_to_dict(filename)
                
def csv_to_dict(filename):
    mongo = mongodbConnector()
    mongo_colln = mongo.initialize_mongo(filename)
    try:
        file = open(filename+'.csv', 'rU')
        reader = csv.DictReader(file, dialect=csv.excel) 
        i=0
        for row in reader:
            for k in row.keys():
                try:
                    if len(row[k])<1:
                        del row[k]
                except: 
                    pass
    
            mongo.insert_into_mongo(mongo_colln, row)
            
            i+=1
            if i == 10:
                logging.info ("loaded to mongo   - " +filename)
                #os.remove(filename+'.csv')
                break
    except:
            raise

           
                

if __name__ == "__main__":
    main()

