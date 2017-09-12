# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:59:56 2017

@author: RAVITHEJA
"""

import os

#DEFAULT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SECData'))

argument_config = {
    'azure_account_name': os.getenv('AZURE_ACCOUNT_NAME', 'randomtrees'),
    'azure_account_key': os.getenv('AZURE_ACCOUNT_KEY', 'wvNLlB2cSHhB0OFPRhIQDv+1QBJ1CnwFt+AGfQnL8rTyKTCG90t1Z+aCepe25aol6CKneJYgvHJl5gMtHON7TQ=='),
	'azure_container': os.getenv('CONTAINER','anshul'),
    'ckan_host': os.getenv('CKAN_HOST', 'http://40.71.214.191:80'),
    'ckan_key': os.getenv('CKAN_KEY', '3474fcd0-2ebc-4036-a60a-8bf77eea161f'),
    'years': os.getenv('YEARS', ['1993,1994']),
    'publisher': os.getenv('PUBLISHER', 'Random Trees')
}
