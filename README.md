# Data Engineering Capstone Project Write Up
---

## Project Summary
---

The goal of this project is to create an ETL pipeline to gather in one data set all the the yellow taxi trip record provided by the NYC Taxi and Limousine Commission (TLC). 
This represent 10 years of data, billions of rows, multiple data models. This data set is growing every month as TLC Trip Record Data are updated on regular basis. 
This data set could support analysis on NYC Yellow taxi cab over the last ten years such as price evolution, evolution of pick-up,drop-off popular area, evolution of timing etc...


## Data Sources
---

The data are available from NYC open data platform and from NYC taxi and limousine Comission
https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page From the taxi and limousine data are access directly from aws  from a NYC open dat aplatform an API is available through socrata data 
I chose to work with the socrata API has it gave me more flexibility 

### Tables:
| Data Set Name | Public Page | API endpoint | Rows | Columns
| ------- | ---------- | ----------- | ---- | ------- |
| 2018 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq | https://data.cityofnewyork.us/resource/t29m-gskq.json | 112M | 17
| 2017 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2017-Yellow-Taxi-Trip-Data/biws-g3hs | https://data.cityofnewyork.us/resource/biws-g3hs.json | 112M | 17
| 2016 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2016-Yellow-Taxi-Trip-Data/k67s-dv2t | https://data.cityofnewyork.us/resource/uacg-pexx.json | 112M | 17
| 2015 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2015-Yellow-Taxi-Trip-Data/ba8s-jw6u | https://data.cityofnewyork.us/resource/2yzn-sicd.json | 112M | 17
| 2014 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2013-Yellow-Taxi-Trip-Data/7rnv-m532 | https://data.cityofnewyork.us/resource/gkne-dk5s.json | 112M | 17
| 2013 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq | https://data.cityofnewyork.us/resource/t7ny-aygi.json | 112M | 17
| 2012 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2012-Yellow-Taxi-Trip-Data/fd5y-xikb | https://data.cityofnewyork.us/resource/kerk-3eby.json | 112M | 17
| 2011 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2011-Yellow-Taxi-Trip-Data/jr6k-xwua | https://data.cityofnewyork.us/resource/uwyp-dntv.json | 112M | 17
| 2009 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2009-Yellow-Taxi-Trip-Data/f9tw-8p66 | https://data.cityofnewyork.us/resource/f9tw-8p66.json | 112M | 17


## Data Sources Description 
---

There was three main challenges working on this project and with this data sources:

- the amount of data was huge. The socrata API instalble and I don't wanted to rely too much on physical memory. so i wanted to cut un small chuck of data with mean to have API call everyday
- Shcema wasn't well described and was changing over time. so I had to find a way to reliable ELT this data 
- As Schema wasn't realiable, it was particularly difficult to translate the geolocalisation point. 

### 2018 Yellow Taxi Trip Data detailed

The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song.

Here is an example of what a single song file looks like:	
	
`
{
  "vendorid":2, //Number
  "tpep_pickup_datetime":"2084 Nov 04 12:32:24 PM", //Date & Time
  "tpep_dropoff_datetime":"2084 Nov 04 12:47:41 PM",	 //Date & Time
  "passenger_count":1,	 //Number
  "trip_distance":1.14,	 //Number
  "RatecodeID":1,	//Number
  "store_and_fwd_flag":"N",	//Plain Text
  "PULocationID	":"238", //Plain Text
  "DOLocationID":"236", // Plain Text
  "payment_type":2, //Number
  "fare_amount":10, //Number
  "extra":0, //Number
  "mta_tax":0.5, //Number
  "tip_amount":0, //Number
  "tolls_amount":0, //Number
  "improvement_surcharge":0.3, //Number
  "total_amount":10.8 //Number
}
`

Each log file contains multiple events.

## Repository overview
---

### files:
* *elt.py* : extract, transform, load dag 
* *SocrataToGCSOperator.py* : Custom operator to query Socrata API and pass result to Google Cloud Storage.
* *SocrataQueryOperator.py* : Custom operator to query Socrata API with customised query.
* *DataQualityOperator.py* : Custom oerator to run queries and test data quality.

### sql queries
* *api_params.sql*: Templated query to filter desired output from Socrata API 
* *bad_rows.sql*: Templated query to pass bad rows from raw data table to bad row table. 
* *coordinate.sql*: Templated query to join geopoint data from raw data table with NYC taxi zones borough from Public NYC taxi zones table
* *create_bad_row_table.sql*: create bad row table 
* *create_fact_table.sql*: create fact table
* *create_geo_table.sql*: create geo table
* *create_summary_table.sql*: create summmary table
* *fact_query.sql*: Templated query to insert data from raw table into fact table
* *insert_key.sql*: Templated query to insert surrogate_keys into raw data table
* *location.sql*: Templated query to join LocationID data from raw data table with NYC taxi zones borough from Public NYC taxi zones table
* *quality_check.sql*: Templated query to count number of rows
* *quality_check_duplicate.sql*: Templated query to check for duplicate
* *summary.sql*: Templated query to insert summary data ready for analysis. 
* *total_record.sql*: Template query to count the number of rows from API call


## Project specifications
---

Data are loaded retroactively for a defined period per day and per pagination as csv file into Google Cloud Storage. From there csv file are imported into a staging environement where data raw format is conserved. Data that fit the project goal are passed into a production table 

* Socrata API call is paginated, each pagination result is passed as a seperate file in Google Cloud Storage.
* Socrata API call is filtered using SQL.
* Data transformation is done with sql queries on BigQuery.
* Transformed data are sent to a production table following the star schema. 
* Data type are handle with predefined JSON schema to enfore consistency. 
* Data Quality test and check ensure that every raw from the API call are passed in staging. 

## Project rationale
---

### Airflow

Airflow was the best option to move such big amount of data. Some core concept helped us to make our choice:

Load data incrementally: As the NYC Yellow taxi cab entire data set is pretty big and spread out over 10 years of data I need a way to break it down into small chunk and load data incrementally. 

Process historic data: Airflow is specifficaly designed historical data by giving the possibility of back-filling data way back to the start date. 

Partition ingested data: Building the pipeline with Airflow was easy to partitioned data by date allowing us to more easily audit ETL process and optimise query performances. 

Enforce deterministic properties: A function is said to be deterministic if for a given input, the output produced is always exactly the same. Examples of cases where behavior of a function can be non-deterministic:

Execute conditionally: As data schema was complexe to handle (different for one year of data to another year) BranchPythonOperator allowed us to run different query with multiple path based on different data schema. 

Rest data between tasks: This concept allowed us to build a reliable and tracable data piple. Data are stored at each step of their transformation. If anything is wrong, issues can be traced back throught log and table inspection. 

### GCP

I've experienced multiple cloud platform environement (Google, Amazon, Microsoft). For this project they all seems to be identical. I chose to work with the environement with which I had most familiarity. 

## Star Schema
---

### Description

*section copied from previous project data modeling* 

The database schema used in this project is the Star Schema. One table (fact table) contains all the measures of each events. 4 dimension tables contain dimension of measures in the Fact table. Each dimension table is linked to the fact table with their PRIMARY KEY.


### Advantage of Star Schema

Here are the main benefits of Star Schema:
* Simplified Queries - join logic are simpler with Star Schema.
* Query Performances - Read-only is easier as compared to normalized schemas
* Simplified business reporting logic 
* Fast aggregations 

### Detailed Structure

![Keywords-Ads-Landing pages flow](schema.png)

#### Fact Table

##### songplays

records in log data associated with song plays i.e. records with page NextSong

| Columns      | Constraints   | Type  | 
| ------------ | ------------- | ----- |
| surrogate_keys | PRIMARY KEY NOT NULL | SERIAL
| partitioned_key | REFERENCES time(start_time) | TIMESTAMP
| pickup_datetime | REFERENCES users(user_id) | VARCHAR
| passenger_count | no constraints | VARCHAR
| trip_distance | REFERENCES songs(song_id) | VARCHAR
| payment_type | REFERENCES artists(artist_id) | VARCHAR
| total_amount | no constraints | INT

#### Dimension Tables

##### users

Users in the app

Columns      | Constraints   | Type  | 
------------ | ------------- | ----- |
surrogate_keys | PRIMARY KEY NOT NULL | VARCHAR
pickup_zone | no constraints | VARCHAR
pickup_borough | no constraints | VARCHAR
dropoff_zone | no constraints | VARCHAR
dropoff_borough | no constraints | VARCHAR



## ELT Process 
---

### Extract

Data are extracted from Socrata API and loaded into Google Cloud Storage bucket as csv file. all the data are stored into a root folder named "data". Inside this folder data are loaded following the folder structure Year / Month / Day. In the day folder each data per pagination (API call) 

### Load

Raw data are loading into a staging environement. The staging table is flexible allowing any data schema change and update. A surrogate key is added. 

### Transform

Data from raw table are selected to fit a common schema in a production environement. Geopoint data and locationID are transformed to bourough to fit common language. 


## How to
---

cf. run airflow

## Ressources
---

* [Markdown guide](https://www.markdownguide.org/basic-syntax/)
* [Project specifications](https://review.udacity.com/#!/rubrics/2501/view)

Step 1: Scope the Project and Gather Data

Since the scope of the project will be highly dependent on the data, these two things happen simultaneously. In this step, you’ll:

Identify and gather the data you'll be using for your project (at least two sources and more than 1 million rows). See Project Resources for ideas of what data you can use.
Explain what end use cases you'd like to prepare the data for (e.g., analytics table, app back-end, source-of-truth database, etc.)

Step 2: Explore and Assess the Data

Explore the data to identify data quality issues, like missing values, duplicate data, etc.
Document steps necessary to clean the data

Step 3: Define the Data Model

Map out the conceptual data model and explain why you chose that model
List the steps necessary to pipeline the data into the chosen data model

Step 4: Run ETL to Model the Data

Create the data pipelines and the data model
Include a data dictionary
Run data quality checks to ensure the pipeline ran as expected
Integrity constraints on the relational database (e.g., unique key, data type, etc.)
Unit tests for the scripts to ensure they are doing the right thing
Source/count checks to ensure completeness

Step 5: Complete Project Write Up

What's the goal? What queries will you want to run? How would Spark or Airflow be incorporated? Why did you choose the model you chose?
Clearly state the rationale for the choice of tools and technologies for the project.
Document the steps of the process.
Propose how often the data should be updated and why.
Post your write-up and final data model in a GitHub repo.
Include a description of how you would approach the problem differently under the following scenarios:
If the data was increased by 100x.
If the pipelines were run on a daily basis by 7am.
If the database needed to be accessed by 100+ people.
