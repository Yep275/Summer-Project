Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
>>> 
import time
import queue
import threading
import random

class Task:
    def __init__(self, id, priority=1):
        self.id = id
        self.priority = priority

class Node:
    def __init__(self, id):
        self.id = id
        self.weight = random.randint(1, 10)  # Assume each node has a random weight initially
        self.task_queue = queue.Queue()
        self.assigned_tasks = 0

    def assign_task(self, task):
        self.task_queue.put(task)
        self.assigned_tasks += 1
        print(f"Assigned task {task.id} to node {self.id}")

    def run(self):
        while True:
            if not self.task_queue.empty():
                task = self.task_queue.get()
                time.sleep(random.randint(1, 3))  # Simulate the time it takes to complete a task
                print(f"Node {self.id} completed task {task.id}")
                self.assigned_tasks -= 1
            time.sleep(0.1)

class LoadBalancer:
    def __init__(self, nodes):
        self.nodes = nodes
        self.threshold = max(node.weight for node in nodes)

    def assign_task(self, task):
        for node in sorted(self.nodes, key=lambda x: x.weight, reverse=True):
            if node.weight >= self.threshold and node.assigned_tasks < node.weight:
                node.assign_task(task)
                node.weight = max(1, node.weight - 1)
                return
        self.threshold = max(1, self.threshold - 1)  # If no suitable node found, reduce the threshold and retry

    def add_task(self, task):
        self.assign_task(task)

nodes = [Node(i) for i in range(4)]

lb = LoadBalancer(nodes)

# Start each node on a separate thread
for node in nodes:
    threading.Thread(target=node.run).start()

# Add tasks with varying priority
for i in range(20):
    lb.add_task(Task(i, random.randint(1, 10)))

while True:
    time.sleep(1)
