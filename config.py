"""
Created on Thu Aug 31 12:59:56 2017

@author: ANSHUL
"""
import os

argument_config = {
        'my_app_token': os.getenv('NADAC_APP_TOKEN', 'FZzIj5UDHAzJD3a0ulNsTxe37'),
        'user_id': os.getenv('USER_ID', 'anshulghogre@gmail.com'),
        'password': os.getenv('PASSWORD', 'Indore1#'),
        'ckan_host': os.getenv('CKAN_HOST', 'http://40.71.214.191:80'),
        'api_key': os.getenv('CKAN_API_KEY', '8613bf84-7b92-40f3-aa08-056c5f65421b'),
        'publisher': os.getenv('PUBLISHER', 'randomtrees'),
        'owner_org': os.getenv('OWNER_ORG', 'securities-exchange-commission'),
        'ckan_private': os.getenv('CKAN_PRIVATE', 'False')
         }


mongo_config = {
    'requires_auth': os.getenv('REQUIRES_AUTH', 'false'),
    'mongo_uri': os.getenv('MONGO_URI', 'localhost:27017'),
    'mongo_username': os.getenv('MONGO_USER', ''),
    'mongo_password': os.getenv('MONGO_PASSWORD', ''),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'dbadmin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'MONGODB-CR'),
    'db_name': os.getenv('MONGO_DB_NAME', 'NADAC1'),
    'col_name': os.getenv('MONGO_COL_NAME', 'testing5'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'csrt'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', False)
}
