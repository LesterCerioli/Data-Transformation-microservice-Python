import uuid
from unittest import TestCase
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.models.import_job import ImportJob
from app.models.organization import Organization
from app.services.import_service import ImportService


class TestImportService(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock(spec=Session)
        self.service = ImportService(db=self.mock_db)
                
        self.valid_org_id1 = uuid.uuid4()
        self.valid_org_id2 = uuid.uuid4()
        self.invalid_org_id = uuid.uuid4()
                
        self.valid_api_key = "valid-key-123"
        self.invalid_api_key = "invalid-key-456"

    @patch('app.services.import_service.verify_api_key')
    def test_verify_organization_access_success(self, mock_verify):
        """Test successful organization access verification"""
        
        mock_verify.return_value = True
                
        mock_source_org = Organization(id=self.valid_org_id1, is_active=True)
        mock_dest_org = Organization(id=self.valid_org_id2, is_active=True)
        
        
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_source_org,
            mock_dest_org
        ]
                
        result = self.service.verify_organization_access(
            api_key=self.valid_api_key,
            source_org_id=self.valid_org_id1,
            destination_org_id=self.valid_org_id2
        )
                
        self.assertTrue(result)
        mock_verify.assert_called_once_with(self.valid_api_key)

    @patch('app.services.import_service.verify_api_key')
    def test_verify_organization_access_invalid_api_key(self, mock_verify):
        """Test with invalid API key"""
        mock_verify.return_value = False
        
        result = self.service.verify_organization_access(
            api_key=self.invalid_api_key,
            source_org_id=self.valid_org_id1,
            destination_org_id=self.valid_org_id2
        )
        
        self.assertFalse(result)
        mock_verify.assert_called_once_with(self.invalid_api_key)

    @patch('app.services.import_service.verify_api_key')
    def test_verify_organization_access_missing_source_org(self, mock_verify):
        """Test when source organization doesn't exist"""
        mock_verify.return_value = True
                
        mock_dest_org = Organization(id=self.valid_org_id2, is_active=True)
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,  # Source org not found
            mock_dest_org
        ]
        
        result = self.service.verify_organization_access(
            api_key=self.valid_api_key,
            source_org_id=self.invalid_org_id,
            destination_org_id=self.valid_org_id2
        )
        
        self.assertFalse(result)

    @patch('app.services.import_service.verify_api_key')
    def test_verify_organization_access_inactive_org(self, mock_verify):
        """Test with inactive organization"""
        mock_verify.return_value = True
                
        mock_source_org = Organization(id=self.valid_org_id1, is_active=False)
        mock_dest_org = Organization(id=self.valid_org_id2, is_active=True)
        
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_source_org,
            mock_dest_org
        ]
        
        result = self.service.verify_organization_access(
            api_key=self.valid_api_key,
            source_org_id=self.valid_org_id1,
            destination_org_id=self.valid_org_id2
        )
        
        self.assertFalse(result)

    @patch('app.services.import_service.verify_api_key')
    def test_verify_organization_access_db_error(self, mock_verify):
        """Test handling of database errors"""
        mock_verify.return_value = True
        self.mock_db.query.side_effect = Exception("DB connection failed")
        
        result = self.service.verify_organization_access(
            api_key=self.valid_api_key,
            source_org_id=self.valid_org_id1,
            destination_org_id=self.valid_org_id2
        )
        
        self.assertFalse(result)

    def test_get_import_job_found(self):
        """Test retrieving an existing import job"""
        
        job_id = uuid.uuid4()
        mock_job = ImportJob(id=job_id)
                
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_job
                
        result = self.service.get_import_job(job_id)
                
        self.assertEqual(result, mock_job)
        self.mock_db.query.assert_called_once_with(ImportJob)
        self.mock_db.query.return_value.filter.assert_called_once()

    def test_get_import_job_not_found(self):
        """Test retrieving a non-existent import job"""
        job_id = uuid.uuid4()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.service.get_import_job(job_id)
        
        self.assertIsNone(result)