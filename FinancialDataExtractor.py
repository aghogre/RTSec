# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 09:38:57 2017

@author: RAVITHEJA
"""

import time
import logging
import feedparser
import requests
import json
import demjson
import os
from config import argument_config
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen
from SiteMap import SitemapParser
from finsymbols.symbols import get_sp500_symbols, get_nyse_symbols
from finsymbols.symbols import get_amex_symbols, get_nasdaq_symbols
from FinKafkaProducer import finKafkaProducer
from requests.auth import HTTPBasicAuth
from mongoDBConnection import initialize_mongo, insert_into_mongo

kafkaProducer = finKafkaProducer()
mongo_colln = initialize_mongo()
feed_count = {}


def main():
    """Initiates the Financial news extraction functionality.
    Executes RSS feed parser, Sitemap parser, Scraping and API calls."""

    t1 = time.time()

    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    # Fetching URLs from Config file.-
    rss_feed_urls = argument_config.get('rss_feed_urls')
    site_map_urls = argument_config.get('site_map_urls')
    scrapy_urls = argument_config.get('scrapy_urls')
    historical_urls = argument_config.get('historical_urls')

    ft_api_key = argument_config.get('ft_api_key')
    ft_api_id = argument_config.get('ft_api_id')
    ft_api_pwd = argument_config.get('ft_api_pwd')

    while True:
        """ RSSFeedParsing begins."""
        for rss_feed_name in rss_feed_urls:
            rss_feed_url = rss_feed_urls[rss_feed_name]
            logging.info("RSSfeed " + rss_feed_name + "[" + rss_feed_url + "]")
            parseAndSave(rss_feed_name, rss_feed_url)
    
        """URLs with subscription using authentication."""
        if ft_api_id and ft_api_pwd:
            try:
                news_url = "http://api.ft.com/content/search/v1"
                scrapeFT("financial-times", news_url, ft_api_id, ft_api_pwd,
                         ft_api_key)
            except:
                logging.warn("Problem while scraping Financial Times")
        else:
            logging.warn("Subscription not found for Financial Times")
    
        """ Scraping begins."""
        for source in scrapy_urls:
            scrape_url = scrapy_urls[source]
            logging.info("RSS feed of " + source + "[" + scrape_url + "]")
            scrapeAndSave(source, scrape_url)
    
        """ Historical data scraping using sitemap url. """
        for source in historical_urls:
            # Check if historical data is already downloaded.
            metadata_cursor = mongo_colln.find({"HISTORICAL": source})
            if metadata_cursor.count() == 0:
                robots_url = historical_urls[source]
                logging.info("SiteMap for " + source + " from " + robots_url)
                crawlAndScrape(source, robots_url)
    
                meta_mongo_colln = initialize_mongo("METADATA")
                meta_feedObj = {"HISTORICAL": source}
                insert_into_mongo(meta_mongo_colln, meta_feedObj)
    
            else:
                logging.info("Historical data already downloaded for " + source)
    
        """ SitemapParsing begins. It fetches all sitmap urls from robots.txt and
            filters the zip, xml urls."""
        for source in site_map_urls:
            robots_url = site_map_urls[source]
            logging.info("SiteMap for " + source + " from " + robots_url)
            crawlAndScrape(source, robots_url)
    
        all_fin_symbols = get_sp500_symbols() + get_nyse_symbols() + get_amex_symbols() + get_nasdaq_symbols()

        """ Google finance News extraction begins."""
        logging.info("Google Finance News...")
        getGoogleNews("google_fin_news", all_fin_symbols)

        """ Google Stocks extraction begins."""
        logging.info("Google Live Stocks...")
        getGoogleQuotes("google_stocks", all_fin_symbols)

        """Yahoo finance stock prices."""
        logging.info("Yahoo Finance Stocks...")
        getYahooStocks("yahoo_stocks", all_fin_symbols)

        logging.info(feed_count)
        logging.info("Total time taken for extracting all Financial News Data "
                     + ":: " + str(time.time() - t1))
        logging.info("This program is now in sleep mode. Will re-execute " +
                     "after 30 mins for latest news feeds.")
        time.sleep(180)


def scrapeFT(feedName, news_url, auth_id, auth_pwd, ft_api_key):
    payload = "{\r\n\t\"queryString\": \"sections:\\\"Financials\\\"\",\r\n\t\"resultContext\" : {\r\n\t\t \"aspects\" :[  \"title\",\"lifecycle\",\"location\",\"summary\",\"editorial\" ]\r\n\t}\r\n}"
    headers = {'x-api-key': ft_api_key}
    response = requests.request("POST", news_url, data=payload,
                                headers=headers)
    js = json.loads(response.content)
    for url in js['results']:
        res = url['results']
        for loc in res:
            loc_url = loc['location']['uri']
            metadata_cursor = mongo_colln.find({feedName: loc_url})
            if metadata_cursor.count() == 0:
                sendToKafka(feedName, loc_url, auth_id, auth_pwd)
            else:
                logging.info("Duplicate data Skipped")


def parseAndSave(feedName, feedURL):
    feed = feedparser.parse(feedURL)
    entries = feed['entries']
    for e in entries:
        logging.info(e['link'])
        metadata_cursor = mongo_colln.find({feedName: e['link']})
        if metadata_cursor.count() == 0:
            sendToKafka(feedName, e['link'])
        else:
            logging.info("Duplicate data Skipped")


def crawlAndScrape(source, robots_url):
    result = os.popen("curl " + robots_url).read()

    sitemapParser = SitemapParser()
    for line in result.split("\n"):
        if line.startswith('Sitemap'):    # this is for allowed url
            sitemap_url = line.split(': ')[1].split(' ')[0]
            print sitemap_url
            logging.info("Extracting SiteMap: " + sitemap_url)

            # for gz formats in Sitemap
            if sitemap_url.split(".")[-1] == "gz":
                cnt = sitemapParser.unzipSiteMapURL(source, sitemap_url)
                if source in feed_count:
                    feed_count[source] = feed_count[source] + cnt
                else:
                    feed_count[source] = cnt

            # for all other formats
            else:
                cnt = sitemapParser.crawlSiteMapXML(source, sitemap_url)
                if source in feed_count:
                    feed_count[source] = feed_count[source] + cnt
                else:
                    feed_count[source] = cnt


def scrapeAndSave(feedName, feedURL):
    resp = requests.get(feedURL)
    soup = BeautifulSoup(resp.text)
    rows = soup.find_all("tr", {"class": "nn"})
    for col in rows:
        td = col.find_all("td")
        for url in td:
            link = url.find('a', href=True)
            if link:
                metadata_cursor = mongo_colln.find({feedName: link['href']})
                if metadata_cursor.count() == 0:
                    sendToKafka(feedName, link['href'])
                else:
                    logging.info("Duplicate data Skipped")


def getGoogleNews(feedName, finsymbols):
    base_url = 'http://www.google.com/finance/company_news?output=json'\
                + '&start=0&num=1000&q='
    for symbol in finsymbols:
        resp = urlopen(Request(base_url + symbol['symbol']))
        content_json = demjson.decode(resp.read())
        # logging.info(symbol['symbol'], content_json['total_number_of_news'])
        article_json = []
        for cluster in content_json['clusters']:
            if 'a' in cluster:
                article_json.extend(cluster['a'])
        for article_url in article_json:
            metadata_cursor = mongo_colln.find({feedName: article_url['u']})
            if metadata_cursor.count() == 0:
                sendToKafka(feedName, article_url['u'])
            else:
                logging.info("Duplicate data Skipped")


def getGoogleQuotes(feedName, finsymbols):
    base_url = 'https://finance.google.com/finance?output=json&q='
    for symbol in finsymbols:
        final_url = base_url + symbol['symbol']
        sendToKafka(feedName, final_url)


def getYahooStocks(feedName, all_fin_symbols):
    for fin_symbol in all_fin_symbols:
        sym = fin_symbol['symbol']
        final_url = "https://finance.yahoo.com/quote/" + sym + "?p=" + sym
        sendToKafka(feedName, final_url)


def sendToKafka(source, final_url, auth_id='', auth_pwd=''):
    logging.info("To KafkaProducer :: [" + source + "] " + final_url)

    if source in feed_count:
        feed_count[source] = feed_count[source] + 1
    else:
        feed_count[source] = 1

    try:
        session = requests.Session()
        if auth_id and auth_pwd:
            final_response = session.get(final_url, allow_redirects=True,
                                         auth=HTTPBasicAuth(auth_id, auth_pwd))
            if final_response.content:
                kafkaProducer.kafkaSend(source, final_url,
                                        final_response.content)
            else:
                logging.info(str(final_response.status_code))
        else:
            final_response = session.get(final_url, allow_redirects=True)

            if final_response.content:
                kafkaProducer.kafkaSend(source, final_url,
                                        final_response.content)
            else:
                logging.info(str(final_response.status_code))
        time.sleep(3)
    except:
        logging.error("Error while request.get.")
    finally:
        session.close()


if __name__ == '__main__':
    main()
