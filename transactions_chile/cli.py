"""
Excel to CSV converter CLI.
A command-line tool for converting Excel files to CSV format.
"""

import os
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .converter import convert_excel_to_csv

console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Output CSV file path. If not specified, will use the input filename with .csv extension.",
)
@click.option(
    "--sheet",
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
def main(input_file, output_file, sheet, delimiter, encoding, force):
    """Convert an Excel file to CSV format.

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
                return

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Converting Excel to CSV...[/bold blue]"),
            transient=True,
        ) as progress:
            task = progress.add_task("Converting", total=None)

            # Perform the conversion
            result = convert_excel_to_csv(
                input_file=input_file,
                output_file=output_file,
                sheet=sheet,
                delimiter=delimiter,
                encoding=encoding,
            )

            progress.update(task, completed=True)

        console.print(
            f"[bold green]✓[/bold green] Successfully converted: {input_file}"
        )
        console.print(f"[bold green]✓[/bold green] Output saved to: {output_file}")
        console.print(f"[bold green]✓[/bold green] Rows processed: {result['rows']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    main()
