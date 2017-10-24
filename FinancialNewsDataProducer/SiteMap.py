"""
Created on Thu Oct 12 12:16:53 2017

@author: RAVITHEJA
"""

import requests
import zlib
import httplib2
import logging
from functools import partial
from lxml import etree
from StringIO import StringIO
from bs4 import BeautifulSoup
from config import argument_config
from kafka import KafkaProducer


class SitemapParser():
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s \
                            %(module)s.%(funcName)s %(message)s',
                            level=logging.INFO)

    def crawlSiteMap(self, source, sitemap_url):
        # Proces each .xml urls from robots.txt and return html object.
        index_response = requests.get(sitemap_url)
        index_root = etree.fromstring(index_response.content)
        print "The number of xml urls {0}".format(len(index_root))

        # Process all sub .xml urls available,stored in list
        h = 1
        for sitemap in index_root:
            index_children = sitemap.getchildren()
            index_loc = index_children[0].text
            if index_loc.split(".")[-1] == "xml":
                print "Processing the {0} url ".format(h) + "amoung {0} Urls"\
                    .format(len(index_root))
                urlset_response = requests.get(index_loc)
                soup = BeautifulSoup(urlset_response.text)
                urlset_locs = soup.find_all("loc")
                print " Processing the {0} url and it contains".format(h) \
                    + "{0} urls" .format(len(urlset_locs))
                h = h + 1
                k = 1
                # Process all sub .xml urls list,returns html object for mongo
                for urlset_loc in urlset_locs:
                    final_url = urlset_loc.contents[0]
                    http = httplib2.Http()
                    http_headers, http_response = http.request(final_url,
                                                               'GET')
                    if http_headers['status'] == "200":
                        k = k + 1
                        self.kafkaSendProducer(source, http_response)
            else:
                http = httplib2.Http()
                http_headers, http_response = http.request(index_loc, 'GET')
                if http_headers['status'] == "200":
                    h = h + 1
                    self.kafkaSendProducer(source, http_response)

    def unzipURL(self, source, sitemap_url):
        # Process the zip url from robot.txt and store in mongo
        response = requests.get(sitemap_url, stream=True)
        sitemap_xml = self.decompress_stream(response.raw)
        tree = etree.parse(sitemap_xml)
        root = tree.getroot()
        print "The number of gz tags are {0}".format(len(root))
        locs = []
        i = 1
        for sitemap in root:
                children = sitemap.getchildren()
                print i, children[0].text
                i = i + 1
                type(children)
                locs.append(children[0].text)      # 23 urls
                len(locs)
        j = 1
        for loc in locs:
            if loc.split(".")[-1] == "gz":
                print j, " The procesing url is {0} ".format(loc)
                response = requests.get(loc, stream=True)
                sitemap_xml = self.decompress_stream(response.raw)
                tree = etree.parse(sitemap_xml)
                root = tree.getroot()
                print " <<<>>>> Final_urls are {0}".format(len(root)) + \
                    " at {0} ".format(loc.split("/")[-1])
                j = j + 1

                final_urls = []
                for sitemap in root:
                    children = sitemap.getchildren()
                    final_urls.append(children[0].text)

                k = 1
                for final_url in final_urls:
                    http = httplib2.Http()
                    http_headers, http_response =  \
                        http.request(final_url, 'GET')
                    if http_headers['status'] == "200":
                        print " Inserted {0} url into mongo  ".format(k)
                        k = k+1
                        self.kafkaSendProducer(source, http_response)

    def decompress_stream(self, rraw):
        # Decompress the zip url
        READ_BLOCK_SIZE = 1024 * 8
        result = StringIO()
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        for chunk in iter(partial(rraw.read, READ_BLOCK_SIZE), ''):
            result.write(d.decompress(chunk))
        result.seek(0)
        return result

    def kafkaSendProducer(self, feedName, response):
        kafka_broker_uri = argument_config.get('kafka_broker_uri')
        producer = KafkaProducer(bootstrap_servers=[kafka_broker_uri])
        try:
            # Writing Tweet to Kafa Topics into producer
            producer.send(feedName, key=feedName, value=response)
            producer.flush()
            logging.info("-- FEED :: " + feedName)
        except ValueError:
            logging.info("Issue in kafka Producer for: " + feedName)
