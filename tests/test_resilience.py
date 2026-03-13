import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from pysecop.client import SecopClient
from pysecop.config import DatasetConfig, DATASETS

class TestSchemaResilience(unittest.TestCase):
    def setUp(self):
        self.mock_config = DatasetConfig(
            id="test-id",
            name="Test Dataset",
            description="Test Description",
            columns=["col1", "col2", "col3"]
        )
        # Patch the configuration to include our test dataset
        patcher = patch.dict(DATASETS, {"TEST": self.mock_config})
        patcher.start()
        self.addCleanup(patcher.stop)
        
        self.client = SecopClient(app_token="test-token")
        self.client.client = MagicMock()

    def test_fetch_with_missing_field_in_api(self):
        """
        Test that fetch handles cases where a field is missing from the API metadata/response.
        """
        # Mock metadata to only show col1 and col2
        self.client.client.get_metadata.return_value = {
            'columns': [{'fieldName': 'col1'}, {'fieldName': 'col2'}]
        }
        
        # Mock API response to only return col1 and col2
        self.client.client.get.return_value = [{'col1': 'val1', 'col2': 'val2'}]

        # Try to fetch using a query that expects col1, col2, and col3
        from pysecop.query_builder import QueryBuilder
        qb = QueryBuilder().select(["col1", "col2", "col3"])
        
        df = self.client.fetch("TEST", qb)
        
        # Verify that the query sent to Socrata only included available columns
        self.client.client.get.assert_called_once_with(
            "test-id", 
            query="select col1, col2", 
            content_type="json"
        )
        
        # Verify that the resulting DataFrame has all 3 columns
        self.assertIn("col1", df.columns)
        self.assertIn("col2", df.columns)
        self.assertIn("col3", df.columns)
        self.assertEqual(df["col1"].iloc[0], "val1")
        self.assertEqual(df["col2"].iloc[0], "val2")
        self.assertTrue(pd.isna(df["col3"].iloc[0]))

    @patch('pysecop.client.logger')
    def test_fetch_warning_for_missing_field(self, mock_logger):
        """
        Test that a warning is logged when fields are missing.
        """
        self.client.client.get_metadata.return_value = {
            'columns': [{'fieldName': 'col1'}]
        }
        self.client.client.get.return_value = [{'col1': 'val1'}]

        from pysecop.query_builder import QueryBuilder
        qb = QueryBuilder().select(["col1", "col2"])
        
        self.client.fetch("TEST", qb)
        
        # Check if warning was called
        mock_logger.warning.assert_any_call("Fields missing from API in TEST: {'col2'}")

if __name__ == '__main__':
    unittest.main()
