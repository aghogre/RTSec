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
    'years': os.getenv('YEARS', '1995'),
    'publisher': os.getenv('PUBLISHER', 'randomtrees'),
    'owner_org': os.getenv('OWNER_ORGANIZATION', 'securities-exchange-commission')
}

mongo_config = {
    'requires_auth': os.getenv('REQUIRES_AUTH', 'false'),
    'mongo_uri': os.getenv('MONGO_URI', 'localhost:27017'),
    'mongo_username': os.getenv('MONGO_USER', ''),
    'mongo_password': os.getenv('MONGO_PASSWORD', ''),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'dbadmin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'MONGODB-CR'),
    'db_name': os.getenv('MONGO_DB_NAME', 'SEC'),
    'col_name': os.getenv('MONGO_COL_NAME', 'SEC'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'seccrt'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', False)
}
