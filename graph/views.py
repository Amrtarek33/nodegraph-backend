from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Node
from .tasks import slow_find_path_task
from .serializers import (
    NodeSerializer,
    NodeConnectionSerializer,
    PathFinderSerializer,
    AsyncTaskSerializer,
    AsyncTaskResultSerializer,
)
from celery.result import AsyncResult


@api_view(["POST"])
@permission_classes([AllowAny])
def create_node(request):
    serializer = NodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    name = serializer.validated_data["name"]

    if Node.objects.filter(name=name).exists():
        return Response(
            {"error": "Node with this name already exists"},
            status=status.HTTP_409_CONFLICT,
        )

    node = Node.objects.create(name=name)
    return Response(NodeSerializer(node).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def connect_nodes(request):
    serializer = NodeConnectionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    from_node_name = serializer.validated_data["FromNode"]
    to_node_name = serializer.validated_data["ToNode"]

    from_node = get_object_or_404(Node, name=from_node_name)
    to_node = get_object_or_404(Node, name=to_node_name)

    if to_node in from_node.connections.all():
        return Response(
            {"message": "Nodes are already connected"}, status=status.HTTP_200_OK
        )

    from_node.connections.add(to_node)
    return Response(
        {"message": "Nodes connected successfully"}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def find_path(request):
    serializer = PathFinderSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    from_node_name = serializer.validated_data["FromNode"]
    to_node_name = serializer.validated_data["ToNode"]

    path = Node.find_path(from_node_name, to_node_name)
    return Response({"path": path}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def slow_find_path(request):
    serializer = PathFinderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    from_node_name = serializer.validated_data["FromNode"]
    to_node_name = serializer.validated_data["ToNode"]

    task = slow_find_path_task.delay(from_node_name, to_node_name)
    return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_slow_path_result(request):
    serializer = AsyncTaskSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    task_id = serializer.validated_data["task_id"]
    task_result = AsyncResult(task_id)

    result_serializer = AsyncTaskResultSerializer(
        {
            "status": "SUCCESS" if task_result.ready() else "PENDING",
            "result": task_result.result if task_result.ready() else None,
        }
    )

    return Response(result_serializer.data, status=status.HTTP_200_OK)
