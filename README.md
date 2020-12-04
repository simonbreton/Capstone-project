# Data Engineering Capstone Project Write Up
---

## Project Summary
---

The goal of this project is to create an ETL pipeline to build a single source-of-truth database with all the the yellow taxi trip record provided by the NYC Taxi and Limousine Commission (TLC). This represent 10 years of data, billions of rows, multiple data models. This data set is growing every month as TLC Trip Record Data are updated on regular basis. Only data available across all these years of data are available in this single source-of-truth database. The production data is composed of two main tables; a fact table and a dimension table containing pick-up and drop-off geograpgical zone.

## Data Sources
---

### Main Data Source Description 

Yellow taxi trip record are accessible from multiple sources. For this project I chose to access them from The Socrata Open Data API (SODA). I chose SODA especially because it allowed me to break down this data in small chunck with a lot of flexibility thanks to SoQL statements that are similar to clauses in SQL statements.

#### Detailed Main Data Source Tables:
| Data Set Name | Public Page | API endpoint | Rows | Columns
| ------- | ---------- | ----------- | ---- | ------- |
| 2020 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2020-Yellow-Taxi-Trip-Data-January-June-/kxp8-n2sj | https://data.cityofnewyork.us/resource/kxp8-n2sj.json | 16.8M | 18
2019 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2019-Yellow-Taxi-Trip-Data/2upf-qytp | https://data.cityofnewyork.us/resource/2upf-qytp.json | 84.4M | 18
| 2018 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq | https://data.cityofnewyork.us/resource/t29m-gskq.json | 112M | 17
| 2017 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2017-Yellow-Taxi-Trip-Data/biws-g3hs | https://data.cityofnewyork.us/resource/biws-g3hs.json | 113M | 17
| 2016 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2016-Yellow-Taxi-Trip-Data/k67s-dv2t | https://data.cityofnewyork.us/resource/uacg-pexx.json | 131M | 17
| 2015 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2015-Yellow-Taxi-Trip-Data/ba8s-jw6u | https://data.cityofnewyork.us/resource/2yzn-sicd.json | 146M | 17
| 2014 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2014-Yellow-Taxi-Trip-Data/gn7m-em8n | https://data.cityofnewyork.us/resource/gkne-dk5s.json | 165M | 17
| 2013 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2013-Yellow-Taxi-Trip-Data/7rnv-m532 | https://data.cityofnewyork.us/resource/t7ny-aygi.json | 173M | 17
| 2012 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2012-Yellow-Taxi-Trip-Data/fd5y-xikb | https://data.cityofnewyork.us/resource/kerk-3eby.json | 166M | 17
| 2011 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2011-Yellow-Taxi-Trip-Data/jr6k-xwua | https://data.cityofnewyork.us/resource/uwyp-dntv.json | 135M | 20
| 2009 Yellow Taxi Trip Data  | https://data.cityofnewyork.us/Transportation/2009-Yellow-Taxi-Trip-Data/f9tw-8p66 | https://data.cityofnewyork.us/resource/f9tw-8p66.json | 171M | 20


#### 2018 Yellow Taxi Trip detailed

Here is an example of what a single trip looks like:	

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

### Additional Data Source

#### New York Taxi Zones data set

I used this small data set to unify Pickup and Dropoff Area accross all the trips recorded. This data set allowed me to match pickup and dropoff depending on when location id or geo point where available.

#### Data set description

| Columns |
| ------- |
| OBJECTID  | 
| Shape_Leng  | 
| the_geom |
| Shape_Area |
| zone |
| LocationID |
| borough |

#### Detailed row description

`
{
  "OBJECTID":1, //INTEGER
  "Shape_Leng":0.116357453189, //FLOAT
  "the_geom":"MULTIPOLYGON (((-74.18445299999996 40.694995999999904, -74.18448899999999 40.69509499999987, -74.18449799999996 40.69518499999987, -74.18438099999997 40.69587799999989, -74.18428199999994 40.6962109999999, -74.18402099999997 40.697074999999884, -74.18391299999996 40.69750699999986, -74.18375099999997 40.69779499999988, -74.18363399999998 40.6983259999999, -74.18356199999994 40.698451999999875, -74.18354399999998 40.69855999999988, -74.18350799999996 40.69870399999992, -74.18327399999998 40.70008999999988, -74.18315699999994 40.701214999999884, -74.18316599999997 40.702384999999886, -74.18313899999998 40.7026279999999, -74.18309399999998 40.7028529999999, -74.18299499999995 40.70315899999985, -74.18284199999994 40.70346499999989, -74.18264399999998 40.70373499999988, -74.18242799999996 40.70395099999992, -74.18220299999996 40.704139999999896, -74.18203199999994 40.70425699999987, -74.18180699999994 40.7043919999999, -74.18157299999996 40.70449999999988, -74.18132099999997 40.70460799999991, -74.18080799999996 …",	 //STRING
  "Shape_Area":0.0007823067885,	 //FLOAT
  "zone":"Newark Airport", //STRING
  "LocationID":1,	//INTEGER
  "borough":"EWR" //STRING
}
`

## Data Sources Challenges
---

There was one main challenge related to the data source. Data Schema isn't well documented across the year and is changing over time. Some columns were renamed, some columns were deleted or added fron one year to another. I wanted to keep the integrety of the data set as long as possible in my ETL process. The staging is flexiblable enough to ingest data without defined schema and this allow to handle data schema modification.

## Repository overview
---

### files:
* *elt.py* : extract, transform, load dag 
* *SocrataToGCSOperator.py* : Custom operator to query Socrata API and pass result to Google Cloud Storage.
* *SocrataQueryOperator.py* : Custom operator to query Socrata API with customised query.
* *DataQualityOperator.py* : Custom operator to run queries and test data quality.

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

Data are loaded retroactively ("backfilled") on daily basis per pagination as csv file into Google Cloud Storage. From there, csv files are imported into a staging environement in Big Query where raw data format (and schema) is conserved. From the staging table, columns consistent enough over time to build a single source-of-truth database are passed into a production fact table (in BigQuery too). In the meantime, geo data point and location ID (depending on the data set schema) are tranformed into Zone and passed into a production dimension table.

* Socrata API request is paginated. Each pagination result is passed as a seperate csv file in Google Cloud Storage.
* Socrata API request is filtered using SoQL.
* Data transformation is done with sql queries on BigQuery.
* Transformed data are sent to a production table following a model that helped me to more easily build a single source-of-truth database. 
* Data type are handle with predefined JSON schema to enfore consistency. 
* Data Quality test and check ensure that every raw from the API call are passed in staging. 

## Project rationale
---

### Airflow

Airflow was the best option to move such big amount of data. Some core concept helped me to better approache this project:

**Load data incrementally**: As the NYC Yellow taxi cab entire data set is pretty big and spread out over 10 years of data I need a way to break it down into small chunk and load data incrementally. 

**Process historic data**: Airflow is specificaly designed to process historical data by giving the possibility of back-filling data way back to the start date. 

**Partition ingested data**: Building the pipeline with Airflow was easy to partitioned data by date allowing me to more easily audit ETL process and optimise query performances. 

**Execute conditionally**: As data schema was complexe to handle (different for one year of data to another year) BranchPythonOperator allowed me to run different query with multiple path based on different data schema. 

**Rest data between tasks**: This concept allowed me to build a reliable and tracable data pipeline. Data are stored at each step of their transformation. If anything is wrong, issues can be traced back throught log and table inspection. 

### GCP

I've experienced multiple cloud platform environement (Google, Amazon, Microsoft). I chose to work with the environement with which I had most familiarity. 

## Data model
---

### Description

The database schema used in this project is a simple Star Schema with one fact table and a dimenson table. Each row is each table is linked with a surrogate key generated in the staging environement. The fact and the dimension table are feed from the staging table. The dimension table also contains data from the additiona data source.

### Advantage of Star Schema

Here are the main benefits of Star Schema:
* Simplified Queries - join logic are simpler with Star Schema.
* Query Performances - Read-only is easier as compared to normalized schemas
* Simplified business reporting logic 
* Fast aggregations 

### Detailed Structure

![Keywords-Ads-Landing pages flow](schema.png)

#### Fact Table

| Columns      | Constraints   | Type  | 
| ------------ | ------------- | ----- |
| surrogate_keys | PRIMARY KEY NOT NULL | SERIAL
| partitioned_key | no constraints | TIMESTAMP
| pickup_datetime | no constraints | VARCHAR
| passenger_count | no constraints | VARCHAR
| trip_distance | no constraints | VARCHAR
| payment_type | no constraints | VARCHAR
| total_amount | no constraints | INT

#### Dimension Table

Columns      | Constraints   | Type  | 
------------ | ------------- | ----- |
surrogate_keys | PRIMARY KEY NOT NULL | SERIAL
pickup_zone | no constraints | VARCHAR
pickup_borough | no constraints | VARCHAR
dropoff_zone | no constraints | VARCHAR
dropoff_borough | no constraints | VARCHAR


## ELT Process 
---

### Extract

Data are extracted from Socrata API and loaded into Google Cloud Storage bucket as csv file. All the data are stored into a root folder named "data". Inside this folder data are loaded following the folder structure Year / Month / Day.

### Load

Raw data are loading into a staging environement. The staging table is flexible allowing any data schema change. A surrogate key is generated. 

### Transform

Data from raw table are selected to fit a common schema in a production environement. Geopoint data and locationID are transformed to zone.

### Update data set

Data can be upated as soon as new data are available. However data are made available usually over a month or 6 months period, which mean that daily data should be ingested backfilled. And again here is using the Socrate API it is best to chose daily backfill update to ensure consistency, reliabibly and respect the Airflow concepts and phylisophy. 

## Specific scenarios
---

###The data was increased by 100x

Data would be stored the same way however it would be necessary to have extra production table prepared for specific purpose.

###The pipelines would be run on a daily basis by 7 am every day.

The pipeline is already set to run on daily basis. If the dag fail and need to be re-run depending on where the dag fails the final production table could be impacted. Duplicate surrogate keys will need to be removed or filtered out.

###The database needed to be accessed by 100+ people.

It would be easy to open access to 100+ people with Google Cloud Console access management however it could become costly very quickly. The best way to share these data would be to build a dashboard with aggregated data, preformated to answer specific questions (in order to avoid too many read operations)

## Choice of tools, technologies, and data model
---

The data model chosen for this project was made for analytics purpose. Fact table can be easily join with dimension table. Answers like the numbers of daily trip, the avg cost of trip, the evolution of trips over time, the average number of passemgers, the hottest pickup and drop-off zone... could be easily answered with the final production table.

