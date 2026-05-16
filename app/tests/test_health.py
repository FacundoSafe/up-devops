from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from scraper import check_bna_status
from models.health import Dependency, Health


class CheckBnaStatusTest(TestCase):
    @patch("scraper.requests.get")
    def test_status_up_cuando_200(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertEqual(check_bna_status(), "up")

    @patch("scraper.requests.get")
    def test_status_down_cuando_500(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        self.assertEqual(check_bna_status(), "down")

    @patch("scraper.requests.get")
    def test_status_down_cuando_excepcion(self, mock_get):
        mock_get.side_effect = Exception("connection refused")
        self.assertEqual(check_bna_status(), "down")


class HealthViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("routes.health.get_health")
    def test_health_estructura(self, mock_get):
        mock_get.return_value = Health(
            datetime="2026-04-25T10:00:00",
            response_time="0.123s",
            dependencies=[Dependency(name="BNA", status="up")],
        )
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("datetime", response.data)
        self.assertIn("response_time", response.data)
        self.assertIn("dependencies", response.data)

    @patch("routes.health.get_health")
    def test_health_bna_up(self, mock_get):
        mock_get.return_value = Health(
            datetime="2026-04-25T10:00:00",
            response_time="0.100s",
            dependencies=[Dependency(name="BNA", status="up")],
        )
        response = self.client.get("/api/health/")

        dep = response.data["dependencies"][0]
        self.assertEqual(dep["name"], "BNA")
        self.assertEqual(dep["status"], "up")

    @patch("routes.health.get_health")
    def test_health_bna_down(self, mock_get):
        mock_get.return_value = Health(
            datetime="2026-04-25T10:00:00",
            response_time="0.100s",
            dependencies=[Dependency(name="BNA", status="down")],
        )
        response = self.client.get("/api/health/")

        dep = response.data["dependencies"][0]
        self.assertEqual(dep["name"], "BNA")
        self.assertEqual(dep["status"], "down")

    @patch("routes.health.get_health")
    def test_health_response_time_formato(self, mock_get):
        mock_get.return_value = Health(
            datetime="2026-04-25T10:00:00",
            response_time="0.123s",
            dependencies=[Dependency(name="BNA", status="up")],
        )
        response = self.client.get("/api/health/")

        self.assertRegex(response.data["response_time"], r"^\d+\.\d{3}s$")

    def test_health_post_no_permitido(self):
        response = self.client.post("/api/health/", {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
