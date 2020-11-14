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
* *etl.py* : Script to extract, transform and load data
* *DataQualityOperator.py* : ???
* *SocrataQueryOperator.py* : ???
* *SocrataQueryOperator.py* : ???

### sql queries
* *api_params.sql*: s3://udacity-dend/song_data
* *bad_rows.sql*: s3://udacity-dend/log_data
* *coordinate.sql*: s3://udacity-dend/log_data
* *create_bad_row_table.sql*: s3://udacity-dend/log_data
* *create_fact_table.sql*: s3://udacity-dend/log_data
* *create_geo_table.sql*: s3://udacity-dend/log_data
* *create_summary_table.sql*: s3://udacity-dend/log_data
fact_query.sql
insert_key.sql
location.sql
quality_check.sql
quality_check_duplicate.sql
summary.sql
total_record.sql


## Project specifications, challenges and project delivery
---

This project is similar to previous projects. The main difference is that we are using S3 as a source and destination. Data are extracted from S3, transformed with Spark and sent to S3 transformed. 

* Data transformation is done with sql queries with pyspark.sql
* Transformed data are sent to S3 following the star schema. 
* Data type are handle with JSON schema when data are read from S3

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



## ETL Process 
---

### Extract & Load

Data are extracted from Socrate API and loaded into storage bucket

### Transform

Data are trasnformed and inserted into BigQuery following Star schema 

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
