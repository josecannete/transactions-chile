"""
Excel to CSV converter CLI.
A command-line tool for converting Excel files to CSV format.
"""

import os
import sys
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .bank_transactions import (
    SantanderBankTransactions,
    ItauTCBankTransactions,
    ItauCCBankTransactions,
    BancoChileTCBankTransactions,
    BancoChileCCBankTransactions,
)
from .schemas import BankTransactionsSchema

console = Console()

# Define account type constants
ACCOUNT_TYPE_CHECKING = "checking"
ACCOUNT_TYPE_CREDIT = "credit"

# Map of supported banks and account types to their respective classes
BANK_CLASSES = {
    "santander": {
        ACCOUNT_TYPE_CHECKING: SantanderBankTransactions,
    },
    "itau": {
        ACCOUNT_TYPE_CREDIT: ItauTCBankTransactions,
        ACCOUNT_TYPE_CHECKING: ItauCCBankTransactions,
    },
    "bancochile": {
        ACCOUNT_TYPE_CREDIT: BancoChileTCBankTransactions,
        ACCOUNT_TYPE_CHECKING: BancoChileCCBankTransactions,
    },
}

# List of supported banks (for CLI choices)
SUPPORTED_BANKS = list(BANK_CLASSES.keys())

# Get supported account types for each bank
SUPPORTED_ACCOUNT_TYPES = {
    bank: list(account_types.keys()) for bank, account_types in BANK_CLASSES.items()
}

# Default account type for each bank
DEFAULT_ACCOUNT_TYPES = {
    "santander": ACCOUNT_TYPE_CHECKING,
    "itau": ACCOUNT_TYPE_CREDIT,
    "bancochile": ACCOUNT_TYPE_CREDIT,
}


@click.group()
def cli():
    """
    Transactions Chile - Convert bank statements from Excel to CSV format.
    """
    pass


@cli.command(name="convert")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Output CSV file path. If not specified, will use the input filename with .csv extension.",
)
@click.option(
    "--sheet-name",
    "-s",
    default=0,
    help="Sheet name or index (0-based) to convert. Defaults to first sheet.",
)
@click.option(
    "--delimiter",
    "-d",
    default=",",
    help="Delimiter to use in the CSV file. Defaults to comma.",
)
@click.option(
    "--encoding",
    "-e",
    default="utf-8",
    help="Encoding for the output CSV file. Defaults to utf-8.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite output file if it already exists.",
)
@click.option(
    "--bank",
    "-b",
    type=click.Choice(SUPPORTED_BANKS, case_sensitive=False),
    help="Bank type (santander, itau, bancochile)",
    required=True,
)
@click.option(
    "--account-type",
    "-a",
    type=click.Choice(
        [ACCOUNT_TYPE_CHECKING, ACCOUNT_TYPE_CREDIT], case_sensitive=False
    ),
    help="Account type (checking for 'Cuenta Corriente', credit for 'Tarjeta de Crédito'). "
    "If not specified, defaults to the most common type for the selected bank.",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate output against schema before saving (default: validate)",
)
def convert(
    input_file,
    output_file,
    sheet_name,
    delimiter,
    encoding,
    force,
    bank,
    account_type,
    validate,
):
    """Convert an Excel file to CSV format using specific bank transaction processors.

    INPUT_FILE: Path to the Excel file to convert.
    """
    try:
        # Generate default output filename if not provided
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.csv"

        # Check if output file already exists
        if os.path.exists(output_file) and not force:
            if not click.confirm(
                f"Output file '{output_file}' already exists. Overwrite?",
                default=False,
            ):
                console.print("[bold red]Operation cancelled.[/bold red]")
                return 1

        # Use default account type if not specified
        if account_type is None:
            account_type = DEFAULT_ACCOUNT_TYPES[bank.lower()]

        # Get the appropriate bank transaction class
        bank_key = bank.lower()
        account_type_key = account_type.lower()

        if bank_key not in BANK_CLASSES:
            console.print(f"[bold red]Error:[/bold red] Unsupported bank type: {bank}")
            return 1

        if account_type_key not in BANK_CLASSES[bank_key]:
            console.print(
                f"[bold red]Error:[/bold red] Unsupported account type '{account_type}' for bank '{bank}'"
            )
            console.print(
                f"Supported account types for {bank}: {', '.join(SUPPORTED_ACCOUNT_TYPES[bank_key])}"
            )
            return 1

        bank_class = BANK_CLASSES[bank_key][account_type_key]

        with Progress(
            SpinnerColumn(),
            TextColumn(
                f"[bold blue]Processing {bank.title()} {account_type} transactions...[/bold blue]"
            ),
            transient=True,
        ) as progress:
            task = progress.add_task("Processing", total=None)

            # Load and process transactions using the appropriate bank class
            try:
                transactions = bank_class.from_excel(
                    input_file=input_file, sheet_name=sheet_name
                )
            except Exception as e:
                console.print(f"[bold red]Error processing file:[/bold red] {str(e)}")
                return 1

            progress.update(task, completed=True)

        console.print(
            f"[bold cyan]Bank:[/bold cyan] {transactions.bank_name} - {transactions.account_type}"
        )
        console.print(
            f"[bold cyan]Transactions:[/bold cyan] {len(transactions.transactions)} records"
        )

        # Save the results, with optional validation
        if validate:
            console.print("[bold blue]Validating transactions...[/bold blue]")
            success = transactions.validate_and_save(
                schema=BankTransactionsSchema, output_file=output_file
            )
            if success:
                console.print("[bold green]✓[/bold green] Validation successful")
            else:
                console.print("[bold red]✗[/bold red] Validation failed")
                return 1
        else:
            transactions.to_csv(output_file, delimiter=delimiter, encoding=encoding)

        console.print(
            f"[bold green]✓[/bold green] Successfully processed: {input_file}"
        )
        console.print(f"[bold green]✓[/bold green] Output saved to: {output_file}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1

    return 0


@cli.command(name="supported-banks")
def supported_banks():
    """List all supported banks."""
    console.print("[bold cyan]Supported Banks:[/bold cyan]")
    for bank in SUPPORTED_BANKS:
        account_types = SUPPORTED_ACCOUNT_TYPES[bank]
        account_types_str = ", ".join(account_types)
        console.print(
            f"  • {bank.title()} [Supported account types: {account_types_str}]"
        )
    return 0


def main():
    """Entry point for the CLI."""
    try:
        return cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
