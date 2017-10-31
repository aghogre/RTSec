# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:59:56 2017

@author: RAVITHEJA
"""

import os

argument_config = {
    'azure_account_name': os.getenv('AZURE_ACCOUNT_NAME', 'randomtrees'),
    'azure_account_key': os.getenv('AZURE_ACCOUNT_KEY', 'wvNLlB2cSHhB0OFPRhIQDv+1QBJ1CnwFt+AGfQnL8rTyKTCG90t1Z+aCepe25aol6CKneJYgvHJl5gMtHON7TQ=='),
    'azure_container': os.getenv('CONTAINER', 'rrrr'),
    'ckan_host': os.getenv('CKAN_HOST', 'http://40.71.214.191:80'),
    'ckan_key': os.getenv('CKAN_KEY', '8613bf84-7b92-40f3-aa08-056c5f65421b'),
    'years': os.getenv('YEARS', '1993'),
    'publisher': os.getenv('PUBLISHER', 'randomtrees'),
    'owner_org': os.getenv('OWNER_ORGANIZATION', 'randomtrees')
}
