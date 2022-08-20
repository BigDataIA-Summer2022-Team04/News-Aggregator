import pymongo
import warnings
import trio
from transformers import AutoModelWithLMHead, AutoTokenizer, pipeline, AutoModelForSeq2SeqLM
import pymongo
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

tokenizer1 = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model1 = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

def summerizer(text):
  inputs = tokenizer1.encode("summarize: " + text , return_tensors="pt", max_length=512, truncation=True)
  outputs = model1.generate(inputs)
  return tokenizer1.decode(outputs[0], skip_special_tokens=True)


tokenizer2 = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
model2 = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-hi")

def translator_into_hindi(text):
  # function to translate english text to hindi
  input_ids = tokenizer2.encode(text, return_tensors="pt", padding=True)
  outputs = model2.generate(input_ids)
  decoded_text = tokenizer2.decode(outputs[0], skip_special_tokens=True)
  
  return decoded_text


mode_name3 = 'liam168/trans-opus-mt-en-zh'
model3 = AutoModelWithLMHead.from_pretrained(mode_name3)
tokenizer3 = AutoTokenizer.from_pretrained(mode_name3)

translation3 = pipeline("translation_en_to_zh", model=model3, tokenizer=tokenizer3)
def translator_into_mandarin(text):
  return translation3(text, max_length=400)


def write_to_mongo(processed):
  client = pymongo.MongoClient("mongodb+srv://airflow_schema:#############@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
  mydb = client["news"]
  mycol = mydb["processed"]
  # mycol.delete_many({}) # Comment
  mycol.insert_many(processed)


def get_existing_article_from_processed(section):
    ids = []
    client = pymongo.MongoClient("mongodb+srv://airflow_schema:#############@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = client["news"]
    mycollection = mydb["processed"]
    query_output = list(mycollection.find({'section': section.title() }, {'_id': 1} ))
    for element in query_output:
        ids.append(element['_id'])
    return ids


def get_article_from_raw(section):
    ids = []
    client = pymongo.MongoClient("mongodb+srv://airflow_schema:#############@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = client["news"]
    mycollection = mydb["raw"]
    query_output = list(mycollection.find({'section': section.title() } ))
    return query_output


async def raw_to_processed(sec):
    print(f"RUN SECTION: {sec}")
    
    processed_list_ids = get_existing_article_from_processed(sec)
    
    articles = get_article_from_raw(sec)
    # print(len(articles))
    processed = []
    for count2, each_article in enumerate(articles, start = 1):
        print(f"RUN ARTICLE - {sec}: {count2} of {len(articles)}")
        if each_article['_id'] in processed_list_ids:
            continue
        title_summary = {}
        title_summary['title'] = each_article['title']
        title_summary['summary'] = summerizer(each_article['article_body'])
        each_article['users_red'] = []
        each_article['language'] = {'english': title_summary}
        each_article['language']['hindi'] = {'title': translator_into_hindi(title_summary['title']), 'summary' : translator_into_hindi(title_summary['summary'])}
        each_article['language']['chinese'] = {'title': translator_into_mandarin(title_summary['title'])[0]['translation_text'], 'summary' : translator_into_mandarin(title_summary['summary'])[0]['translation_text']}

        processed.append(each_article)
    if processed:
        write_to_mongo(processed)
    
    

async def spawn_task():
    async with trio.open_nursery() as nursery:
        # explicit task spawning area. Nursery for tasks!
        all_section = 'arts|automobiles|books|business|climate|education|fashion|food|health|science|sports|technology|travel|universal|world'
        for count, sec in enumerate(all_section.split('|'), start = 1):
            print(f"RUN SECTION: {count} of {len(all_section.split('|'))}")
            nursery.start_soon(raw_to_processed, sec)

trio.run(spawn_task)
