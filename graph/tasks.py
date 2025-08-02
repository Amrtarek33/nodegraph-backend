from celery import shared_task
import time
from .models import Node


@shared_task
def slow_find_path_task(from_node_name, to_node_name):
    time.sleep(5)
    return Node.find_path(from_node_name, to_node_name)
