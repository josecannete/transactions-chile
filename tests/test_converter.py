"""
Tests for the converter module.
"""

import os
import pytest
import pandas as pd
from transactions_chile.converter import convert_excel_to_csv


@pytest.fixture
def temp_excel_file(tmp_path):
    """Create a temporary Excel file for testing."""
    # Create a sample dataframe
    df = pd.DataFrame(
        {
            "Name": ["John", "Alice", "Bob"],
            "Age": [30, 25, 35],
            "City": ["New York", "London", "Berlin"],
        }
    )

    # Save to Excel file
    file_path = tmp_path / "test_data.xlsx"
    df.to_excel(file_path, index=False)

    return file_path


@pytest.fixture
def temp_output_file(tmp_path):
    """Provide a temporary output file path."""
    return tmp_path / "output.csv"


def test_convert_excel_to_csv(temp_excel_file, temp_output_file):
    """Test basic conversion functionality."""
    # Convert Excel to CSV
    result = convert_excel_to_csv(
        input_file=str(temp_excel_file),
        output_file=str(temp_output_file),
    )

    # Assertions
    assert os.path.exists(temp_output_file)
    assert result["rows"] == 3
    assert result["columns"] == 3

    # Check content
    df = pd.read_csv(temp_output_file)
    assert list(df.columns) == ["Name", "Age", "City"]
    assert len(df) == 3


def test_convert_excel_with_custom_delimiter(temp_excel_file, temp_output_file):
    """Test conversion with custom delimiter."""
    # Convert Excel to CSV with semicolon delimiter
    convert_excel_to_csv(
        input_file=str(temp_excel_file),
        output_file=str(temp_output_file),
        delimiter=";",
    )

    # Read with correct delimiter
    with open(temp_output_file, "r") as f:
        first_line = f.readline().strip()

    # Check delimiter was applied
    assert ";" in first_line
    assert "," not in first_line
