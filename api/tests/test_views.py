from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Project


class ProjectTests(APITestCase):
    def setUp(self):
        self.project_data = {"name": "Test Project", "description": "Test Description"}
        self.project = Project.objects.create(**self.project_data)

    def test_create_project(self):
        """
        Ensure we can create a new project.
        """
        url = reverse("project-list")
        data = {"name": "New Project", "description": "New Description"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(
            Project.objects.get(id=response.data["id"]).name, "New Project"
        )

    def test_get_project_list(self):
        """
        Ensure we can get the project list.
        """
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project_detail(self):
        """
        Ensure we can get a project by ID.
        """
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.project_data["name"])

    def test_update_project(self):
        """
        Ensure we can update a project.
        """
        url = reverse("project-detail", args=[self.project.id])
        updated_data = {"name": "Updated Project", "description": "Updated Description"}
        response = self.client.put(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], updated_data["name"])

    def test_delete_project(self):
        """
        Ensure we can delete a project.
        """
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)
