import os
import json
import pymongo
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.models.param import Param
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator


args = {
    'owner': 'Anku',
    'start_date': days_ago(0),
    'email': ['anand.pi@northeastern.edu'],
	'email_on_failure': True
}
 
dag = DAG(dag_id = f"NYT_Scraping_sports",
            default_args=args,
            schedule_interval="44 5 * * *"
        )


def scrape_article_body(url: str):
  session = HTMLSession()
  r = session.get(url)
  resp=r.html.raw_html
  soup = BeautifulSoup(r.html.raw_html, "html.parser")
  try:
    all_paras = articleBody[0].find_all('p')
    strBody = []
    for element in all_paras:
        strBody.append(element.text)
    ARTICLE = '\n'.join(strBody)
    return ARTICLE
  except:
    return 101

def get_existing_article(section):
    ids = []
    client = pymongo.MongoClient("mongodb+srv://airflow_schema:################@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = client["news"]
    mycollection = mydb["raw"]
    query_output = list(mycollection.find({'section': section.title() }, {'_id': 1} ))
    for element in query_output:
        ids.append(element['_id'])
    return ids


def data_sourcing(**kwargs):  
    sec = 'sports'
    existing_article_ids = get_existing_article(sec)
    payload = {'limit' : 40 ,'api-key' : '##########################'}
    response = requests.get(url = f"https://api.nytimes.com/svc/news/v3/content/all/{sec}.json", params=payload)
    json_data = json.loads(response.text)
    processed = []
    for element in json_data['results']:
        if element['uri'] in existing_article_ids:
            continue
        if element['material_type_facet'] == 'News':
            try:
                for e in ['slug_name', 'byline', 'thumbnail_standard', 'updated_date', 'created_date', 'published_date', 'subheadline', 'des_facet', 'org_facet', 'per_facet', 'geo_facet', 'related_urls', 'kicker']: 
                    element.pop(e)
            except KeyError:
                print("pop key doesnot exist")
            element['_id'] = element['uri']
            element['first_published_date'] = datetime.fromisoformat(element['first_published_date'])
            element['article_body'] = scrape_article_body(element['url'])
            if element['article_body'] == 101:
                print(f"SKIPPED : {element['url']}")
                continue
            element['thumbnail'] = ''
            try:
                for media in element['multimedia']:
                    if media['format'] == 'Normal':
                        element['thumbnail'] = media['url']
            except:
                print("No multimedia link")
            # element.pop('multimedia')
            processed.append(element)
    
    client = pymongo.MongoClient("mongodb+srv://airflow_schema:################@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = client["news"]
    mycol = mydb["raw"]
    # mycol.delete_many({}) # Comment
    if processed:
        print (f"Inserting {len(processed)} into MongoDB")
        mycol.insert_many(processed)
        mydb.daily_reporting.insert_many(processed)
    else:
        print (f"WARNING: Inserting {len(processed)} into MongoDB")
    return len(processed)
    

with dag:

    data_sourcing = PythonOperator(
        task_id='data_sourcing',
        python_callable = data_sourcing,
        provide_context=True,
        dag=dag
    )

    data_sourcing
    