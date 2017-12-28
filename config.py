"""
Created on Thu Aug 31 12:59:56 2017

@author: ANSHUL
"""
import os

argument_config = {
        'ckan_host': os.getenv('CKAN_HOST', 'http://40.71.214.191:80'),
        'api_key': os.getenv('CKAN_API_KEY', '3474fcd0-2ebc-4036-a60a-8bf77eea161f'),
        'publisher': os.getenv('PUBLISHER', 'random trees'),
        'owner_org': os.getenv('OWNER_ORG', 'securities-exchange-commission'),
        'ckan_private': os.getenv('CKAN_PRIVATE', False)
         }


mongo_config = {
    'requires_auth': os.getenv('REQUIRES_AUTH', 'false'),
    'mongo_uri': os.getenv('MONGO_URI', 'localhost:27017'),
    'mongo_username': os.getenv('MONGO_USER', ''),
    'mongo_password': os.getenv('MONGO_PASSWORD', ''),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'dbadmin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'MONGODB-CR'),
    'db_name': os.getenv('MONGO_DB_NAME', 'Drugs2'),
    'col_name': os.getenv('MONGO_COL_NAME', 'drug'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'csrt'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', False)
}
