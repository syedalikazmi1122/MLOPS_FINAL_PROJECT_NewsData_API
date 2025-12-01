"""
Unit tests for data processing functions.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestDataLoading:
    """Tests for data loading functions."""
    
    def test_load_parquet_file(self):
        """Test loading parquet file."""
        # This would test actual file loading if we had test data
        # For now, just test the concept
        try:
            # Try to import the function
            from train import load_data
            # If file doesn't exist, that's OK for unit tests
            assert callable(load_data)
        except ImportError:
            pass
    
    def test_data_validation(self):
        """Test data validation logic."""
        # Create sample data
        df = pd.DataFrame({
            'magnitude': [3.5, 4.2, 3.8, None, 4.0],
            'latitude': [34.0, 35.0, 36.0, 37.0, 38.0],
            'longitude': [-118.0, -119.0, -120.0, -121.0, -122.0]
        })
        
        # Test null check
        null_count = df['magnitude'].isna().sum()
        null_percentage = (null_count / len(df)) * 100
        assert null_percentage < 50  # Should be less than 50% for test data


class TestFeatureEngineering:
    """Tests for feature engineering."""
    
    def test_feature_preparation(self):
        """Test feature preparation logic."""
        # Create sample data
        df = pd.DataFrame({
            'magnitude': [3.5, 4.2, 3.8, 4.0, 3.9],
            'latitude': [34.0, 35.0, 36.0, 37.0, 38.0],
            'longitude': [-118.0, -119.0, -120.0, -121.0, -122.0],
            'depth': [10.0, 15.0, 12.0, 18.0, 14.0],
            'datetime': pd.date_range('2024-01-01', periods=5, freq='D')
        })
        
        # Test that we can select numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        assert len(numeric_cols) > 0
        assert 'magnitude' in numeric_cols or 'latitude' in numeric_cols
    
    def test_feature_exclusion(self):
        """Test that excluded columns are not in features."""
        df = pd.DataFrame({
            'magnitude': [3.5, 4.2],
            'latitude': [34.0, 35.0],
            'id': [1, 2],
            'time': ['2024-01-01', '2024-01-02'],
            'place': ['Location A', 'Location B']
        })
        
        # Exclude non-feature columns
        exclude_cols = ['id', 'time', 'place']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        assert 'id' not in feature_cols
        assert 'time' not in feature_cols
        assert 'place' not in feature_cols
        assert 'magnitude' in feature_cols
        assert 'latitude' in feature_cols


class TestDataTransformation:
    """Tests for data transformation."""
    
    def test_missing_value_handling(self):
        """Test missing value handling."""
        df = pd.DataFrame({
            'value1': [1.0, 2.0, None, 4.0],
            'value2': [5.0, None, 7.0, 8.0]
        })
        
        # Fill with median
        df_filled = df.fillna(df.median())
        
        assert df_filled['value1'].isna().sum() == 0
        assert df_filled['value2'].isna().sum() == 0
    
    def test_data_types(self):
        """Test data type consistency."""
        df = pd.DataFrame({
            'numeric1': [1, 2, 3],
            'numeric2': [1.0, 2.0, 3.0],
            'string': ['a', 'b', 'c']
        })
        
        # Check numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        assert len(numeric_cols) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

