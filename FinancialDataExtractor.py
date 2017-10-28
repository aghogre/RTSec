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
from mongoDBConnection import initialize_mongo

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
    auth_urls = argument_config.get('auth_urls')
    ft_api_key = argument_config.get('ft_api_key')

    # while True:
    """ SitemapParsing begins. It fetches all sitmap urls from robots.txt and
        filters the zip, xml urls.
    for source in site_map_urls:
        robots_url = site_map_urls[source]
        logging.info("SiteMap for " + source + " from " + robots_url)
        crawlAndScrape(source, robots_url)"""

    """ RSSFeedParsing begins."""
    for rss_feed_name in rss_feed_urls:
        rss_feed_url = rss_feed_urls[rss_feed_name]
        logging.info("RSSfeed " + rss_feed_name + "[" + rss_feed_url + "]")
        parseAndSave(rss_feed_name, rss_feed_url)

    """ URLs with subscription using authentication.
    for auth_item in auth_urls:
        auth_credentials = auth_urls[auth_item]
        auth_id = auth_credentials['auth_id']
        auth_pwd = auth_credentials['auth_pwd']

        if auth_id and auth_pwd:
            try:
                if auth_item == "financial-times":
                    news_url = "http://api.ft.com/content/search/v1"
                    scrapeFT(auth_item, news_url, auth_id, auth_pwd,
                             ft_api_key)
                elif auth_item == "the-wall-street-journal":
                    news_url = "https://newsapi.org/v1/articles"
                    ## scrapeWSJ(auth_item, news_url, auth_id, auth_pwd)
            except:
                logging.warn("Problem while scraping " + auth_item)
                continue
        else:
            logging.warn("Subscription not found for: " + auth_item)"""

    """ Scraping begins.
    for source in scrapy_urls:
        scrape_url = scrapy_urls[source]
        logging.info("RSS feed of " + source + "[" + scrape_url + "]")
        scrapeAndSave(source, scrape_url)

    all_fin_symbols = get_sp500_symbols() + get_nyse_symbols() + get_amex_symbols() + get_nasdaq_symbols()
    """
    """ Google finance News extraction begins.
    logging.info("Google Finance News...")
    getGoogleNews("google_fin_news", all_fin_symbols)"""

    """ Google Stocks extraction begins.
    logging.info("Google Live Stocks...")
    getGoogleQuotes("google_stocks", all_fin_symbols)"""

    """Yahoo finance stock prices.
    logging.info("Yahoo Finance Stocks...")
    getYahooStocks("yahoo_stocks", all_fin_symbols)"""

    logging.info(feed_count)
    logging.info("Total time taken for extracting all Financial News Data :: "
                 + str(time.time() - t1))
        #time.sleep(180)
    

def scrapeWSJ(feedName, news_url, auth_id, auth_pwd):
    querystring = {"source": feedName,
                   "sortBy": "top",
                   "apiKey": "67c7663f07af4c388e2734118ffa6b17"}
    auth_response = requests.request("GET", news_url, params=querystring)
    js = json.loads(auth_response.content)
    for url in js['articles']:
        metadata_cursor = mongo_colln.find({feedName: url['url']})
        if metadata_cursor.count() == 0:
            sendToKafka(feedName, url['url'], auth_id, auth_pwd)
        else:
            logging.info("Duplicate data Skipped")


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

            # for XML formats in Sitemap
            if sitemap_url.split(".")[-1] == "xml":
                cnt = sitemapParser.crawlSiteMapXML(source, sitemap_url)
                if source in feed_count:
                    feed_count[source] = feed_count[source] + cnt
                else:
                    feed_count[source] = cnt

            # for gz formats in Sitemap
            elif sitemap_url.split(".")[-1] == "gz":
                cnt = sitemapParser.unzipSiteMapURL(source, sitemap_url)
                if source in feed_count:
                    feed_count[source] = feed_count[source] + cnt
                else:
                    feed_count[source] = cnt

            # for HTML formats in Sitemap
            elif sitemap_url.split(".")[-1] == "html":
                pass

            # for other unknown formats
            else:
                pass


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
        metadata_cursor = mongo_colln.find({feedName: final_url})
        if metadata_cursor.count() == 0:
            sendToKafka(feedName, final_url)
        else:
            logging.info("Duplicate data Skipped")


def getYahooStocks(feedName, all_fin_symbols):
    for fin_symbol in all_fin_symbols:
        sym = fin_symbol['symbol']
        final_url = "https://finance.yahoo.com/quote/" + sym + "?p=" + sym
        metadata_cursor = mongo_colln.find({feedName: final_url})
        if metadata_cursor.count() == 0:
            sendToKafka(feedName, final_url)
        else:
            logging.info("Duplicate data Skipped")


def sendToKafka(source, final_url, auth_id='', auth_pwd=''):
    session = requests.Session()
    logging.info("To KafkaProducer :: [" + source + "] " + final_url)

    if source in feed_count:
        feed_count[source] = feed_count[source] + 1
    else:
        feed_count[source] = 1

    try:
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
    except:
        pass

    time.sleep(3)
    session.close()


if __name__ == '__main__':
    main()
