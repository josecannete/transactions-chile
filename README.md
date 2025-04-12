# Transactions Chile - Excel to CSV Converter

A command-line tool for converting Excel files to CSV format with various customization options.

## Features

- Convert Excel (.xlsx, .xls) files to CSV format
- Specify which sheet to convert
- Customize delimiter and encoding
- Rich command-line interface with progress indicators
- Force overwrite option

## Installation

### From PyPI

```bash
pip install transactions-chile
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/transactions-chile.git
cd transactions-chile
pip install -e .
```

## Usage

You can use the tool in two ways:

### As a CLI command

Once installed, you can use the `excel2csv` command directly:

```bash
excel2csv path/to/your/file.xlsx -o output.csv
```

### From Python code

```python
from transactions_chile import convert_excel_to_csv

result = convert_excel_to_csv(
    input_file="path/to/your/file.xlsx",
    output_file="output.csv",
    sheet=0,  # First sheet (0-based index)
    delimiter=",",
    encoding="utf-8"
)
```

## Command Line Options

```
Usage: excel2csv [OPTIONS] INPUT_FILE

  Convert an Excel file to CSV format.

  INPUT_FILE: Path to the Excel file to convert.

Options:
  -o, --output-file PATH       Output CSV file path. If not specified, will use
                               the input filename with .csv extension.
  -s, --sheet TEXT             Sheet name or index (0-based) to convert.
                               Defaults to first sheet.
  -d, --delimiter TEXT         Delimiter to use in the CSV file. Defaults to
                               comma.
  -e, --encoding TEXT          Encoding for the output CSV file. Defaults to
                               utf-8.
  -f, --force                  Overwrite output file if it already exists.
  --help                       Show this message and exit.
```

## Examples

Convert the first sheet of an Excel file:
```bash
excel2csv data.xlsx
```

Convert a specific sheet by name:
```bash
excel2csv data.xlsx --sheet "Sales Data"
```

Use a different delimiter:
```bash
excel2csv data.xlsx --delimiter ";" --output-file data_semicolon.csv
```

Force overwrite of existing file:
```bash
excel2csv data.xlsx -f
```

## Development

### Setting up development environment

1. Clone the repository
2. Create and activate a virtual environment
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running tests

```bash
pytest
```

### Building the package

```bash
python -m build
```

## License

MIT
