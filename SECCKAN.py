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

    
    def storeMetadata(self, cik, azure_url, year):    
        # read all metadata information from 'metadata.json'
        with open('metadata.json') as json_file:    
            json_data = json_file.read() #.replace('u "','"').replace('u"','"')
            metadata_json = json.loads(json_data)
        json_file.close()
        
        metadata = [mdata for mdata in metadata_json["metadata"] if mdata["cik"] == str(cik)]
        if len(metadata) == 0:
            return
        else:
            metadata = metadata[0]
           
        # write the metadata content to file in JSON format and get its path
        with open(os.path.join(os.path.dirname(__file__), 'upload',cik+'.json'), 'w') as ckan_file:
            json.dump(metadata, ckan_file)
        path = os.path.join(os.path.dirname(__file__), 'upload', cik+'.json')
    
        package_name = "sec_" + cik
        
        if metadata["Created"]:
            sourcing_date = metadata["Created"]
        else:
            sourcing_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       
        # create or update the package for each artifact with latest Metadata of Azure datasets.
        if str(metadata) :
           package_title = metadata["Title"].replace('.','')       
           tags = []
           if "Tags" in metadata:
               for tag in metadata["Tags"].split(','):
                   if str(tag).strip():
                       tags.append({'name': str(tag).strip()})
           tags.append({'name': str(year)})

           update = False

           version = ''
           package = ''
           try:
               package = self.ckan_ckan.action.package_create(name=package_name, 
                                      title=package_title,
                                      notes=metadata["Description"],
                                      maintainer=metadata["Publisher"],
                                      version=year,
                                     # license_id=metadata["License"],
                                      tags=tags 
                                      )
           except ckanapi.ValidationError as ve:
               if (ve.error_dict['__type'] == 'Validation Error'):
                   if('name' in ve.error_dict and ve.error_dict['name'] == ['That URL is already in use.']):
                       request = urllib2.Request(self.ckan_host+"/api/rest/dataset/sec_"+str(cik))
                       response = urllib2.urlopen(request)
                       resp_json = json.loads(response.read())
                       version = resp_json["version"]
                       if len(version) > 1:
                           version = version+","+str(year)
                       else:
                           version = year

                       package = self.ckan_ckan.action.package_show(id=package_name)
                       if package:
                           print("PACKAGE")
                           print(package)
                           update = True
        
                       package = self.ckan_ckan.action.package_update(id=package_name, 
                                          title=package_title,
                                          notes=metadata["Description"],
                                          maintainer=metadata["Publisher"],
                                          version=version,
                                          #license_id=metadata["License"],
                                          tags=tags 
                                          )
                   elif('tags' in ve.error_dict and len(ve.error_dict['tags'])>0):
                       for e in ve.error_dict['tags']:
                           if "must be alphanumeric characters" in e:
                               if update:
                                   package = self.ckan_ckan.action.package_update(id=package_name, 
                                              title=package_title,
                                              notes=metadata["Description"],
                                              maintainer=metadata["Publisher"],
                                              version=version)                       
                               else:
                                   package = self.ckan_ckan.action.package_create(name=package_name, 
                                              title=package_title,
                                              notes=metadata["Description"],
                                              maintainer=metadata["Publisher"],
                                              version=year)                           
                                   
                   else:
                       print("111")
                       raise
               else:
                   print("222")
                   raise

           r = requests.post(self.ckan_host+'/api/action/resource_create',
                             data= {'Title':package_title,
                                     'package_id': package['id'],
                                     'name': package_title,
                                     'Azure URL': azure_url,
                                     'Source':metadata["Source"],
        #################                             'Source type':"", 
                                     'Sourcing_Date': sourcing_date,
                                     #'owner_org':owner_org,
                                     'url': 'upload'
                                   },
                             headers={'Authorization': self.api_key},
                             files=[('upload', file(path))])
           #print(r.status_code)
           if r.status_code != 200:
               print('Error while creating resource: {0}'.format(r.content))
           #else:
               #print('Created "{package_title}" package in CKAN'.format(**locals()))       

