# SEC 10-K filings
## Overview
This project sources the annual 10-K filings from SEC Edgar Data and stores to a Azure blob container by CIK (Central Index Key) while accepting year(s) as an argument. For each CIK artifact, a data catalog will be created in the CKAN Data management system. 

## Instructions
The Dockerfile has the information to build a docker image which in turn is used to build a docker container. Environment variables are defined in .env file and these values can be passed during deployment. Below are the list of environment variables and their function.

* `AZURE ACCOUNT NAME`: The account name or the IP address of Azure Cloud Storage
* `AZURE ACCOUNT KEY`: Authentication key of the Azure Cloud Storage
* `CONTAINER`: Name of the Azure blob container where the data is stored
* `CKAN HOST`: Account name or the IP address of CKAN Instance
* `CKAN KEY`: Authentication key of the CKAN Instance
* `YEARS`: Years for which the SEC 10-K data need to be sourced. This can be a single year or a comma separated years, (e.g., '2012' or '2000,2008,2014')
* `PUBLISHER`: Name of the person or entity that is publishing the data
* `OWNER_ORGANIZATION`: Organization that owns this dataset. For ex: 'Securities-Exchange-Commission' would be an example for the organization in this case.

Once deployed and run, the script should load the data into Azure and create a data catalog in CKAN. Please verify to make sure the data is published. 



