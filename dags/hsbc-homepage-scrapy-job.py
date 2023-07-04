""" This is a DAG to scrapy HSBC HK homepage info and deploy on GCP MapleQuad's Airflow
The knowledge will be stored in a txt file and upload to GCS bucket
"""
import re
import requests
import json
from datetime import datetime
from google.cloud import storage
from airflow import DAG
from airflow.decorators import task
from bs4 import BeautifulSoup

# init variables
project_id = 'hsbc-1044360-ihubasp-sandbox'
bucket_name = 'openrice_scrapy_for_dining_recommendation/hsbc_knowledge' # openrice_scrapy_for_dining_recommendation/hsbc_knowledge
homepage_url = 'https://www.hsbc.com.hk/'
wealth_insigths_articles = 'https://www.hsbc.com.hk/wealth/insights.load-wih-articles.json'
chinese_pattern = re.compile("[\u4e00-\u9fff\u3400-\u4dbf]+")

def scrape_content_by_url(url: str):
    """ scrape content by url
    """
    # Send a GET request to the webpage URL
    response = requests.get(url, timeout=5)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the text content and remove excess whitespace
    text = soup.get_text()
    text = re.sub('\s+', ' ', text).strip().lower()
    text = chinese_pattern.sub("", text)
    return text


def retreive_urls_by_parent_url():
    """ retreive urls by parent url
    """
    # Send a GET request to the webpage URL
    response = requests.get(homepage_url, timeout=5)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the url start with a
    a_tags = soup.find_all('a')
    # retrieve all the link
    urls = [a_tag.get('href') for a_tag in a_tags if a_tag is not None and a_tag.get('href') is not None]
    # remove all the link start with http or https
    urls = [url for url in urls if not url.startswith(('http', '#'))]
    # remove other language url
    urls = [url for url in urls if url not in ('/', '/zh-hk/', '/zh-cn/')]
    return urls

def copy_file_to_gcs_bucket(bucket_name, source_file_name, destination_blob_name):
    """
    Copy a local file to a GCS bucket
    """
    # Instantiate a client
    storage_client = storage.Client()
    # Set the bucket and blob names
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    # Upload the file to GCS
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")    


@task(task_id='scrapy')
def extract_knowledge():
    """
    Extract knowledge from hsbc homepage and wealth insights
    """
    # extract home page child urls
    urls = retreive_urls_by_parent_url()
    # loop and extract content
    for url in urls:
        try:
            # retreive content
            content = scrape_content_by_url(homepage_url + url)
            key_words = url.replace('/', ' ')
            # skip the content if less than 50 words
            if len(content) < 50:
                print('Skip current url -> content less than 50 words with url=%s' % url)
                continue
            # append content into a txt file
            with open('/tmp/knowledge.txt', 'a') as f:
                print(f"Append knowledge with url={url}")
                f.write('Key Words: {}\n'.format(key_words))
                f.write('Content: {}\n\n'.format(content))
        except Exception as e:
            print('Skip current url -> error occurred when scraping content from url=%s with error=%s' % (url, e))

    # copy the knowledge.txt to GCS bucket
    copy_file_to_gcs_bucket(bucket_name, '/tmp/knowledge.txt', 'knowledge.txt')

    # extract wealth insights content
    try:
        # extract wealth insights content
        response = requests.get(wealth_insigths_articles, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.text)
            for article in data:
                title, href = article["title"], article["href"]
                print(title, href)
                # retreive content
                content = scrape_content_by_url(href)
                # append content into a txt file
                with open('/tmp/wealth_insights.txt', 'a') as f:
                    f.write('Title: {}\n'.format(title))
                    f.write('URL: {}\n'.format(href))
                    f.write('Content: {}\n\n'.format(content))    
        else:
            print("Error: Could not retrieve JSON data")
    except Exception as e:
        print('Error occurred when scraping wealth insights content with error=%s' % e)

    # copy the wealth insights content to GCS bucket
    copy_file_to_gcs_bucket(bucket_name, '/tmp/wealth_insights.txt', 'wealth_insights.txt')


with DAG(
    'hsbc-knowledge-scrapy-job',
    default_args={
        'depends_on_past': False,
        'email': ['tracyqucy@gmail.com'],
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 0
    },
    description='DAG to scrapy HSBC HK homepage knowledge and weath insights and upload to GCS bucket',
    schedule_interval='0 8 * * *',
    start_date=datetime(2023, 6, 29),
    catchup=False,
    tags=['hsbc','homepage','scrape'],
) as dag:

    t1 = extract_knowledge()

    t1
