# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:25:49 2017

@author: RAVITHEJA
"""

import os


RSS_FEED_URLS = {
        "thomson_reuters": "http://feeds.reuters.com/reuters/INbusinessNews",
        "wall_street_journal": "http://www.wsj.com/xml/rss/3_7031.xml",
        "cnbc": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "cnn_money": "http://rss.cnn.com/rss/money_latest.rss",
        "morning_star": "http://feeds.feedburner.com/morningstar/glkd",
        "rtt_news": "http://www.rttnews.com/RSS/Todaystop.xml",
        "seeking_alpha": "https://seekingalpha.com/sector/financial.xml",
        "yahoo_finance": "https://finance.yahoo.com/rss/topstories",
        "motley_fool": "http://culture.fool.com/feed/",
        "zacks_investment": "http://feed.zacks.com/commentary/AllStories/rss",
        
        # Need Subscription 
        # "financial_times": "https://www.openft.org/searches/083bb4149bf03104c4549dcbc929b428e8f98c84.rss", # need API KEY
        }

SITE_MAP_URLS = {
        "bloomberg": "https://www.bloomberg.com/robots.txt",
        "market_watch": "http://www.marketwatch.com/robots.txt",
        "forbes": "https://www.forbes.com/robots.txt",
        "the_street": "https://www.thestreet.com/robots.txt",
        "msci_dataset": "https://www.msci.com/robots.txt",
        "ceic_dataset": "https://www.ceicdata.com/robots.txt",

        # SITEMAPS FOR HISTORICAL RSS 
        "wall_street_journal": "https://www.wsj.com/robots.txt",
        "cnbc": "https://www.cnbc.com/robots.txt",
        "cnn_money": "http://money.cnn.com/robots.txt",
        "rtt_news": "http://www.rttnews.com/robots.txt",
        "seeking_alpha": "https://seekingalpha.com/robots.txt",
        "motley_fool": "http://culture.fool.com/robots.txt",
        "zacks_investment": "https://www.zacks.com/robots.txt",
        }

SCRAPY_URLS = {
        "finviz": "https://finviz.com/news.ashx",
        }


argument_config = {
    'rss_feed_urls': os.getenv('RSS_FEED_URLS', RSS_FEED_URLS),
    'site_map_urls': os.getenv('SITE_MAP_URLS', SITE_MAP_URLS),
    'scrapy_urls': os.getenv('SCRAPY_URLS', SCRAPY_URLS),
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', 'localhost:9092'),
}
