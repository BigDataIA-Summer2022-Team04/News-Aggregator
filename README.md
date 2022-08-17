# News Aggregator

Backend data service build using [FastAPI](https://fastapi.tiangolo.com/) to integrate Frontend application on [Streamlit](https://streamlit.io/) and Databases of [BigQuery](https://cloud.google.com/bigquery) and [MongoDB Atlas](https://www.mongodb.com/atlas)

## Primary Endpoints

1. User Registration
2. User Login
3. Article Stats
4. Fetch Article Document
5. User Activity Tracking
6. IM Notification

## API Documentation

Access Swagger documentation at [link]()

## Deployed Service

Tech: `Docker`

Docker Image: (DockerHub)[https://hub.docker.com/repository/docker/anku22/news_agg_fastapi]

Environment Variables:
```text
TWILIO_SID
TWILIO_TOKEN
MONGO_DB_USERNAME
MONGO_DB_PASSWORD
GOOGLE_APPLICATION_CREDENTIALS
```
Accessible Port: `8090`