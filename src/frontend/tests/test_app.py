import json
import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_validate_missing_data(self):
        """Test validation with missing data"""
        response = self.app.post('/api/validate',
                               content_type='application/json',
                               data=json.dumps({}))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_validate_invalid_email(self):
        """Test validation with invalid email"""
        test_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'age': 25
        }
        response = self.app.post('/api/validate',
                               content_type='application/json',
                               data=json.dumps(test_data))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_validate_invalid_age(self):
        """Test validation with invalid age"""
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'age': -1
        }
        response = self.app.post('/api/validate',
                               content_type='application/json',
                               data=json.dumps(test_data))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main() 