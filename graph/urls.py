from django.urls import path
from . import views

urlpatterns = [
    path("create-node/", views.create_node, name="create_node"),
    path("connect-nodes/", views.connect_nodes, name="connect_nodes"),
    path("find-path/", views.find_path, name="find_path"),
    path("slow-find-path/", views.slow_find_path, name="slow_find_path"),
    path(
        "get-slow-path-result/", views.get_slow_path_result, name="get_slow_path_result"
    ),
]
