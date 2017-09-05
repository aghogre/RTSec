# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:56:40 2017

@author: ANSHUL
"""

import requests
import io
import re
from bs4 import BeautifulSoup
from urllib2 import urlopen
from azure.storage.blob import BlockBlobService


class SEC_Azure():

    def __init__(self, azure_account_name, azure_account_key, azure_container):
        self.azure_container = azure_container
        self.block_blob_service = BlockBlobService(account_name = azure_account_name, 
                                                   account_key = azure_account_key)
        #creating azure container
        self.block_blob_service.create_container(self.azure_container)
    
    
    def createDocumentList(self, cik, year):
        if (len(cik) != 10):
            while(len(cik) != 10):
                cik = '0'+cik

        # generate the url to crawl
        base_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+str(cik)+"&type=10-K&dateb=&owner=exclude&output=xml&start=0&count="
        r = requests.get(base_url)
        data = r.text

        # parse fetched data using beatifulsoup
        soup = BeautifulSoup(data)
        
        # store the link in the list
        link_list = list()
        year_link_list = soup.find_all(['datefiled','filinghref'])
        year_link_string = [str(e) for e in year_link_list]
        
        arg = year + '-'
        for year_str in year_link_string:
            if arg in year_str:
                i = year_link_string.index(year_str)
                link = year_link_string[i+1]
                url =  re.split('[< >]', link)[2]

                # If the link is .htm, convert it to .html
                if url.split(".")[len(url.split("."))-1] == "htm":
                    url += "l"
                link_list.append(url)
        
        self.downloadToAzure(cik, link_list)
        download_url = self.block_blob_service.make_blob_url(self.azure_container, str(cik))
        return download_url 
    

    def downloadToAzure(self, cik, link_list):
        # Get all the doc
        source_list = [] #sourcelist
        for k in range(len(link_list)):
            original_url=''
            soup1= BeautifulSoup(urlopen(link_list[k]))
            tablecheck = soup1.findAll("table",{"class":"tableFile"})
            table1 = soup1.findAll("table",{"class":"tableFile","summary":"Document Format Files"})
            
            if(len(tablecheck)==2):
                
                required_xbrl_url = link_list[k].replace('-index.html', '') 
                xbrl_zip_file_url = required_xbrl_url + "-xbrl.zip"
                xbrl_zip_file_name = xbrl_zip_file_url.split("/")[-1]
                if 'zip'  not in source_list:
                    source_list = source_list.append(xbrl_zip_file_url.split(".")[-1])   #sourcelist
                r = requests.get(xbrl_zip_file_url, stream=True)
                stream = io.BytesIO(r.content)
                                
                #print("downloading zip " + xbrl_zip_file_url)
                self.block_blob_service.create_blob_from_stream(self.azure_container+'/'+cik, xbrl_zip_file_name, stream)
            else:
                pass
                #print('No Xbrl files available')            
            
            for tbl in table1:                    
                rows = tbl.findAll('tr')
                for tr in rows:
                    cols = tr.findAll('td')
                    for td in cols:
                        url = tr.find('a' , href=True)
                        original_url = url['href']
                        
                        arc = "https://www.sec.gov"+original_url
                        #print(arc)
                        if(original_url.split("/")[-1] != ''):
                            if(original_url.split(".")[-1]=='pdf' or original_url.split(".")[-1]=='gif' 
                               or original_url.split(".")[-1]=='jpg'):
                                r = requests.get(arc, stream=True)
                                stream = io.BytesIO(r.content)
                                self.block_blob_service.create_blob_from_stream(self.azure_container+'/'+cik, 
                                                                                original_url.split("/")[-1], stream)
                                if 'pdf' or 'gif'  or 'jpg' not in source_list:
                                    source_list = source_list.append(original_url.split(".")[-1])                         #sourcelist 
                                break
                            else:  
                                f = requests.get(arc)
                                self.block_blob_service.create_blob_from_text(self.azure_container+'/'+cik, 
                                                                              original_url.split("/")[-1], f.text)
                                if 'htm' or 'txt'  not in source_list:
                                    source_list = source_list.append(original_url.split(".")[-1])                         #sourcelist
                                break                            
                        else:
                            pass 
                            #print('No file Found for')
       
       