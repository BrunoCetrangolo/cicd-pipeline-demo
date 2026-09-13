import unittest
from app import app, get_version


class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_get_version_defaults_to_dev(self):
        self.assertEqual(get_version(), "dev")


if __name__ == "__main__":
    unittest.main()
