# Twitter Producer Streaming
## Overview
This project streams the Twitter data for the handles mentioned under the config file using Twitter's Live Streaming API. Kafka Producer writes the streamed tweets to Kafka topics in JSON format. Kafka Consumer consumes the tweets as is and passes them to store in MongoDB.

## Instructions
An application has to be created in apps.twitter.com to get our application recognised by Twitter. 
With the help of Consumer/API Key and Secret, provided as part of the created App, authentication will be possible. 
Valid Access Token and Token Secret provides access to the application without virtually loging into the Twitter account.

The Dockerfile has the information to build a docker image which in turn is used to build a docker container. Environment variables are defined in .env file and these values can be passed during deployment. 

Below are the list of arguments to be part of the execution.

* **Agent**

  * `CONSUMER_KEY`: Twitter consumer key to recognise the source.
  * `CONSUMER_SECRET`: Twitter consumer secret authenticates the source application user.
  * `ACCESS_TOKEN`: Twitter access token replaces the user access for OAuth.
  * `ACCESS_TOKEN_SECRET`: Twitter access token secret authenticates without password, using OAuth.
  * `TWITTER_HASHTAGS`: Twitter handles whose data needs to be streamed
  * `KAFKA_BROKER_URI`: URI (including host name and port number, if applicable), where Kafka server is running.
  * `KAFKA_TOPIC_NAME`: A Topic to be used by Kafka Producer to write the message and Kafka Consumer to read from the same.

## Note:
* Twitter Account handles are included in the config file as a Dictionary-key:Value pair (Key- HandleNames, Value-Userids). For any updates in the Twitter Accounts/Hashtags to be modified at the same location ('HASHTAGS' list in the config.py). To get these changes reflected, Streaming program has to be recompiled and re-run.

Once deployed and run, the script should stream the tweets and data is to be published in MongoDB. 

