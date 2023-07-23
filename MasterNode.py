Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
import pika
import redis
import logging
import time

logging.basicConfig(level=logging.INFO)

# Connecting to RabbitMQ Services
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Connecting to Redis Service
r = redis.Redis(host='localhost', port=6379, db=0)

# Declare a queue that holds the URLs to be crawled.
channel.queue_declare(queue='url_queue', durable=True)

# This is a list of URLs to be crawled
urls_to_crawl = ['http://example1.com', 'http://example2.com', 'http://example3.com']

for url in urls_to_crawl:
    # If the URL has already been added to the queue, skip it
    if url in added_urls:
        continue
    
    # Get the load of all the nodes
    loads = r.hgetall('loads')
    
    # If all nodes are busy, wait for a while.
    while all(int(load) > 5 for load in loads.values()):
        time.sleep(5)
        loads = r.hgetall('loads')
    
    # Select the least loaded node
    min_load_node = min(loads, key=loads.get)
    
    # Add the URL to the queue of the corresponding node.
    channel.basic_publish(exchange='',
                          routing_key=f'{min_load_node}_queue',
                          body=url,
                          properties=pika.BasicProperties(delivery_mode=2))  # Set message persistence
    logging.info(f"Added URL to queue: {url}, node: {min_load_node}")

logging.info("Finished adding URLs to queue")
connection.close()
