"""
Excel to CSV converter module.
Contains functions for converting Excel files to CSV format.
"""

import pandas as pd
from typing import Dict, Union, Any


def convert_excel_to_csv(
    input_file: str,
    output_file: str,
    sheet: Union[int, str] = 0,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Convert an Excel file to CSV format.

    Args:
        input_file: Path to the Excel file to convert
        output_file: Path where the CSV file will be saved
        sheet: Sheet name or index (0-based) to convert
        delimiter: Delimiter to use in the CSV file
        encoding: Encoding for the output CSV file

    Returns:
        Dict containing metadata about the conversion
    """
    try:
        # Read the Excel file
        df = pd.read_excel(input_file, sheet_name=sheet)

        # Write to CSV
        df.to_csv(output_file, sep=delimiter, encoding=encoding, index=False)

        # Return metadata about the conversion
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "input_file": input_file,
            "output_file": output_file,
            "sheet": sheet,
        }

    except Exception as e:
        raise Exception(f"Failed to convert Excel to CSV: {str(e)}")
