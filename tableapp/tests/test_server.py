import unittest
from server import app

class TestServer(unittest.TestCase):

    def test_server_startup(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 404)  # Assuming root endpoint is not defined

if __name__ == '__main__':
    unittest.main()