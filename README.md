# News-Aggregator

## Deployed on Google Compute Instance 

Configuration:
* Name: `airflow`
* Region: `us-east1`
* Zone: `us-east-b`
* Series: `N2`
* Machine Type: `n2-standard-2`
* Boot disk: 
    * Image: `Ubuntu 22.04 LTS`
* Firewall: Check both
    * Allow HTTP traffic
    * Allow HTTPS traffic
* Firewall Rule:
    * Allow `8000`, `8090`, `8095`


## Generate DAG

Using [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templating generate the DAG's

```bash
pip install Jinja2

python DAG_generator.py
```

## Pipeline Schedule

Everyday
* 5:40 ~ 5:50 - Data Scraping
* 6:00 - Data Report Generation
* 6:15 - Data Processing

Note: Data Processing job is scheduled as cronjob due large runtime of up to 2~3 hours based on documents
```shell
$ crontab -l
15 6 * * * python data_processing.py
```

## Services 

To deploy this application use docker-compose to start airflow, FastAPI and Streamlit <br>
Replace the environment variables

```shell
docker-compose up
```

## BigQuery

User Data logs and article read are stored in Bigquery

#### Procedure 1: To create customer records while registration

```sql
CREATE OR REPLACE PROCEDURE `plane-detection-352701.NEWS_USER_MONITORING.create_customer`(username STRING)
BEGIN
SELECT 'SECTION'
    FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME`
    WHERE USER = username
    ORDER BY READ_TIME DESC
    limit 3;
END
```

#### Procedure 2: To calculate the reading time of article 

```sql
CREATE OR REPLACE PROCEDURE `plane-detection-352701.NEWS_USER_MONITORING.update_read_time`(USER_ID STRING, USER_SECTION STRING)
BEGIN

DECLARE LAST_READ_ARTICLE_TS TIMESTAMP;
DECLARE NOW_TS TIMESTAMP;
DECLARE DIFF_MINS INT64;
DECLARE LAST_READ_MINS INT64;
DECLARE LAST_READ_SECTION STRING;

SET NOW_TS = CURRENT_TIMESTAMP();
SET LAST_READ_ARTICLE_TS = (SELECT MAX(READ_START_TIME) FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` WHERE USER = USER_ID);
SET DIFF_MINS = TIMESTAMP_DIFF(NOW_TS, LAST_READ_ARTICLE_TS, MINUTE);

SET LAST_READ_MINS = (SELECT READ_TIME FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` WHERE USER = USER_ID ORDER BY READ_START_TIME DESC limit 1);
SET LAST_READ_SECTION = (SELECT SECTION FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` WHERE USER = USER_ID ORDER BY READ_START_TIME DESC limit 1);

SELECT DIFF_MINS;

IF (DIFF_MINS <= 10) THEN
  UPDATE `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME`
    SET READ_START_TIME = CURRENT_TIMESTAMP(), 
    READ_TIME = (DIFF_MINS + LAST_READ_MINS)
    WHERE USER = USER_ID  AND SECTION = LAST_READ_SECTION;
END IF;

SELECT COUNT(*) FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` WHERE USER = USER_ID AND SECTION = USER_SECTION;

IF (SELECT COUNT(*) FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` WHERE USER = USER_ID AND SECTION = USER_SECTION) = 1 THEN

UPDATE `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME`
    SET READ_START_TIME = CURRENT_TIMESTAMP()
    WHERE USER = USER_ID  AND SECTION = USER_SECTION;

ELSE

INSERT INTO `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` (ID, USER, SECTION, READ_START_TIME, READ_TIME ) VALUES (
            (SELECT MAX(ID)+1 from `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME`),
            USER_ID,
            USER_SECTION,
            CURRENT_TIMESTAMP(),
            0);

END IF;
END
```
