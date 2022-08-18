
import logging
from typing import Union
from fastapi import APIRouter, HTTPException, Response, status, Query, Depends
import schemas
from routers.oaut2 import get_current_user
from bson.json_util import dumps
from custom_functions import get_top_3_user_interest_from_bigquery, logfunc
from routers.mongodb import news_feed
from google.cloud import bigquery
import random

router = APIRouter(
    prefix="/feeds",
    tags=['Feeds']
)

@router.get('/personalized_section', status_code=status.HTTP_200_OK)
async def personalized_section(
                            get_current_user: schemas.ServiceAccount = Depends(get_current_user)
                        ):
    """Calls BigQuery to get top 3 section based on user interest and fetches resp articles from MongoDb

    Parameters
    ----------
    None

    Returns
    -------
    news_top_3_section: list
        list of dict containing article document from mongo db
    """
    try:
        top_3_topics_json = get_top_3_user_interest_from_bigquery(get_current_user.email)

        news_top_3_section = {}
        for elements in top_3_topics_json:
            news_top_3_section[elements['SECTION']] = await news_feed(elements['SECTION'], get_current_user)
        logfunc(get_current_user.email, "/NA/feeds/personalized_section", 200)
        return news_top_3_section
    except:
        logfunc(get_current_user.email, "/NA/feeds/personalized_section", 400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot generate Personalized Section")
        
@router.get('/other_section_news', status_code=status.HTTP_200_OK)
async def other_section_news(
                            get_current_user: schemas.ServiceAccount = Depends(get_current_user)
                        ):
    """Calls BigQuery to get top 3 section based on user interest and fetches 3 random articles from other sections

    Parameters
    ----------
    None

    Returns
    -------
    news_top_3_section: list
        list of dict containing article document from mongo db
    """
    try:
        top_3_topics_json = get_top_3_user_interest_from_bigquery(get_current_user.email)
        logging.debug(top_3_topics_json)
        options = ['arts',
                'automobiles',
                'books',
                'business',
                'climate',
                'education',
                'fashion',
                'food',
                'health',
                # 'job+market',
                'science',
                'sports',
                'technology',
                'travel',
                # 'u.s.',
                'universal',
                'world']
        
        news_top_3_section = {}
        for elements in top_3_topics_json:
            logging.debug(elements['SECTION'])
            options.remove(elements['SECTION'])
        logging.debug(options)
        sampled_list = random.sample(options, 3)
        logging.debug(sampled_list)
        for element in sampled_list:
            news_top_3_section[element] = await news_feed(element, get_current_user)
        logging.debug(news_top_3_section)
        logfunc(get_current_user.email, "/NA/feeds/other_section_news", 200)
        return news_top_3_section
    except:
        logfunc(get_current_user.email, "/NA/feeds/other_section_news", 400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot generate Personalized Section")


@router.post('/post_read_mins', status_code=status.HTTP_200_OK)
async def post_read_mins( user_section: str,
                            get_current_user: schemas.ServiceAccount = Depends(get_current_user)
                        ):
    """Calls BigQuery procedure to log the user article read time

    Parameters
    ----------
    user_section: str
        The news section which the user is currently reading

    Returns
    -------
    None
    """
    client = bigquery.Client()
    query_string = f"""CALL `plane-detection-352701.NEWS_USER_MONITORING.update_read_time`('{get_current_user.email}', '{user_section.lower()}');"""
    try:
        df = client.query(query_string)
        logfunc(get_current_user.email, "/NA/feeds/post_read_mins", 200)
        return list(df)
    except:
        logfunc(get_current_user.email, "/NA/feeds/post_read_mins", 400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot connect to BigQuery")

