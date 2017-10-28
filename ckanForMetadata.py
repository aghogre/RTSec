# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:36:20 2017

@author: RAVITHEJA
"""

import ckanapi
from datetime import datetime
from config import mongo_config


def insert_into_ckan(ckan_host, api_key, publisher, mongo_uri, source):

    current_date = datetime.now()

    db_name = mongo_config.get('db_name')

    ckan_ckan = ckanapi.RemoteCKAN(ckan_host, apikey=api_key)

    package_name = source.replace("_", "-")
    package_title = source.replace("_", " ")

    dict_additional_fields = {
            'Title': package_title,
            'Sourcing_Date': current_date.strftime("%B %d, %Y, %H:%M"),
            'Source': source,
            'Datastore': mongo_uri,
            'Database_Name': db_name,
            'Collection': source,
            'Description': "Financial data of " + package_title,
            }
    additional_fields = []
    for k, v in dict_additional_fields.items():
        additional_fields.append({'key': k, 'value': v})

    tags = buildTags(source)
    try:
        ckan_ckan.action.package_create(name=package_name,
                                        title=package_name,
                                        maintainer=publisher,
                                        tags=tags,
                                        extras=additional_fields,
                                        )
    except:
        ckan_ckan.action.package_update(id=package_name,
                                        title=package_name,
                                        maintainer=publisher,
                                        tags=tags,
                                        extras=additional_fields,
                                        )


def buildTags(source):
        tags = []
        tags.append({'name': source.replace("_", " ")})
        tags.append({'name': "Financial News"})
        return tags
