# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:53:18 2017

@author: ADMIN
"""

import re
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup




class SECCrawler():

    def __init__(self):
        #Setting path to  download a file 
        os.chdir(os.path.dirname(os.path.abspath('SECData.py')))
        self.browser = Browser()
        self.browser.addheaders = [('User-agent', 'Mozilla/5.0\
            (Windows NT 6.2; WOW64) AppleWebKit/537.11 (KHTML, like Gecko)\
            Chrome/23.0.1271.97 Safari/537.11')]

    
    def get10kdata(self, year):
        df = []
        archive_url = "https://www.sec.gov/Archives/edgar/full-index/"+year+"/"
        
        r = requests.get(archive_url) 
        soup = BeautifulSoup(r.content, "html.parser")
       
        for n in range(1,5):
            qtr = "QTR"+str(n)+"/"
            if soup.find("a", {"href" : qtr}):
                url ="https://www.sec.gov/Archives/edgar/full-index/"+year+"/"+qtr+"/company.idx"
                print "URL -->> ",url
                company_index = pd.read_table(url, header=None, 
                                              skiprows=[0,1,2,3,4,5], engine='python')
                idx_list = company_index.values.tolist()
                
                col_heads= [re.sub('\s\s+','$$', head) for head in idx_list[0] ]
                col_heads = col_heads[0].strip().split('$$')
                    
                #Fetch all rows data for company index
                col_10k = col_heads.index('Form Type')
                data_list = []
                raw_row = []
                for data in idx_list[2:]:
                    record_elements = []
                    for row in data:
                        raw_row = re.sub('\s\s+','$$', row)
                        record_elements = raw_row.strip().split('$$')[:len(col_heads)]
                    if record_elements[col_10k] =='10-K':
                        data_list.append(record_elements)
                
                df.append(pd.DataFrame(data_list, columns=col_heads))
                print("length("+qtr+") -- " + str(len(df[n-1])))
                
        df_all = pd.concat([df[part] for part in range(0,len(df))])
        cik_list = df_all[['CIK']]
            
        print("Total ciks for "+year+" are " + str(len(cik_list)))
       # return cik_list.values.tolist()
        return cik_list
    
    
