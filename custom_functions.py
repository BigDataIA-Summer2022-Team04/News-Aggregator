import logging
from google.cloud import bigquery

#################################################
# Author: Piyush
# Creation Date: 17-Jun-22
# Last Modified Date:
# Change Logs:
# SL No         Date            Changes
# 1             17-Jun-22       First Version
# 2             24-Jun-22       Log Function
# 3             13-Jul-22       Remove state function
# 4             13-Jul-22       Added create_user_interest_in_bigquery function
# 5             13-Jul-22       Added get_top_3_user_interest_from_bigquery function
#################################################


def logfunc(username: str, endpoint:str, response_code: int):
    logging.info(f"Writing logs to bigQuery")
    client = bigquery.Client()
    query_string = f"""
    INSERT INTO `plane-detection-352701.SPY_PLANE.logs` VALUES (
    CAST(CURRENT_TIMESTAMP() AS STRING ), '{username}', '{endpoint}', {response_code}, (SELECT MAX(logid)+1 AS ID from `plane-detection-352701.SPY_PLANE.logs`))
    """
    # logging.info(f"query_string : {query_string}")
    try:
        df = client.query(query_string)
        print(df)
    except Exception as e:
        logging.error(f"Exception: {e}")
        logging.error(f"Error Writing logs to BigQuery")
        return
    logging.info(f"Writing logs to bigQuery Completed")


async def create_user_interest_in_bigquery(username: str, section:str):
    """_summary_
    Table Schema
    ID	            INTEGER	    REQUIRED		
    USER	        STRING	    REQUIRED
    SECTION	        STRING	    REQUIRED
    READ_START_TIME	TIMESTAMP	NULLABLE
    READ_END_TIME	TIMESTAMP	NULLABLE
    READ_TIME       INTEGER	    NULLABLE	
    """
    logging.info(f"Writing user entry to bigQuery")
    client = bigquery.Client()
    for sec in section.split('|'):
        query_string = f"""
        INSERT INTO `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME` (ID, USER, SECTION, READ_START_TIME, READ_TIME ) VALUES (
            (SELECT MAX(ID)+1 from `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME`),
            '{username}',
            '{sec}',
            CURRENT_TIMESTAMP(),
            0
        );
        COMMIT TRANSACTION;
        """
        print(query_string)
        try:
            client.query(query_string)
        except Exception as e:
            logging.error(f"Exception: {e}")
            logging.error(f"Error Writing user entry to BigQuery")
            continue
    logging.info(f"Writing user entry to bigQuery Completed")
    
    
def get_top_3_user_interest_from_bigquery(username: str):
    """_summary_
    Table Schema
    ID	            INTEGER	    REQUIRED		
    USER	        STRING	    REQUIRED
    SECTION	        STRING	    REQUIRED
    READ_START_TIME	TIMESTAMP	NULLABLE
    READ_END_TIME	TIMESTAMP	NULLABLE
    READ_TIME       INTEGER	    NULLABLE	
    """
    logging.info(f"Writing user entry to bigQuery")
    client = bigquery.Client()
    query_string = f"""SELECT SECTION
    FROM `plane-detection-352701.NEWS_USER_MONITORING.SPEND_TIME`
    WHERE USER = '{username}'
    ORDER BY READ_TIME DESC
    limit 3
    """
    print(query_string)
    try:
        df = client.query(query_string)
        logging.info(f"Writing user entry to bigQuery Completed")
        return list(df)
    except Exception as e:
        logging.error(f"Exception: {e}")
        logging.error(f"Error Writing user entry to BigQuery")
    