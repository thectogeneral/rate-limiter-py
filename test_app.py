import unittest
from flask import Flask
from app import app  # Import the Flask app from your app.py
from limiter import RateLimiter  # Import your rate limiter
import redis  # Import the Redis library

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Set up the test client and initialize any resources needed
        self.app = app.test_client()
        self.app.testing = True

        # Initialize Redis client
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

        # Initialize the rate limiter with the Redis client
        self.limiter = RateLimiter(redis_client=self.redis_client, rate=1, max_tokens=5, refill_interval=1)

    def test_home_page(self):
        # Test the home page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Home Page!', response.data)

    def test_about_page(self):
        # Test the about page
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About Page', response.data)

    def test_rate_limiter(self):
        # Test the rate limiter
        for _ in range(5):
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)

        # 6th request should be blocked by rate limiter
        response = self.app.get('/')
        self.assertEqual(response.status_code, 429)  # HTTP status code 429 for Too Many Requests
        self.assertIn(b'too many requests', response.data.lower())

    def tearDown(self):
        # Clean up any resources if necessary
        pass

if __name__ == '__main__':
    unittest.main()
