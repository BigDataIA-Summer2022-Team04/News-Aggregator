
import logging
from typing import Union
from fastapi import APIRouter, HTTPException, Response, status, Query, Depends
import schemas
from routers.oaut2 import get_current_user
import datetime
import pymongo
from bson.json_util import dumps
import os

router = APIRouter(
    prefix="/mongodb",
    tags=['Database']
)


@router.get('/weekly', status_code=status.HTTP_200_OK)
async def get_weekly_stats(
                            get_current_user: schemas.ServiceAccount = Depends(get_current_user)
                            ):
    """Gets counts of articles based on daily, weekly and monthly timeframe

    Parameters
    ----------
    None

    Returns
    -------
    dataframe
        a dataframe with number of articles based on daily, weekly and monthly
    """
    now = datetime.datetime.now().replace(microsecond=0)
    lastweek = now - datetime.timedelta(days=7)
    mongo_client = pymongo.MongoClient(
        f"mongodb+srv://{os.environ['MONGO_DB_USERNAME']}:{os.environ['MONGO_DB_PASSWORD']}@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = mongo_client["news"]
    mycollection = mydb["processed"]
    try:
        query_output = mycollection.aggregate([
            {
                "$match": {"first_published_date": {'$gte': lastweek, '$lt': now}}},

            {
                "$group": {"_id": "$section",
                        "count": {"$sum": 1}}
            },
            {
                "$sort": {'count': 1}
            }
        ])
        return dumps(list(query_output))
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot retrieve time period stats document")


@router.get('/news_feed', status_code=status.HTTP_200_OK)
async def news_feed(news_section: str,
                    get_current_user: schemas.ServiceAccount = Depends(
                        get_current_user)
                    ):
    """Gets top 3 latest articles which are unread by user

    Parameters
    ----------
    news_section : str
        The news section based on 15 defined section
        
    Returns
    -------
    list
        a dict which contains article data 
    """
    mongo_client = pymongo.MongoClient(
        f"mongodb+srv://{os.environ['MONGO_DB_USERNAME']}:{os.environ['MONGO_DB_PASSWORD']}@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = mongo_client["news"]
    mycollection = mydb["processed"]
    try:
        query_output = mycollection.find(
            {"section": f"{news_section.title()}",
            "users_red": {"$ne": f"{get_current_user.email}"}},
            {"_id": 1, "section": 1, "subsection": 1, "url": 1,
                "language": 1, "first_published_date": 1}
        ).sort('first_published_date', -1).limit(3)

        return list(query_output)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot retrieve article document")


@router.post('/mark_news_as_red', status_code=status.HTTP_200_OK)
async def mark_news_as_red(news_uid: str,
                           get_current_user: schemas.ServiceAccount = Depends(
                               get_current_user)
                           ):
    """Appends user id into the article document marking it as read

    Parameters
    ----------
    news_uid : str
        Logged in user email id
        
    Returns
    -------
    None
    """
    mongo_client = pymongo.MongoClient(
        f"mongodb+srv://{os.environ['MONGO_DB_USERNAME']}:{os.environ['MONGO_DB_PASSWORD']}@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = mongo_client["news"]
    mycollection = mydb["processed"]
    user_id = get_current_user.email

    try:
        output = mycollection.update_one(
            {"_id": f"{news_uid}"},
            {"$addToSet": {"users_red": f"{get_current_user.email}"}}
        )
        return output.matched_count
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot Update MongoDB")
