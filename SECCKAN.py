# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 13:03:13 2017

@author: RAVITHEJA
"""

import os
import json
import urllib2
import ckanapi
import requests
from datetime import datetime


class SEC_CKAN():

    def __init__(self, ckan_host, api_key):
        # Connecting to CKAN
        self.ckan_ckan = ckanapi.RemoteCKAN(ckan_host, apikey = api_key)
        self.ckan_host = ckan_host
        self.api_key = api_key
    
        if not os.path.exists('upload'):
            os.makedirs('upload')

    
    def storeMetadata(self, cik, azure_url, file_types, year):    
        # read all metadata information from 'metadata.json'
        with open('metadata.json') as json_file:    
            json_data = json_file.read() #.replace('u "','"').replace('u"','"')
            metadata_json = json.loads(json_data)
        json_file.close()
        
        metadata = [mdata for mdata in metadata_json if mdata["cik"] == str(cik)]
        if len(metadata) == 0:
            return
        else:
            metadata = metadata[0]
           
        # write the metadata content to file in JSON format and get its path
        with open(os.path.join(os.path.dirname(__file__), 'upload',cik+'.json'), 'w') as ckan_file:
            json.dump(metadata, ckan_file)
        path = os.path.join(os.path.dirname(__file__), 'upload', cik+'.json')
    
        package_name = "sec_" + cik
        current_date = datetime.now().strftime("%B %d, %Y, %H:%M")
       
        # create or update the package for each artifact with latest Metadata of Azure datasets.
        if str(metadata) :
           package_title = metadata["Title"].replace('.','')       
           tags = []
           package = ''
           if "Tags" in metadata:
               for tag in metadata["Tags"].split(','):
                   if str(tag).strip():
                       tags.append({'name': str(tag).strip()})
           tags.append({'name': str(year)})

           try:
               self.createPackage(package_name, package_title, year, metadata, tags)
           except ckanapi.ValidationError as ve:
               if (ve.error_dict['__type'] == 'Validation Error'):
                   if('name' in ve.error_dict 
                      and ve.error_dict['name'] == ['That URL is already in use.']):                       
                       try:
                           self.updatePackage(package_name, package_title, cik, year, metadata, tags)
                       except ckanapi.ValidationError as ve2:
                           if('tags' in ve2.error_dict and len(ve2.error_dict['tags'])>0):
                               self.updatePackageWithoutTags(package_name, package_title, cik, year, metadata)
                           else:
                               pass                               
                   elif('tags' in ve.error_dict and len(ve.error_dict['tags'])>0):
                       for e in ve.error_dict['tags']:
                           if "must be alphanumeric characters" in e:
                               try:
                                   self.createPackageWithoutTags(package_name, package_title, year, metadata)
                               except:
                                   self.updatePackageWithoutTags(package_name, package_title, cik, year, metadata)                                       
                   else:
                       pass
               else:
                   pass
           package = ''
           try:
               package = self.ckan_ckan.action.package_show(id=package_name)
               source_type = [type for type in file_types]
               r = requests.post(self.ckan_host+'/api/action/resource_create',
                             data= {'Title':package_title,
                                    'package_id': package['id'],
                                    'name': package_title,
                                    'Azure URL': azure_url,
                                    'Source': metadata["Source"],
                                    'Source type': source_type, 
                                    'Sourcing_Date': current_date,
                                    'Container' : metadata["Container"],
                                    'Ticker' : metadata["Ticker"],
                                    'Exchange' : metadata["Exchange"],
                                    'Industry' : metadata["Industry"],
                                    'cik' : metadata["cik"],
                                    'Name' : metadata["Name"],
                                    'IRS Number' : metadata["IRS Number"],
                                    'Business' : metadata["Business"],
                                    'Incorporated' : metadata["Incorporated"],
                                     #'owner_org':owner_org,
                                     'url': 'upload'
                                   },
                             headers={'Authorization': self.api_key},
                             files=[('upload', file(path))])
               if r.status_code != 200:
                   print('Error while creating resource: {0}'.format(r.content))
               #else:
                   #print('Created "{package_title}" package in CKAN'.format(**locals()))       
           except:
               pass
           


    def createPackage(self, package_name, package_title, year, metadata, tags):
        self.ckan_ckan.action.package_create(name=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=year,
                             # license_id=metadata["License"],
                              tags=tags 
                              )

        
    def createPackageWithoutTags(self, package_name, package_title, year, metadata):
        self.ckan_ckan.action.package_create(name=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=year
                              )


    def updatePackage(self, package_name, package_title, cik, year, metadata, tags):
        self.ckan_ckan.action.package_update(id=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=self.getVersions(cik, year),
                             # license_id=metadata["License"],
                              tags=tags 
                              )

        
    def updatePackageWithoutTags(self, package_name, package_title, cik, year, metadata):
        self.ckan_ckan.action.package_update(id=package_name, 
                              title=package_title,
                              notes=metadata["Description"],
                              maintainer=metadata["Publisher"],
                              version=self.getVersions(cik, year)
                              )


    def getVersions(self, cik, year):
        request = urllib2.Request(self.ckan_host+"/api/rest/dataset/sec_"+str(cik))
        response = urllib2.urlopen(request)
        resp_json = json.loads(response.read())
        version = resp_json["version"]
        if len(version) > 1:
            version = version+","+str(year)
        else:
            version = year
