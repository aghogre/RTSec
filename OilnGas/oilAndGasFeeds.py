# -*- coding: utf-8 -*-
"""
Created on Wed May 02 12:03:25 2018

@author: ADMIN
"""
import feedparser
import hashlib
import json
import logging
import datetime
from mongoDBconnection import mongodbConnector

try:
    mongo = mongodbConnector()
except:
    raise

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s \
                     %(module)s.%(funcName)s :: %(message)s',
                     level=logging.INFO)
    feeds = [
            'https://tradingeconomics.com/russia/rss',
            'https://tradingeconomics.com/venezuela/rss',
            'https://tradingeconomics.com/iran/rss',
            'https://tradingeconomics.com/iraq/rss',
            'https://tradingeconomics.com/nigeria/rss',
            'https://tradingeconomics.com/angola/rss',
            'https://tradingeconomics.com/saudi-arabia/rss',
            'https://tradingeconomics.com/united-arab-emirates/rss',
            'https://tradingeconomics.com/united-states/rss',
            'https://tradingeconomics.com/india/rss',
            'https://tradingeconomics.com/china/rss'
            ]
    try:
        for i in feeds:
            response = feedparser.parse(i)
            feed_object = {}
            
        
            for e in response['entries']:
                feed_object["title"] = e['title']
                d = str(datetime.datetime.strptime(e['published'], '%a, %d %b %Y %H:%M:%S GMT').date())
                feed_object["publishedDate"] = d 
                feed_object["description"] = e['description']
                checksum = hashlib.md5(json.dumps(feed_object, sort_keys=True)).hexdigest()
                mongo_colln_name = '_'+d
                mongo_colln = mongo.initialize_mongo(mongo_colln_name)
                doc_count = mongo_colln.count()
                if doc_count>0:
                    cursor = mongo_colln.find()
                    for c in cursor:
                            title = c['title']
                            description = c['description']
                            mongo_colln.find_and_modify(query={'publishedDate':d}, update={"$set": {'title': title+","+e['title'], 'description': description+","+e['description']}}, upsert=False, full_response= True)
                            logging.info("Appended new data to mongo collection-"+mongo_colln_name)
                else:
                    mongo.update_collection(mongo_colln, checksum, feed_object)
                    logging.info("Upserted to mongo collection-"+mongo_colln_name)

    except:
        logging.error("Error")
        raise

if __name__ == "__main__":
    main()       