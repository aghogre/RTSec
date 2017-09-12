# SEC 10-K filings
## Overview
This project sources the annual 10-K filings from SEC Edgar Data and stores to a Azure blob container by CIK (Central Index Key) while accepting year(s) as an argument. For each CIK artifact, a data catalog will be created in the CKAN Data management system. 

## Instructions
The Dockerfile has the information to build a docker image which in turn is used to build a docker container. Environment variables are defined in .env file and these values can be passed during execution time. The script accepts six variables namely AZURE ACCOUNT NAME, AZURE ACCOUNT KEY, CONTAINER, CKAN HOST, CKAN KEY AND YEARS.

Once deployed and run, the script should load the data into Azure and CKAN storage. Please verify to make sure the data is published. 



