from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    connections = models.ManyToManyField("self", symmetrical=False)

    def __str__(self):
        return self.name

    @classmethod
    def find_path(cls, from_node_name, to_node_name):
        try:
            from_node = cls.objects.select_related().get(name=from_node_name)
            to_node = cls.objects.select_related().get(name=to_node_name)
        except cls.DoesNotExist:
            return None

        if from_node == to_node:
            return [from_node.name]

        visited = set()
        queue = [(from_node, [from_node.name])]

        while queue:
            current_node, path = queue.pop(0)
            if current_node == to_node:
                return path
            visited.add(current_node)
            for neighbor in current_node.connections.all():
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor.name]))

        return None
