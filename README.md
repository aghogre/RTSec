# Drugs.com

## Drugs.com- Contains the details of all drugs.

This project is to fetch drugs detail from drugs.com. By using scrapy, data are getting fetched and stored into Mongo DB. Data contains all available categories of each drug(overview, side effect, dosage, review, interaction etc)

Used beautifulSoup for scrapping the data from website, as no API and other way found to get data.

## Data Storing

A collection is maintained for all data in the MongoDB. A Metadata collection helps maintain a record of what all data have been downloaded. The MongoDB host URI can be maintained in the CKAN along with License details of datasets.

Below are the list of arguments to be part of the execution.

## Agent

* `CKAN_HOST`: Account name or the IP address of CKAN Instance.

* `CKAN_API_KEY`: Authentication key of the CKAN Instance.

* `PUBLISHER`: Name of the person or entity that is publishing the data.

* `OWNER_ORG`: CKAN Organization entity.

* `CKAN_PRIVATE`: Dataset visibility parameter.

* `MONGO_URI`: The URI of the deployed MongoDB instance (default: localhost:27017)

* `MONGO_SSL_REQUIRED`: MongoDB clients can use TLS/SSL to encrypt connections to mongod and mongos instances.

* `REQUIRES_AUTH`: Specify whether the MongoDB Instance needs authentication (default: false)

* `MONGO_USER`: Username in case the authentication is specified true.

* `MONGO_PASSWORD`: Password in case the authentication is specified true.

* `MONGO_AUTH_SOURCE`: If authentication is required, the database which MongoDB uses as its authentication source (default: dbadmin)

* `MONGO_AUTH_MECHANISM`: If authentication is required, the method which MongoDB uses as authentication mechanism (default: MONGODB-CR)

* `MONGO_DB_NAME`: The name of the MongoDB database to which data is sourced.

* `MONGO_INDEX_NAME`: The field with unique values to create an index on.

* `MONGO_COL_NAME`: The name of the MongoDB collection within the database where data is grouped. Given 'METADATA' to create a reference of all the data that has been downloaded in separate collections. Useful for checking the duplicate entries.
