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
    ItauBankTransactions,
    BancoChileBankTransactions,
)
from .schemas import BankTransactionsSchema

console = Console()

# Map of supported banks to their respective classes
BANK_CLASSES = {
    "santander": SantanderBankTransactions,
    "itau": ItauBankTransactions,
    "bancochile": BancoChileBankTransactions,
}


@click.command()
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
    type=click.Choice(list(BANK_CLASSES.keys()), case_sensitive=False),
    help="Bank type (santander, itau, bancochile)",
    required=True,
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate output against schema before saving (default: validate)",
)
def main(
    input_file, output_file, sheet_name, delimiter, encoding, force, bank, validate
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

        # Get the appropriate bank transaction class
        bank_class = BANK_CLASSES.get(bank.lower())
        if not bank_class:
            console.print(f"[bold red]Error:[/bold red] Unsupported bank type: {bank}")
            return 1

        with Progress(
            SpinnerColumn(),
            TextColumn(
                f"[bold blue]Processing {bank.title()} transactions...[/bold blue]"
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


if __name__ == "__main__":
    sys.exit(main())
