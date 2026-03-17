from unittest.mock import patch

from django.test import Client, TestCase


class WeatherViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Weather Assistant")

    def test_get_weather_requires_city(self):
        response = self.client.get("/get-weather/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "City is required.")

    @patch("weather.views.fetch_weather")
    def test_get_weather_returns_json(self, mock_fetch_weather):
        mock_fetch_weather.return_value = {
            "city": "London",
            "country": "GB",
            "current": {"temperature": 10, "humidity": 70, "wind_speed": 4, "condition": "Clouds"},
            "forecast": [],
            "ai_summary": "Mild and cloudy.",
        }

        response = self.client.get("/get-weather/?city=London")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["city"], "London")
