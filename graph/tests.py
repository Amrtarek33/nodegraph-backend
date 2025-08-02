import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Node
from celery.result import AsyncResult


class NodeAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.node1 = Node.objects.create(name="Node1")
        self.node2 = Node.objects.create(name="Node2")
        self.node3 = Node.objects.create(name="Node3")
        self.node4 = Node.objects.create(name="Node4")

        self.node1.connections.add(self.node2)
        self.node2.connections.add(self.node3)

    def _parse_response(self, response):
        return json.loads(response.content.decode("utf-8"))

    def test_create_node_success(self):
        url = reverse("create_node")
        data = {"name": "NewNode"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        response_data = self._parse_response(response)
        self.assertEqual(response_data["name"], "NewNode")
        self.assertTrue(Node.objects.filter(name="NewNode").exists())

    def test_create_node_duplicate(self):
        url = reverse("create_node")
        data = {"name": "Node1"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)
        response_data = self._parse_response(response)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Node with this name already exists")

    def test_create_node_missing_name(self):
        url = reverse("create_node")
        data = {}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = self._parse_response(response)
        self.assertIn("error", response_data)
        self.assertIn("name", response_data["error"])

    def test_connect_nodes_success(self):
        url = reverse("connect_nodes")
        data = {"FromNode": "Node1", "ToNode": "Node4"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertIn("message", response_data)
        self.assertTrue(self.node4 in self.node1.connections.all())

    def test_connect_nodes_already_connected(self):
        url = reverse("connect_nodes")
        data = {"FromNode": "Node1", "ToNode": "Node2"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertIn("message", response_data)

    def test_connect_nodes_missing_parameters(self):
        url = reverse("connect_nodes")
        data = {"FromNode": "Node1"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = self._parse_response(response)
        self.assertIn("error", response_data)
        self.assertIn("ToNode", response_data["error"])

    def test_connect_nodes_nonexistent_nodes(self):
        url = reverse("connect_nodes")
        data = {"FromNode": "Node1", "ToNode": "NonExistent"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        response_data = self._parse_response(response)
        self.assertIn("detail", response_data)
        self.assertEqual(response_data["detail"], "No Node matches the given query.")

    def test_find_path_direct_connection(self):
        url = reverse("find_path") + "?FromNode=Node1&ToNode=Node2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertEqual(response_data["path"], ["Node1", "Node2"])

    def test_find_path_indirect_connection(self):
        url = reverse("find_path") + "?FromNode=Node1&ToNode=Node3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertEqual(response_data["path"], ["Node1", "Node2", "Node3"])

    def test_find_path_no_connection(self):
        url = reverse("find_path") + "?FromNode=Node1&ToNode=Node4"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertIsNone(response_data["path"])

    def test_find_path_same_node(self):
        url = reverse("find_path") + "?FromNode=Node1&ToNode=Node1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertEqual(response_data["path"], ["Node1"])

    def test_find_path_missing_parameters(self):
        url = reverse("find_path") + "?FromNode=Node1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        response_data = self._parse_response(response)
        self.assertIn("error", response_data)
        self.assertIn("ToNode", response_data["error"])

    def test_find_path_nonexistent_nodes(self):
        url = reverse("find_path") + "?FromNode=X&ToNode=Y"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertIsNone(response_data["path"])

    def test_slow_find_path_success(self):
        url = reverse("slow_find_path")
        data = {"FromNode": "Node1", "ToNode": "Node3"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 202)
        response_data = self._parse_response(response)
        self.assertIn("task_id", response_data)

        task = AsyncResult(response_data["task_id"])
        self.assertFalse(task.ready())

    def test_slow_find_path_missing_parameters(self):
        url = reverse("slow_find_path")
        data = {"FromNode": "Node1"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = self._parse_response(response)
        self.assertIn("error", response_data)
        self.assertIn("ToNode", response_data["error"])

    def test_get_slow_path_result_pending(self):
        slow_path_url = reverse("slow_find_path")
        data = {"FromNode": "Node1", "ToNode": "Node3"}
        task_response = self.client.post(
            slow_path_url, data=json.dumps(data), content_type="application/json"
        )
        task_id = self._parse_response(task_response)["task_id"]

        url = reverse("get_slow_path_result") + f"?task_id={task_id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertEqual(response_data["status"], "PENDING")

    def test_get_slow_path_result_missing_task_id(self):
        url = reverse("get_slow_path_result")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        response_data = self._parse_response(response)
        self.assertIn("error", response_data)
        self.assertIn("task_id", response_data["error"])

    def test_get_slow_path_result_invalid_task_id(self):
        url = reverse("get_slow_path_result") + "?task_id=invalid_id"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = self._parse_response(response)
        self.assertEqual(response_data["status"], "PENDING")
