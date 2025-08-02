from rest_framework import serializers


class NodeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class NodeConnectionSerializer(serializers.Serializer):
    FromNode = serializers.CharField(max_length=255)
    ToNode = serializers.CharField(max_length=255)


class PathFinderSerializer(serializers.Serializer):
    FromNode = serializers.CharField(max_length=255)
    ToNode = serializers.CharField(max_length=255)


class AsyncTaskSerializer(serializers.Serializer):
    task_id = serializers.CharField()


class AsyncTaskResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    result = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )
