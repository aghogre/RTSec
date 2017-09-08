# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 13:03:13 2017

@author: RAVITHEJA
"""

import os
import json
import urllib2
import ckanapi
import re
#import requests
from datetime import datetime


class SEC_CKAN():

    def __init__(self, ckan_host, api_key):
        self.ckan_host = ckan_host
        self.api_key = api_key
        
        # Connecting to CKAN
        self.ckan_ckan = ckanapi.RemoteCKAN(ckan_host, apikey = api_key)
        
        # creating a folder to hold all cik related files, to be uploaded in ckan
        if not os.path.exists('upload'): os.makedirs('upload')

    
    def storeMetadata(self, cik, azure_urls, file_types, year):    
        # read all metadata information from 'metadata.json'
        with open('ticker_metadata.json') as json_file:    
            json_data = json_file.read() #.replace('u "','"').replace('u"','"')
            metadata_json = json.loads(json_data)
        json_file.close()
        
        metadata = [mdata for mdata in metadata_json["metadata"] if mdata["cik"] == str(cik)]
        if len(metadata) == 0:
            return
        else:
            metadata = metadata[0]
           
        # write the metadata content to file in JSON format and get its path
       # with open(os.path.join(os.path.dirname(__file__), 'upload',cik+'.json'), 'w') as ckan_file:
        #    json.dump(metadata, ckan_file)
     #   path = os.path.join(os.path.dirname(__file__), 'upload', cik+'.json')
    
        package_name = "sec_" + cik
        current_date = datetime.now().strftime("%B %d, %Y, %H:%M")
       
        # create or update the package for each artifact with latest Metadata of Azure datasets.
        if str(metadata) :
            package_title = metadata["Title"].replace('.','')       
            tags = []
       #     package = ''
            if "Tags" in metadata:
               for tag in metadata["Tags"].split(','):
                   if str(tag).strip():
                       tags.append({'name': str(tag).strip()})
            tags.append({'name': str(year)})

            multi_url_dict = {'url' + str(i + 1): url for i, url in enumerate(azure_urls)}
        
            dict_additional_fields = {
                'Source': metadata["Source"],
                'SourceType': file_types,
                'Title':package_title,
                'Sourcing_Date': current_date,
                'Container' : metadata["Container"],
                'Ticker' : metadata["Ticker"],
                'Exchange' : metadata["Exchange"],
                'Industry' : metadata["Industry"],
                'cik' : metadata["cik"],
                #'name' : metadata["Name"],
                'IRS Number' : metadata["IRS Number"],
                'Business' : metadata["Business"],
                'Incorporated' : metadata["Incorporated"],
                #'owner_org' : 'USSecurityExchangeCommission'
            }
            
            print(dict_additional_fields)
            dict_additional_fields.update(multi_url_dict)
        
            additional_fields = []
        
            for k, v in dict_additional_fields.items():
                additional_fields.append({'key': k, 'value': v})
        
            #print(additional_fields)
            try:
                print "creating package1"
                self.createPackage(package_name, package_title, year, metadata, tags, additional_fields)
            except ckanapi.ValidationError as ve:
               if (ve.error_dict['__type'] == 'Validation Error'):
                   if('name' in ve.error_dict 
                      and ve.error_dict['name'] == ['That URL is already in use.']):                       
                       try:
                           print "creating package2"
                           self.updatePackage(package_name, package_title, cik, year, metadata, tags, additional_fields)
                       except ckanapi.ValidationError as ve2:
                           if('tags' in ve2.error_dict and len(ve2.error_dict['tags'])>0):
                               print "creating package3"
                               self.updatePackageWithoutTags(package_name, package_title, cik, year, metadata, additional_fields)
                           else:
                               raise
                   elif('tags' in ve.error_dict and len(ve.error_dict['tags'])>0):
                       for e in ve.error_dict['tags']:
                           if "must be alphanumeric characters" in e:
                               try:
                                   print "creating package4"
                                   self.createPackageWithoutTags(package_name, package_title, year, metadata, additional_fields)
                               except:
                                   print "creating package5"
                                   self.updatePackageWithoutTags(package_name, package_title, cik, year, metadata, additional_fields)                                       
                   else:
                       raise
               else:
                   raise

            except:
               raise
           


    def createPackage(self, package_name, package_title, year, metadata, tags, additional_fields):
        self.ckan_ckan.action.package_create(name=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=year,
                             # license_id=metadata["License"],
                              tags=tags,
                              extras=additional_fields
                              )

        
    def createPackageWithoutTags(self, package_name, package_title, year, metadata, additional_fields):
        self.ckan_ckan.action.package_create(name=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=year,
                              extras=additional_fields
                              )


    def updatePackage(self, package_name, package_title, cik, year, metadata, tags, additional_fields):
        self.ckan_ckan.action.package_update(id=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=self.getVersions(cik, year),
                             # license_id=metadata["License"],
                              tags=tags,
                              extras=additional_fields
                              )

        
    def updatePackageWithoutTags(self, package_name, package_title, cik, year, metadata, additional_fields):
        self.ckan_ckan.action.package_update(id=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=self.getVersions(cik, year),
                              extras=additional_fields
                              )


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
    
    