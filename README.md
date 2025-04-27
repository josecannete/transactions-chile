# Transactions Chile

A command-line tool for converting bank statements from Excel to CSV format with support for several Chilean banks.

## Features

- Convert bank statements from Excel (.xlsx, .xls) files to CSV format
- Support for multiple banks:
  - Santander (Checking Account)
  - Itau (Checking Account, Credit Card - Billed and Unbilled)
  - Banco de Chile (Checking Account, Credit Card - Billed and Unbilled)
- Account type selection:
  - Checking accounts
  - Credit card billed transactions
  - Credit card unbilled (pending) transactions
- Standardized output format with common fields across all banks
- Validation of transaction data
- Customizable delimiter and encoding
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
transactions-chile convert path/to/your/bank-statement.xlsx --bank bchile
```

### List supported banks

View all supported banks and their supported account types:

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
  -b, --bank [santander|itau|bchile]
                                Bank type (required)
  -a, --account-type [checking|credit-billed|credit-unbilled]
                                Account type (checking for 'Cuenta Corriente',
                                credit-billed for 'Tarjeta de Crédito Facturada',
                                credit-unbilled for 'Tarjeta de Crédito No Facturada').
                                If not specified, defaults to the most common type for the selected bank.
  --validate / --no-validate    Validate output against schema before saving
                                (default: validate)
  --help                        Show this message and exit.
```

## Examples

Convert a Santander bank statement (only supports checking account):
```bash
transactions-chile convert santander-checking.xlsx --bank santander
```

Convert a Banco de Chile credit card billed statement (default account type):
```bash
transactions-chile convert bchile-credit-billed.xls --bank bchile
```

Convert a Banco de Chile checking account statement:
```bash
transactions-chile convert bchile-checking.xls --bank bchile --account-type checking
```

Convert a Banco de Chile unbilled credit card statement:
```bash
transactions-chile convert bchile-credit-unbilled.xls --bank bchile --account-type credit-unbilled
```

Convert an Itau credit card statement with a specific output file:
```bash
transactions-chile convert itau-credit-billed.xls --bank itau --output-file itau-credit-processed.csv
```

Convert an Itau statement with a specific sheet:
```bash
transactions-chile convert itau-checking.xlsx --bank itau --sheet-name "Movimientos" --account-type checking
```

Use a different delimiter:
```bash
transactions-chile convert santander-checking.xlsx --bank santander --delimiter ";" --output-file santander_semicolon.csv
```

Force overwrite of existing file:
```bash
transactions-chile convert itau-credit-billed.xlsx --bank itau -f
```

Skip validation:
```bash
transactions-chile convert bchile-checking.xlsx --bank bchile --no-validate
```

## Output Format

The converted CSV files will have the following standardized columns:

- `date`: Transaction date
- `payee`: Name of the transaction payee
- `description`: Transaction description
- `amount`: Transaction amount (positive for credits, negative for debits)
- `city`: Location or branch where transaction occurred (when available)
- `balance`: Account balance after transaction (when available, 0 for credit cards)

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
