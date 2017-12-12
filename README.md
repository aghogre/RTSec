# Quandl

## Financial Data

This project is to fetch Financial data both persisted ones and live data. URLs based on Quandl codes along with the registered API Key helps in fetching the data. Data is fetched from about 195 datasets (when this document is made).
REST API request URLs of the data sources are passed using a CSV file.
Quandl API can also be used to get data dump for every request made using Quandl code, but not much updated.

API Key: It can be generated at Quandl upon creating an account at https://www.quandl.com/

## Data Fetching

Quandl facilitates 2 types of APIs:
* 1.	Time-series
  https://www.quandl.com/api/v3/datasets/{database_code}/{dataset_code}/data.{return_format} 
* 2.	Tables
  https://www.quandl.com/api/v3/datatables/{datatable_code}.{format}?<row_filter_criteria> 

JSON Response format is preferred over CSV and XML as it is suitable for MongoDB storage.
More details are available at the documentation page https://docs.quandl.com/docs

## Data Storing
Each collection is maintained for every dataset in the MongoDB. A Metadata collection helps maintain a record of what all datasets have been downloaded.
The MongoDB host URI can be maintained in the CKAN. Last updated time helps in identifying when the program was executed latest.

## Below are the list of arguments to be part of the execution.

* **Agent**

   *	`QUANDL_APIKEY`: Quandl provides an API Key to recognize the account user accessing the global REST API URL.
   *	`CKAN_HOST`: Account name or the IP address of CKAN Instance.
   *	`CKAN_API_KEY`: Authentication key of the CKAN Instance.
   *	`PUBLISHER`: Name of the person or entity that is publishing the data.
   *	`OWNER_ORG`: CKAN Organization entity.
   *	`CKAN_PRIVATE`: Dataset visibility parameter.

   *	`MONGO_URI`: The URI of the deployed MongoDB instance (default: localhost:27017)
   *	`MONGO_SSL_REQUIRED`: MongoDB clients can use TLS/SSL to encrypt connections to mongod and mongos instances.
   *	`REQUIRES_AUTH`: Specify whether the MongoDB Instance needs authentication (default: false)
   *	`MONGO_USER`: Username in case the authentication is specified true.
   *	`MONGO_PASSWORD`: Password in case the authentication is specified true.
   *	`MONGO_AUTH_SOURCE`: If authentication is required, the database which MongoDB uses as its authentication source (default: dbadmin)
   *	`MONGO_AUTH_MECHANISM`: If authentication is required, the method which MongoDB uses as authentication mechanism (default: MONGODB-CR)
   *	`MONGO_DB_NAME`: The name of the MongoDB database to which data is sourced.
   *	`MONGO_INDEX_NAME`: The field with unique values to create an index on.
   *	`MONGO_COL_NAME`: The name of the MongoDB collection within the database where data is grouped. Given 'METADATA' to create a reference of all the data that has been downloaded in separate collections. Useful for checking the duplicate entries.
   
