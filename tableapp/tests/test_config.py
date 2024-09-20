import unittest
import config

class TestConfig(unittest.TestCase):

    def test_database_uri(self):
        self.assertEqual(config.SQLALCHEMY_DATABASE_URI, 'sqlite:///skillmap.db')

    def test_debug_mode(self):
        self.assertTrue(config.DEBUG)

    def test_track_modifications(self):
        self.assertTrue(config.SQLALCHEMY_TRACK_MODIFICATIONS)

if __name__ == '__main__':
    unittest.main()