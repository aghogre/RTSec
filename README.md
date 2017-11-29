# Twitter Consumer Streaming
## Overview
This project consumes the specified (default: twitterhandle) topic from the Kafka broker through Kafka consumer and stores into MongoDB. 

## Instructions

The Dockerfile has the information to build a docker image which in turn is used to build a docker container. Environment variables are defined in .env file and these values can be passed during deployment. 

Below are the list of environment variables to be part of the execution.

* **Agent**

    * `KAFKA_BROKER_URI`: URI (including host name and port number, if applicable), where Kafka server is running.
    
    * `KAFKA_TOPIC_NAME`: A Topic to be used by Kafka Producer to write the message and Kafka Consumer to read from the same.


* **MongoDB**

    * `REQUIRES_AUTH`: Specify whether the MongoDB Instance needs authentication (default: `false`)
    
    * `MONGO_URI`: The URI of the deployed MongoDB instance (default: `localhost:27017`)
    
    * `MONGO_USER`: Username in case the authentication is specified `true`
    
    * `MONGO_PASSWORD`: Password in case the authentication is specified `true`
    
    * `MONGO_AUTH_SOURCE`: If authentication is required, the database which MongoDB uses as its authentication source (default: `dbadmin`)
    
    * `MONGO_AUTH_MECHANISM`: If authentication is required, the method which 
    MongoDB uses as authentication mechanism (default: `MONGODB-CR`)
    
    * `MONGO_DB_NAME`: The name of the MongoDB database to which data is sourced 
    
    * `MONGO_COL_NAME`: The name of the MongoDB collection within the database where data is grouped
    
    * `MONGO_INDEX_NAME`: The field with unique values to create an index on
    
    * `MONGO_SSL_REQUIRED`: MongoDB clients can use TLS/SSL to encrypt connections to mongod and mongos instances.


Once deployed and run, the script should consume messages from the broker and publish to MongoDB. 

