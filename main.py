import os
import logging
import models
from database import engine, SessionLocal
from routers import mongodb, users, authentication, news_feeds, whatsapp
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.staticfiles import StaticFiles

#################################################
# Author: Piyush
# Creation Date: 10-Aug-22
# Last Modified Date:
# Change Logs:
# SL No         Date            Changes
# 1             10-Aug-22      First Version
# 
#################################################

# os.environ['TWILIO_SID'] = ''
# os.environ['TWILIO_TOKEN'] = ''
# os.environ['MONGO_DB_USERNAME'] = ''
# os.environ['MONGO_DB_PASSWORD'] = ''
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/keys/key2.json'


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level="DEBUG", # INFO DEBUG ERROR
    datefmt='%Y-%m-%d %H:%M:%S')



app = FastAPI(title="News Aggregator Backend")

models.Base.metadata.create_all(bind=engine)

app.include_router(news_feeds.router)
app.include_router(mongodb.router)
app.include_router(whatsapp.router)
app.include_router(users.router)
app.include_router(authentication.router)
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")


