# -*- coding: utf-8 -*-

import os

datagov_domains = ["energy", "finance", "health", "local"]

argument_config = {
    'domains': os.getenv('DOMAINS', datagov_domains),
}


mongo_config = {
   'mongo_uri': os.getenv('MONGO_URI', 'cluster0-shard-00-00-kjzdb.mongodb.net:27017'),
    'ssl_required': os.getenv('MONGO_SSL_REQUIRED', 'true'),
    'requires_auth': os.getenv('REQUIRES_AUTH', 'true'),
    'mongo_username': os.getenv('MONGO_USER', 'admin'),
    'mongo_password': os.getenv('MONGO_PASSWORD', 'R@ndomTrees123'),
    'mongo_auth_source': os.getenv('MONGO_AUTH_SOURCE', 'admin'),
    'mongo_auth_mechanism': os.getenv('MONGO_AUTH_MECHANISM', 'SCRAM-SHA-1'),
    'db_name': os.getenv('MONGO_DB_NAME', 'datagov_health'),
    'mongo_index_name': os.getenv('MONGO_INDEX_NAME', 'csrtc'),
    'meta_colln_name': os.getenv('METADATA_COLLN_NAME', 'metadata'),
    'datasets_colln_name': os.getenv('DATASETS_COLLN_NAME', 'datasets'),
}
