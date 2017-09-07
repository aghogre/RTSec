# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:53:18 2017

@author: ADMIN
"""

import re
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup


class SECCrawler():

    def __init__(self):
        #Setting path to  download a file 
        os.chdir(os.path.dirname(os.path.abspath('SECData.py')))

    
    def get10kdata(self, year):
        df = []
        archive_url = "https://www.sec.gov/Archives/edgar/full-index/"+year+"/"
        r = requests.get(archive_url)

        # create beautiful-soup object
        soup = BeautifulSoup(r.content)
        table = soup.find('table', {'summary':'heding'})
        rows = table.findAll('tr')
        for tr in rows:
            if tr.find("th", text="Name") or tr.find("th", text="Size") or tr.find("th", text="Last Modified\n"):
            #if tr.text== 'NameSizeLast Modified\n':
                continue 
            else:
                cols = tr.findAll('td')
                links = cols[0].find('a').get('href')
                url ="https://www.sec.gov/Archives/edgar/full-index/"+year+"/"+links+"/company.idx"
                print "URL -->> ",url
                company_index = pd.read_table(url,header=None,skiprows=[0,1,2,3,4,5],engine='python')
                list = company_index.values.tolist()
                
                if links:
                    col_heads= [re.sub('\s\s+','$$', head) for head in list[0] ]
                    col_heads = col_heads[0].strip().split('$$')
                    #print col_heads
                    
                #Fetch all rows data for company index
                col_10k = col_heads.index('Form Type')
                data_list = []
                raw_row = []
                for data in list[2:]:
                    record_elements = []
                    for row in data:
                        raw_row = re.sub('\s\s+','$$', row)
                        record_elements = raw_row.strip().split('$$')[:len(col_heads)]
                    if record_elements[col_10k] =='10-K':
                        data_list.append(record_elements)
                
                df.append(pd.DataFrame(data_list, columns=col_heads))
                
            df_all = pd.concat([df[part] for part in range(0,len(df))])
            cik_list = df_all[['CIK']]
            
        #print(cik_list)
        return cik_list.values.tolist()
    
    