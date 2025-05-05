import unittest
from unittest.mock import patch, MagicMock
import logging
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


from app.services.data_service import CandidateDataService


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



class TestCandidateDataService(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://api.example.com"
        self.service = CandidateDataService(base_api_url=self.base_url)
        self.test_candidate = {
            "id": "123",
            "firstName": "John",
            "lastName": "Doe",
            "cpf": "12345678901",
            "email": "john@example.com",
            "telephone": "11987654321",
            "city": "São Paulo",
            "state": "SP",
            "country": "Brasil",
            "createdAt": "2023-01-01T00:00:00Z",
            "updatedAt": "2023-01-02T00:00:00Z"
        }
        logging.basicConfig(level=logging.CRITICAL)

    def test_example(self):
        """Basic verification test"""
        self.assertTrue(True)

    @patch('requests.Session.get')
    def test_fetch_candidates_success(self, mock_get):
        """Candidates search test"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.test_candidate]
        mock_get.return_value = mock_response

        result = self.service.fetch_candidates_by_lastname("Doe")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["lastName"], "Doe")

if __name__ == '__main__':
    unittest.main()