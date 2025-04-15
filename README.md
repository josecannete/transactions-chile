# Transactions Chile

A command-line tool for converting bank statements from Excel to CSV format with support for several Chilean banks.

## Features

- Convert bank statements from Excel (.xlsx, .xls) files to CSV format
- Support for multiple banks:
  - Santander (Checking Account)
  - Itau (Credit Card and Checking Account)
  - Banco Chile (Credit Card and Checking Account)
- Account type selection (checking or credit card)
- Validation of transaction data
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

Once installed, you can use the tool in the following ways:

### Convert bank statements

Convert a bank statement from Excel to CSV:

```bash
transactions-chile convert path/to/your/bank-statement.xlsx --bank santander
```

### List supported banks

View all supported banks:

```bash
transactions-chile supported-banks
```

## Command Line Options

```
Usage: transactions-chile convert [OPTIONS] INPUT_FILE

  Convert an Excel file to CSV format using specific bank transaction processors.

  INPUT_FILE: Path to the Excel file to convert.

Options:
  -o, --output-file PATH        Output CSV file path. If not specified, will use
                                the input filename with .csv extension.
  -s, --sheet-name TEXT         Sheet name or index (0-based) to convert.
                                Defaults to first sheet.
  -d, --delimiter TEXT          Delimiter to use in the CSV file. Defaults to
                                comma.
  -e, --encoding TEXT           Encoding for the output CSV file. Defaults to
                                utf-8.
  -f, --force                   Overwrite output file if it already exists.
  -b, --bank [santander|itau|bancochile]
                                Bank type (required)
  -a, --account-type [checking|credit]
                                Account type (checking for 'Cuenta Corriente', 
                                credit for 'Tarjeta de Crédito'). If not specified,
                                defaults to the most common type for the selected bank.
  --validate / --no-validate    Validate output against schema before saving
                                (default: validate)
  --help                        Show this message and exit.
```

## Examples

Convert a Santander bank statement:
```bash
transactions-chile convert santander.xlsx --bank santander
```

Convert a Banco Chile credit card statement (default account type):
```bash
transactions-chile convert bancochile.xls --bank bancochile
```

Convert a Banco Chile checking account statement:
```bash
transactions-chile convert bancochile-cc.xls --bank bancochile --account-type checking
```

Convert an Itau credit card statement with a specific output file:
```bash
transactions-chile convert itau.xls --bank itau --output-file itau-processed.csv
```

Convert a Banco Chile statement with a specific sheet:
```bash
transactions-chile convert bancochile.xlsx --bank bancochile --sheet-name "Movimientos"
```

Use a different delimiter:
```bash
transactions-chile convert santander.xlsx --bank santander --delimiter ";" --output-file santander_semicolon.csv
```

Force overwrite of existing file:
```bash
transactions-chile convert itau.xlsx --bank itau -f
```

Skip validation:
```bash
transactions-chile convert bancochile.xlsx --bank bancochile --no-validate
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
