Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
>>> 
import time
import threading
import logging
from operator import attrgetter
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import numpy as np


class Node:
    def __init__(self, id, weight, timeout=1, max_retries=3):
        self.id = id
        self.weight = weight
        self.timeout = timeout
        self.max_retries = max_retries
        self.is_down = False
        self.failed_retries = 0
        self.history = []

    def assign_task(self, task):
        try:
            start_time = time.time()
            # Process the task...
            soup = BeautifulSoup(task['html'], 'html.parser')
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            end_time = time.time()
            self.history.append(end_time - start_time)
            self.update_weight()
            self.failed_retries = 0
            if self.is_down:
                print(f"Node {self.id} recovered")
                self.is_down = False
            return links
        except Exception as e:
            self.failed_retries += 1
            if self.failed_retries >= self.max_retries:
                print(f"Node {self.id} is down")
                self.is_down = True
            return None

    def update_weight(self):
        if len(self.history) > 100:  # We consider only last 100 tasks.
            self.history.pop(0)
        self.weight = 300000/(np.sum(self.history)*(len(self.history)+1))


class Master:
    def __init__(self, initial_threshold=1):
        self.nodes = []
        self.lock = threading.Lock()
        self.threshold = initial_threshold
        logging.basicConfig(filename='times.log', level=logging.INFO)

    def add_node(self, node):
        with self.lock:
            self.nodes.append(node)
        threading.Thread(target=self.health_check, args=(node,)).start()

    def assign_task(self, task):
        for _ in range(self.threshold, -1, -1):
            for node in sorted(self.nodes, key=attrgetter('weight'), reverse=True):
                if node.weight >= self.threshold and not node.is_down:
                    result = node.assign_task(task)
                    if result is not None:
                        total_time = self.total_time()
                        self.log_time(total_time)
                        return result
        self.threshold = max(node.weight for node in self.nodes)  # Reset threshold
        return None

    def health_check(self, node):
        while True:
            time.sleep(60)  # Health check every minute
            if not node.is_down:
                node.assign_task({})

    def total_time(self):
        return sum(sum(node.history) for node in self.nodes)
    
    def log_time(self, total_time):
        logging.info(f"Total time after assigning task: {total_time}")

                
app = Flask(__name__)
master = Master()

@app.route('/task', methods=['POST'])
def task():
    task_data = request.get_json()
    result = master.assign_task(task_data)
    if result is not None:
        return jsonify(result)
    else:
        return "All nodes are down or busy.", 500  
