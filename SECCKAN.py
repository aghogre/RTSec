# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 13:03:13 2017

@author: RAVITHEJA
"""

import json
import urllib2
import ckanapi
import re
from datetime import datetime

class SEC_CKAN():

    def __init__(self, ckan_host, api_key, azure_container, publisher):
        # initializing class variables
        self.ckan_host = ckan_host
        self.api_key = api_key
        self.azure_container = azure_container
        self.publisher = publisher

        # Establishing connection with CKAN
        self.ckan_ckan = ckanapi.RemoteCKAN(ckan_host, apikey = api_key)
        
    
    # To save the metadata of CIKs downloaded into Azure.
    def storeMetadata(self, cik, azure_urls, file_types, year, license_azure_url):    
        # read all metadata information from 'metadata.json'
        with open('ticker_metadata.json') as json_file:    
            json_data = json_file.read()
            metadata_json = json.loads(json_data)
        
        # fetch the metadata info for the cik, from json
        metadata = [mdata for mdata in metadata_json["metadata"] if mdata["cik"] == str(cik)]
        
        # flag the availability of ticker info 
        tickerInfo = False
        if len(metadata) != 0:
            tickerInfo = True
            metadata = metadata[0]

        package_name = "sec_" + cik
        current_date = datetime.now().strftime("%B %d, %Y, %H:%M")
        tags = []
        package_title = ''
        description = ''

        # iterate the URLs of files stored in Azure to organize a dict of URLs.
        multi_url_dict = {'url' + str(i + 1): url for i, url in enumerate(azure_urls)}
                
        # create or update the package for each artifact with latest Metadata of Azure datasets.
        if tickerInfo:
            package_title = metadata["Title"].replace('.','')       
            if "Tags" in metadata:
               for tag in metadata["Tags"].split(','):
                   if str(tag).strip():
                       tags.append({'name': str(tag).strip()})
            tags.append({'name': str(year)})

            # additional fields to be added in CKAN dataset
            dict_additional_fields = {
                'Title':package_title,
                'Sourcing_Date': current_date,
                'SourceType': file_types,
                'Source': metadata["Source"],
                'Container' : metadata["Container"],
                'License' : license_azure_url,
                'Ticker' : metadata["Ticker"],
                'Exchange' : metadata["Exchange"],
                'Industry' : metadata["Industry"],
                'cik' : metadata["cik"],
                'IRS Number' : metadata["IRS Number"],
                'Business' : metadata["Business"],
                'Incorporated' : metadata["Incorporated"],
            }
            description = metadata["Description"] + "\n\n" 
        else:
            package_title = "SEC " + cik
            description = "SEC 10-K filings for " +package_title
            tags.append({'name': str(year)})
            tags.append({'name': str(cik)})
            
            # additional fields to be added in CKAN dataset
            dict_additional_fields = {
                'Title':package_title,
                'Sourcing_Date': current_date,
                'SourceType': file_types,
                'Source': "SEC",
                'Container' : self.azure_container,
                'License' : license_azure_url,
                'cik' : cik
            }

        # appending URLs to the additional fields
        dict_additional_fields.update(multi_url_dict)
    
        # adding extra properties to CKAN dataset using Wrapper 'extras'
        additional_fields = []
        for k, v in dict_additional_fields.items():
            additional_fields.append({'key': k, 'value': v})
            
        try:
            # attempting to create a new package
            self.createPackage(description, package_name, package_title, year, 
                               tags, additional_fields)
        except ckanapi.ValidationError as ve:
           if (ve.error_dict['__type'] == 'Validation Error'):
               if('name' in ve.error_dict 
                  and ve.error_dict['name'] == ['That URL is already in use.']):                       
                   try:
                       # in case package already existed, attempting to update the same.
                       self.updatePackage(description, package_name, package_title, 
                                          cik, year, tags, additional_fields)
                   except ckanapi.ValidationError as ve2:
                       if('tags' in ve2.error_dict and len(ve2.error_dict['tags'])>0):
                           # in case any tags not supported due to special characters,
                           # rebuilding the tags and updating the package
                           tags = self.rebuildTags(cik, year)
                           self.updatePackage(description, package_name, package_title, 
                                              cik, year, tags, additional_fields)
                       else:
                           raise
               elif('tags' in ve.error_dict and len(ve.error_dict['tags'])>0):
                   for e in ve.error_dict['tags']:
                       if "must be alphanumeric characters" in e:
                           try:
                               # in case any tags not supported due to special characters,
                               # rebuilding the tags and creating the package
                               tags = self.rebuildTags(cik, year)
                               self.createPackage(description, package_name, package_title, 
                                                  year, tags, additional_fields)
                           except:
                               # in case any tags not supported due to special characters,
                               # rebuilding the tags and updating the package
                               tags = self.rebuildTags(cik, year)
                               self.updatePackage(description, package_name, package_title, 
                                                  cik, year, tags, additional_fields)                                       
               else:
                   raise
           else:
               raise
        except:
           raise
           

    # creating package in CKAN
    def createPackage(self, description, package_name, package_title, year, 
                       tags, additional_fields):
        try:
            self.ckan_ckan.action.package_create(name=package_name, 
                              title=package_title,
                              owner_org="securities-exchange-commission",
                              notes=description,
                              maintainer=self.publisher,
                              version=year,
                              tags=tags,
                              extras=additional_fields,
                              #link = "https://randomtrees.blob.core.windows.net/sec1994/0000820081\\?sr=b&sp=r&sig=MPFHne0n0JYu2Lldv2gssnHOk8wz0z7eeBfdUX0hpWM%3D&sv=2015-07-08&se=2018-09-10T07%3A00%3A31Z', 'url2': 'https://randomtrees.blob.core.windows.net/sec1994/0000820081\\0000950123-94-000557.txt?sr=b&sp=r&sig=NM4bXhtc4RKhxtCkknu8/ehqoWvJZmiF44fjl%2BfusLw%3D&sv=2015-07-08&se=2018-09-10T07%3A00%3A31Z"
                              )
        except:
               raise

        
    # creating package in CKAN
    def updatePackage(self, description, package_name, package_title, cik, year, 
                      tags, additional_fields):
        try:
            self.ckan_ckan.action.package_update(id=package_name, 
                              title=package_title,
                              owner_org="securities-exchange-commission",
                              notes=description,
                              maintainer=self.publisher,
                              version=self.getVersions(cik, year),
                              tags=tags,
                              extras=additional_fields,
                             # link = "https://randomtrees.blob.core.windows.net/sec1994/0000820081\\?sr=b&sp=r&sig=MPFHne0n0JYu2Lldv2gssnHOk8wz0z7eeBfdUX0hpWM%3D&sv=2015-07-08&se=2018-09-10T07%3A00%3A31Z', 'url2': 'https://randomtrees.blob.core.windows.net/sec1994/0000820081\\0000950123-94-000557.txt?sr=b&sp=r&sig=NM4bXhtc4RKhxtCkknu8/ehqoWvJZmiF44fjl%2BfusLw%3D&sv=2015-07-08&se=2018-09-10T07%3A00%3A31Z"
                              )
        except:
               raise

        
    def getVersions(self, cik, year):
        request = urllib2.Request(self.ckan_host+"/api/rest/dataset/sec_"+str(cik))
        response = urllib2.urlopen(request)
        resp_json = json.loads(response.read())
         
        regex = re.compile(r'[1|2][0|9][0-9][0-9]')
        
        ckan_version = resp_json["version"]
        valid_version = []
        
        if len(ckan_version) > 1:
            version = set(ckan_version.split(","))
            for yr in version:
                if regex.findall(yr):
                    valid_version.append(yr)
            if year not in version:
                valid_version.append(str(year))
        else:
            valid_version.append(year)

        return ",".join(valid_version)
    
    
    def rebuildTags(self, cik, year):
        tags = []
        tags.append({'name': "SEC"})
        tags.append({'name': str(cik)})
        tags.append({'name': str(year)})
        return tags