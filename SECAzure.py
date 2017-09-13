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
from azure.storage.blob import BlockBlobService, ContainerPermissions
from datetime import datetime, timedelta
from os import path


class SEC_Azure():

    def __init__(self, azure_account_name, azure_account_key, azure_container):
        # initializing class variables
        self.azure_container = azure_container
        self.block_blob_service = BlockBlobService(
            account_name=azure_account_name,
            account_key=azure_account_key)
        # creating azure container, iff container doesn't exist.
        if not self.block_blob_service.exists(self.azure_container):
            self.block_blob_service.create_container(self.azure_container)

    def createDocumentList(self, cik, year):
        if (len(cik) != 10):
            while(len(cik) != 10):
                cik = '0' + cik

        # generate the url to crawl
        base_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + \
            str(cik) + "&type=10-K&dateb=&owner=exclude&output=xml&start=0&count="
        r = requests.get(base_url)
        data = r.text

        # parse fetched data using beatifulsoup
        soup = BeautifulSoup(data)

        # store the link in the list
        link_list = list()
        year_link_list = soup.find_all(['datefiled', 'filinghref'])
        year_link_string = [str(e) for e in year_link_list]

        arg = year + '-'
        for year_str in year_link_string:
            if arg in year_str:
                i = year_link_string.index(year_str)
                if len(year_link_string) > i + 1:
                    link = year_link_string[i + 1]
                    url = re.split('[< >]', link)[2]

                    # If the link is .htm, convert it to .html
                    if url.split(".")[len(url.split(".")) - 1] == "htm":
                        url += "l"
                    link_list.append(url)

        azure_urls, file_types = self.downloadToAzure(cik, link_list)

        return azure_urls, file_types

    def downloadToAzure(self, cik, link_list):
        # Get all the doc
        azure_urls = set()
        file_types = set()

        for k in range(len(link_list)):
            original_url = ''
            try:
                soup1 = BeautifulSoup(urlopen(link_list[k]))
            except BaseException:
                continue

            tablecheck = soup1.findAll("table", {"class": "tableFile"})
            table1 = soup1.findAll(
                "table", {
                    "class": "tableFile", "summary": "Document Format Files"})

            if(len(tablecheck) == 2):
                xbrl_zip_file_url = link_list[k].replace(
                    '-index.html', '') + "-xbrl.zip"
                xbrl_zip_file_name = xbrl_zip_file_url.split("/")[-1]

                r = requests.get(xbrl_zip_file_url, stream=True)
                stream = io.BytesIO(r.content)

                self.block_blob_service.create_blob_from_stream(path.join(
                    self.azure_container, cik), xbrl_zip_file_name, stream)
                sas_token = self.block_blob_service.generate_blob_shared_access_signature(
                    self.azure_container,
                    path.join(cik, xbrl_zip_file_name),
                    expiry=datetime.utcnow() + timedelta(weeks=52),
                    permission=ContainerPermissions.READ)

                download_url = self.block_blob_service.make_blob_url(
                    self.azure_container, path.join(
                        cik, xbrl_zip_file_name), sas_token=sas_token)
                azure_urls.add(download_url)
                file_types.add(xbrl_zip_file_url.split(".")[-1])

            for tbl in table1:
                rows = tbl.findAll('tr')
                for tr in rows:
                    cols = tr.findAll('td')
                    for td in cols:
                        url = tr.find('a', href=True)
                        original_url = url['href']

                        arc = "https://www.sec.gov" + original_url

                        file_name = original_url.split("/")[-1]
                        file_type = original_url.split(".")[-1]

                        if(file_name != ''):
                            if(file_type == 'pdf' or
                               file_type == 'gif' or
                               file_type == 'jpg'):
                                r = requests.get(arc, stream=True)
                                stream = io.BytesIO(r.content)
                                self.block_blob_service.create_blob_from_stream(
                                    path.join(self.azure_container, cik),
                                    file_name, stream)
                            else:
                                f = requests.get(arc)
                                self.block_blob_service.create_blob_from_text(
                                    path.join(self.azure_container, cik),
                                    file_name, f.text)

                            sas_token = self.block_blob_service.generate_blob_shared_access_signature(
                                self.azure_container,
                                path.join(cik, file_name),
                                expiry=datetime.utcnow() + timedelta(weeks=52),
                                permission=ContainerPermissions.READ)

                            download_url = self.block_blob_service.make_blob_url(
                                self.azure_container, path.join(cik, file_name), sas_token=sas_token)
                            azure_urls.add(download_url)
                            file_types.add(file_type)
                            break

        return azure_urls, file_types
