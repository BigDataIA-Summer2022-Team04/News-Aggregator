import os
import json
import requests
from dotenv import load_dotenv


###############################
# Create .env file with 
#       USERNAME = 'anand.pi@northeastern.edu'
#       PASSWORD = ''
###############################


load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
BASE_URL = 'http://34.73.35.12:8090'
# BASE_URL = 'http://localhost:8000'

def get_access_token():
    payload={'username': {USERNAME}, 'password': PASSWORD}
    response = requests.request("POST", f"{BASE_URL}/login", data=payload)
    json_data = json.loads(response.text)
    return json_data["access_token"]


ACCESS_TOKEN = get_access_token()
header = {}
header['Authorization'] = f"Bearer {ACCESS_TOKEN}"


def test_login(url =  f"{BASE_URL}/login"):
    payload={'username': {USERNAME}, 'password': PASSWORD}
    response = requests.request("POST", url, data=payload)
    assert response.status_code == 200

def test_incorrect_login(url =  f"{BASE_URL}/login"):
    payload={'username': 'fake_user@email.com', 'password': 'WrongPassword'}
    response = requests.request("POST", url, data=payload)
    assert response.status_code == 404


## Feeds

# Feeds | Endpoint 1
def test_personalized_section(url =  f"{BASE_URL}/feeds/personalized_section"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp.keys()) == 3 # Check for 3 keys for top 3 topics
    assert len(json_resp[list(json_resp.keys())[0]]) == 3
    assert len(json_resp[list(json_resp.keys())[1]]) == 3
    assert len(json_resp[list(json_resp.keys())[2]]) == 3

def test_personalized_section_invalid_token(url =  f"{BASE_URL}/feeds/personalized_section"):
    response = requests.request("GET", url, headers={'Authorization' : 'InvalidToken'})
    assert response.status_code == 401

# Feeds | Endpoint 2
def test_other_section_news(url =  f"{BASE_URL}/feeds/other_section_news"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp.keys()) == 3 # Check for 3 keys for other 3 topics
    assert len(json_resp[list(json_resp.keys())[0]]) == 3
    assert len(json_resp[list(json_resp.keys())[1]]) == 3
    assert len(json_resp[list(json_resp.keys())[2]]) == 3

def test_other_section_news_invalid_token(url =  f"{BASE_URL}/feeds/other_section_news"):
    response = requests.request("GET", url, headers={'Authorization' : 'InvalidToken'})
    assert response.status_code == 401

# Feeds | Endpoint 3
def test_post_read_mins(url =  f"{BASE_URL}/feeds/post_read_mins?user_section=health"):
    response = requests.request("POST", url, headers=header)
    assert response.status_code == 200



# Database | Endpoint 1
def test_mongodb_weekly(url =  f"{BASE_URL}/mongodb/weekly"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 15 # Check for 15 keys indicating all 15 sections


# Database | Endpoint 2
def test_mongodb_news_stats(url =  f"{BASE_URL}/mongodb/news_stats"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) <= 45 # Max of 3 categories of 15 sections => 3 * 15 = 45


# Database | Endpoint 3
def test_mongodb_news_feed(url =  f"{BASE_URL}/mongodb/news_feed?news_section=technology"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 3 # Check for 3 news of the input section

# Database | Endpoint 3
def test_mongodb_news_feed_unknown(url =  f"{BASE_URL}/mongodb/news_feed?news_section=unknownsection"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 0 # should return empty for unknownsection section


# Database | Endpoint 4
def test_mongodb_read_articles(url =  f"{BASE_URL}/mongodb/read_articles"):
    response = requests.request("GET", url, headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) >= 0  # Must be 0 or more 
    

# Whatsapp | Endpoint 1
def test_send_link(url =  f"{BASE_URL}/notify/send_link?news_title=Testing&news_url=testingURL&mobile=8572694998"):
    response = requests.request("POST", url, headers=header)
    assert response.status_code == 200
    assert response.text == "\"Success\""
    
# Whatsapp | Endpoint 1
def test_send_link_wrong_number(url =  f"{BASE_URL}/notify/send_link?news_title=Testing&news_url=testingURL%20url&mobile=8572998"):
    response = requests.request("POST", url, headers=header)
    assert response.status_code == 400
    