Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
import pika
import redis
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
from time import sleep
from contextlib import closing
import os

logging.basicConfig(level=logging.INFO)

# Get the name of the current node
node_name = os.getenv('NODE_NAME')

# Crawler Code
def crawl_url(url):
    response = requests.get(url)
    response.raise_for_status()  # If the HTTP request returns an error status code, an exception will be thrown

    # Use BeautifulSoup to parse HTML and extract headers
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string

    return title

# Save the result to the database
def save_result_to_db(db_path, url, title):
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS results (url TEXT, title TEXT)')
        cursor.execute('INSERT INTO results VALUES (?, ?)', (url, title))
        conn.commit()

# Connect to RabbitMQ service
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Connect to Redis service
r = redis.Redis(host='localhost', port=6379, db=0)

# Declare a queue to fetch the URLs to be crawled
channel.queue_declare(queue=f'{node_name}_queue', durable=True)

def callback(ch, method, properties, body):
    url = body.decode()
    try:
        # Attempt to crawl the URL
        title = crawl_url(url)
        save_result_to_db('results.db', url, title)
    except Exception as e:
        # If an error occurs during crawling, log the error message but do not send an ack so that the URL stays in the queue.
        logging.error(f"Error processing URL {url}: {e}")
    else:
        # If the crawl is successful, send an ack so that the URL is removed from the queue.
        ch.basic_ack(delivery_tag=method.delivery_tag)
        r.hincrby('loads', node_name, -1)

channel.basic_qos(prefetch_count=1)  # Fair scheduling to ensure that each sub-node handles only one task at a time.
channel.basic_consume(queue=f'{node_name}_queue', on_message_callback=callback)

logging.info(f"{node_name} worker started consuming URL tasks")
channel.start_consuming()
