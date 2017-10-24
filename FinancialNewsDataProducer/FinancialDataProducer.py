# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 09:38:57 2017

@author: RAVITHEJA
"""

import time
import logging
import feedparser
import requests
import demjson
import os
from config import argument_config
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen
from SiteMap import SitemapParser
from finsymbols.symbols import get_sp500_symbols, get_nyse_symbols
from finsymbols.symbols import get_amex_symbols, get_nasdaq_symbols
from kafka import KafkaProducer


kafka_broker_uri = argument_config.get('kafka_broker_uri')
producer = KafkaProducer(bootstrap_servers=[kafka_broker_uri])


def main():
    """Initiates the Financial news extraction functionality.
    Executes RSS feed parser, Sitemap parser, Scraping and API calls."""

    t1 = time.time()

    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    # Fetching URLs from Config file.
    rss_feed_urls = argument_config.get('rss_feed_urls')
    site_map_urls = argument_config.get('site_map_urls')
    scrapy_urls = argument_config.get('scrapy_urls')

    rss_keys = rss_feed_urls.keys()
    print rss_keys
    """ RSSFeedParsing begins."""
    for rss_feed_name in rss_feed_urls:
        rss_feed_url = rss_feed_urls[rss_feed_name]
        logging.info("RSS feed of " + rss_feed_name + "[" + rss_feed_url + "]")
        parseAndSave(rss_feed_name, rss_feed_url)

    """ SitemapParsing begins. It fetches all sitmap urls from robots.txt and
        filters the zip, xml urls."""
    for source in site_map_urls:
        if source in rss_keys:
            # TODO: Check in CKAN. If not available download the Historical data.
            pass
        print(source, site_map_urls[source])
        robots_url = site_map_urls[source]
        crawlAndScrape(source, robots_url)

    """ Scraping begins."""
    for source in scrapy_urls:
        scrape_url = scrapy_urls[source]
        logging.info("RSS feed of " + source + "[" + scrape_url + "]")
        scrapeAndSave(source, scrape_url)

    all_fin_symbols = get_sp500_symbols() + get_nyse_symbols() + get_amex_symbols() + get_nasdaq_symbols()

    """ Google finance News extraction begins."""
    logging.info("Google Finance News...")
    getGoogleNews("googleFinanceNews", all_fin_symbols)

    """ Google Stocks extraction begins."""
    logging.info("Google Live Stocks...")
    getGoogleQuotes("googleStocks", all_fin_symbols)

    """Yahoo finance stock prices."""
    logging.info("Yahoo Finance Stocks...")
    getYahooStocks("yahooStocks", all_fin_symbols)

    logging.info("Total time taken :: " + str(time.time() - t1))


def kafkaSendProducer(feedName, response):
    try:
        # Writing Tweet to Kafa Topics into producer
        producer.send(feedName, key=feedName, value=response)
        producer.flush()
        logging.info("-- FEED :: " + feedName)
    except ValueError:
        logging.info("Issue in kafka Producer for: " + feedName)


def parseAndSave(feedName, feedURL):
    feed = feedparser.parse(feedURL)
    entries = feed['entries']
    for e in entries:
        response = requests.get(e['link'])
        kafkaSendProducer(feedName, response.content)


def crawlAndScrape(source, robots_url):
    result = os.popen("curl " + robots_url).read()
    sitemapParser = SitemapParser()
    for line in result.split("\n"):
        if line.startswith('Sitemap'):    # this is for allowed url
            sitemap_url = line.split(': ')[1].split(' ')[0]
            if sitemap_url.split(".")[-1] != "gz":
                sitemapParser.crawlSiteMap(source, sitemap_url)
            else:
                sitemapParser.unzipURL(source, sitemap_url)


def scrapeAndSave(feedName, feedURL):
    r = requests.get(feedURL)
    data = r.text
    # parse fetched data using beatifulsoup
    soup = BeautifulSoup(data)
    rows = soup.find_all("tr", {"class": "nn"})

    for col in rows:
        td = col.find_all("td")
        for url in td:
            link = url.find('a', href=True)
            if link:
                original_link = link['href']
                logging.info("Scraping " + feedName + "[" + original_link
                             + "]")
                response = requests.get(original_link)
                kafkaSendProducer(feedName, response.content)


def getGoogleNews(feedName, finsymbols):
    base_url = 'http://www.google.com/finance/company_news?output=json'\
                + '&start=0&num=1000&q='
    for symbol in finsymbols:
        resp = urlopen(Request(base_url + symbol['symbol']))
        content_json = demjson.decode(resp.read())
        logging.info(symbol['symbol'], content_json['total_number_of_news'])

        article_json = []
        for cluster in content_json['clusters']:
            if 'a' in cluster:
                article_json.extend(cluster['a'])
        for article_url in article_json:
            logging.info(article_url['u'])
            response = requests.get(article_url['u'])
            kafkaSendProducer(feedName, response.content)


def getGoogleQuotes(feedName, finsymbols):
    base_url = 'https://finance.google.com/finance?output=json&q='
    for symbol in finsymbols:
        symbol = symbol['symbol']
        rsp = requests.get(base_url + symbol)

        if rsp.status_code in (200,):
            logging.info("Writing Google Stock data (to Topic): " + symbol)
            kafkaSendProducer(feedName, rsp.content)


def getYahooStocks(feedName, all_fin_symbols):
    for fin_symbol in all_fin_symbols:
        sym = fin_symbol['symbol']
        # base_url = 'http://finance.yahoo.com/d/quotes.csv?f=sb2b3jk&s=' + sym
        base_url = "https://finance.yahoo.com/quote/" + sym + "?p=" + sym
        rsp = requests.get(base_url)

        if rsp.status_code in (200,):
            print rsp.content
            logging.info("Writing Yahoo Stock data (to Topic): " + sym)
            kafkaSendProducer(feedName, rsp.content)


if __name__ == '__main__':
    main()
