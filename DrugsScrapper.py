# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 17:34:56 2017

@author: ANSHUL
"""

import requests
from bs4 import BeautifulSoup
from mongoDBConnection import update_mongo_collection, initialize_mongo, mongo_metadata
from config import mongo_config
import logging
from DrugsCKAN import insert_into_ckan
from datetime import datetime


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                     %(module)s.%(funcName)s :: %(message)s',
                     level=logging.INFO)

    mongo_colln = initialize_mongo(mongo_config.get('col_name'))
    description = "Drugs.com is the most popular, comprehensive and up-to-date source of drug information online. Providing free, peer-reviewed, accurate and independent data on more than 24,000 prescription drugs, over-the-counter medicines & natural products."
    insert_into_ckan(mongo_config.get('mongo_uri'), description)
    original_url = ''
    resp = requests.get('https://www.drugs.com/drug_information.html')
    soup = BeautifulSoup(resp.content, "html.parser")
    listOfLinks = soup.find_all("div",
                                {"class": "boxList boxListAZDrugs noprint"})

    for url in listOfLinks:
        alphaURL = url.find_all('a', href=True)
    for r in alphaURL:
        original_url = 'https://www.drugs.com'+r['href']
        logging.info("Fetching medicines name starting" +
                     "with letter- '"+r['href'].split('.')[-2][1]+"'")
        alphabet_urls(original_url, mongo_colln)
        response = requests.get(original_url)
        soup = BeautifulSoup(response.content, "html.parser")
        pagingLinks = soup.find_all("td", {"class": "paging-list-index"})
        for purl in pagingLinks:
            pageURL = purl.find_all('a',  href=True, title=True)

            for b in pageURL:
                original_page_url = 'https://www.drugs.com'+b['href']
                alphabet_urls(original_page_url, mongo_colln)
        logging.info("Completeted fetching medicines name" +
                     "starting with letter- '"+r['href'].split('.')[-2][1]+"'")


def alphabet_urls(original_page_url, mongo_colln):
    response = requests.get(original_page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    medicinesLink = soup.find_all("ul", {"class": "doc-type-list"})
    for murl in medicinesLink:
        medURL = murl.find_all('a', href=True)
        for a in medURL:
            medicine_name = a.getText()
            original_med_url = 'https://www.drugs.com'+a['href']
            typeOfmed = original_med_url.split('/')[-2]
            if typeOfmed == 'mtm':
                medicine_name = medicine_name+'-concise'
            elif typeOfmed == 'cdi':
                medicine_name = medicine_name+'-med fact'
            elif typeOfmed == 'cons':
                medicine_name = medicine_name+'-advance'
            elif typeOfmed == 'pro':
                medicine_name = medicine_name+'-professional'
            else:
                medicine_name = medicine_name
            try:
                if mongo_colln.find({'_id': medicine_name}).count() > 0:
                    logging.info("Skipping, Already present" +
                                 "in mongo: "+medicine_name)
                    continue
                else:
                    drug_page(original_med_url, medicine_name, mongo_colln)
            except:
                pass


def drug_page(original_med_url, medicine_name, mongo_colln):
    feedObject = {}
    status = {}
    flag = False
    med_response = requests.get(original_med_url)
    soup = BeautifulSoup(med_response.content, "html.parser")
    medicineDetails = soup.find_all("ul",
                                    {"class": ["visible-links",
                                               "hidden-links invisible"]})
    for links in medicineDetails:
        med_link = links.find_all('a', href=True)
        for u in med_link:
            if flag is False:
                med_tabs_name = 'Overview'
                original_medlink = original_med_url
                flag = True
            else:
                med_tabs_name = u.getText()
                if med_tabs_name != 'Overview':
                    original_medlink = 'https://www.drugs.com'+u['href']
                else:
                    pass
            content_response = requests.get(original_medlink)
            soup = BeautifulSoup(content_response.content, "html.parser")
            content = soup.find("div", {"class": "contentBox"})
            for script in soup(["script", "style"]):
                script.extract()
            feedObject[med_tabs_name] = content.getText().replace('\n', ' ').replace('\t', ' ').replace('\u', ' ')
    current_time = datetime.today().strftime('%Y-%d-%m %H:%M:%S')
    feedObject['Created_Time'] = current_time
    logging.info("Inserting into Mongo: "+medicine_name)
    # Upserting into Mongo DB
    update_mongo_collection(mongo_colln, medicine_name, feedObject)
    # Inserting medicine name to metadata
    status["status"] = 'success'
    mongo_metadata(medicine_name, status)

if __name__ == "__main__":
    main()
