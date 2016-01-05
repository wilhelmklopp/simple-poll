from django.test import TestCase

# Create your tests here.


class MainViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("state" in resp.context)

    def test_poll(self):
        resp = self.client.get("/poll/")
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post("/poll/")
        self.assertEqual(resp.status_code, 400)
