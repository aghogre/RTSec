# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 16:48:44 2017
@author: ADMIN
"""

import os

TWITTER_ACCOUNT_IDS = { "business":"34713362",
                        "WSJ":"3108351",
                        "WSJMarkets":"28164923",
                        "Forbes":"91478624",
                        "TheEconomist":"5988062",
                        "FT":"18949452",
                        "Reuters":"1652541",
                        "nytimes":"807095",
                        "MarketFolly":"14173032",
                        "CNNMoney":"16184358",
                        "TheStreet":"15281391",
                        "MarketWatch":"624413",
                        "YahooFinance":"19546277",
                        "jimcramer":"14216123",
                        "TruthGundlach":"861619895485726722",
                        "Carl_C_Icahn":"1534167900",
                        "ReformedBroker":"22522178",
                        "Schuldensuehner":"40129171",
                        "LizAnnSonders":"2961589380",
                        "NorthmanTrader":"714051110",
                        "Frances_Coppola":"101002059",
                        "bySamRo":"239026022",
                        "BrianSozzi":"104257356",
                        "Wu_Tang_Finance":"553713584",
                        "TheStalwart":"14096763",
                        "RyanDetrick":"21232827",
                        "zerohedge":"18856867",
                        "Amena_Bakr":"338221793",
                        "kitjuckes":"58754203",
                        "Benzinga":"44060322",
                        "CiovaccoCapital":"264370502",
                        "JLyonsFundMGMT":"244248703",
                        "jasonzweigwsj":"89043072",
                        "Samir_Madani":"317643185",
                        "Brenda_Kelly":"47621568",
                        "LiveSquawk":"59393368",
                        "vexmark":"2992395456",
                        "Sassy_SPY":"375980238",
                        "StockTwits":"14886375",
                        "KeithMcCullough":"18378349",
                        "FXCM":"110793585",
                        "JoelKruger":"23102962",
                        "bespokeinvest":"28571999",
                        "IBDinvestors":"21328656",
                        "PaulKrugman":"17006157",
                        "JustinWolfers":"327577091",
                        "jessefelder":"1473431",
                        "DailyFXTeam":"28366310",
                        "Ukarlewitz":"37284991",
                        "Stephanie_Link":"455309376"
                        }

argument_config = {
    'consumer_key': os.getenv('CONSUMER_KEY', '3KD4GKbxCVsvTLy7IbSlq07vy'),
    'consumer_secret': os.getenv('CONSUMER_SECRET', 'JXOYEOW7jp7iDRUGc49Gu8cRy5bZMPwCSxG1GqUbtHaJ3DLDU6'),
    'access_token': os.getenv('ACCESS_TOKEN', '909762256350601216-eqFBd8WIW7PmHsru3VlR6eS7Mg5dnXT'),
    'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET', 'uTjwzMo7jEfkRVWyA9dSJAQ6mePBGEcmjgCVa0lAIDB23'),
    'twitter_hashtags': os.getenv('TWITTER_HASHTAGS', TWITTER_ACCOUNT_IDS),
    'kafka_broker_uri': os.getenv('KAFKA_BROKER_URI', '173.193.179.253:9092'),
    'kafka_topic': os.getenv('KAFKA_TOPIC', 'tweeter')
}

