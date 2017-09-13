# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:59:56 2017

@author: RAVITHEJA
"""

import os

argument_config = {
    'azure_account_name': os.getenv('AZURE_ACCOUNT_NAME', ''),
    'azure_account_key': os.getenv('AZURE_ACCOUNT_KEY', ''),
    'azure_container': os.getenv('CONTAINER', ''),
    'ckan_host': os.getenv('CKAN_HOST', ''),
    'ckan_key': os.getenv('CKAN_KEY', ''),
    'years': os.getenv('YEARS', ''),
    'publisher': os.getenv('PUBLISHER', '')
}
