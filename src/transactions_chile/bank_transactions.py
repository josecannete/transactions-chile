from abc import ABC, abstractmethod
from typing import Self
import pandera as pa
import pandas as pd


class BankTransactions(ABC):
    """Base class for handling bank transactions."""

    def __init__(self, transactions: pd.DataFrame, convert: bool = True) -> None:
        """
        Initialize the BankTransactions class.

        Args:
            transactions (pd.DataFrame): DataFrame containing transactions.
            convert (bool, optional): Whether to convert the DataFrame format. Defaults to True.
        """
        self.transactions = transactions
        if convert:
            self.transactions = self._convert_dataframe(transactions)

    @property
    @abstractmethod
    def bank_name(self) -> str:
        """
        Get the bank name.

        Returns:
            str: Name of the bank.
        """
        pass

    @property
    @abstractmethod
    def account_type(self) -> str:
        """
        Get the account type.

        Returns:
            str: Type of the account.
        """
        pass

    @classmethod
    @abstractmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from an Excel file.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0 (first sheet).

        Returns:
            Self: Instance of the class with loaded transactions.
        """
        pass

    def to_csv(
        self, output_file: str, delimiter: str = ",", encoding: str = "utf-8"
    ) -> None:
        """
        Write transactions to a CSV file.

        Args:
            output_file (str): Path to the output CSV file.
            delimiter (str, optional): Delimiter for the CSV file. Defaults to ','.
            encoding (str, optional): Encoding for the CSV file. Defaults to 'utf-8'.
        """
        self.transactions.to_csv(
            output_file, sep=delimiter, encoding=encoding, index=False
        )

    @abstractmethod
    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the DataFrame to a standardized format.

        Args:
            transactions_df (pd.DataFrame): Original DataFrame with bank-specific format.

        Returns:
            pd.DataFrame: Standardized DataFrame with common fields.
        """
        pass

    def validate(self, schema: pa.DataFrameModel) -> bool:
        """
        Validate the transactions against a schema.

        Args:
            schema (pa.DataFrameModel): Schema to validate against.

        Returns:
            bool: True if valid, False otherwise.
        """
        schema.validate(self.transactions)
        return True

    def validate_and_save(self, schema: pa.DataFrameModel, output_file: str) -> bool:
        """
        Validate the transactions and save to a CSV file if valid.

        Args:
            schema (pa.DataFrameModel): Schema to validate against.
            output_file (str): Path to the output CSV file.

        Returns:
            bool: True if valid and saved, False otherwise.
        """
        if self.validate(schema):
            self.to_csv(output_file)
            return True
        return False


class SantanderBankTransactions(BankTransactions):
    """Class for handling transactions from Santander Bank."""

    @property
    def bank_name(self) -> str:
        return "Santander"

    @property
    def account_type(self) -> str:
        return "Cuenta Corriente"

    @classmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from a Santander Bank Excel file.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0.

        Returns:
            Self: Instance with loaded transactions.
        """
        transactions_df = pd.read_excel(
            input_file, sheet_name=sheet_name, skiprows=1, header=1
        )
        return cls(transactions_df, convert=True)

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Santander Bank transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Santander transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        transactions_df = transactions_df.fillna(0)
        transactions_df["amount"] = (
            transactions_df["Monto abono ($)"] - transactions_df["Monto cargo ($)"]
        ).astype(int)
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha"], format="%d-%m-%Y"
        )
        transactions_df["description"] = transactions_df["Detalle"]
        transactions_df["imported_payee"] = transactions_df["description"]
        transactions_df["balance"] = transactions_df["Saldo ($)"]
        transactions_df["city"] = ""

        return transactions_df[
            ["date", "imported_payee", "description", "amount", "balance", "city"]
        ]


class ItauBankTransactions(BankTransactions, ABC):
    """Base class for handling transactions from Itau Bank."""

    @property
    def bank_name(self) -> str:
        return "Itau"


class ItauTCBankTransactions(ItauBankTransactions):
    """Class for handling transactions from Itau Bank Tarjeta de Crédito."""

    @property
    def account_type(self) -> str:
        return "Tarjeta de Crédito"

    @classmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from an Itau Bank Excel file.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0.

        Returns:
            Self: Instance with loaded transactions.
        """
        transactions_df = pd.read_excel(
            input_file, sheet_name=sheet_name, skiprows=9, skipfooter=5
        )
        return cls(transactions_df, convert=True)

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Itau Bank transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Itau transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha compra"], format="%Y-%m-%d"
        )
        transactions_df["description"] = transactions_df["Descripción"]
        transactions_df["imported_payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = -transactions_df["Monto"]
        transactions_df["city"] = transactions_df["Ciudad"]
        transactions_df["balance"] = 0
        return transactions_df[
            ["date", "imported_payee", "description", "amount", "city", "balance"]
        ]


class ItauCCBankTransactions(ItauBankTransactions):
    """Class for handling transactions from Itau Bank Cuenta Corriente."""

    @property
    def account_type(self) -> str:
        return "Cuenta Corriente"

    @classmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from an Itau Bank Excel file.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0.

        Returns:
            Self: Instance with loaded transactions.
        """
        transactions_df = pd.read_excel(
            input_file, sheet_name=sheet_name, skiprows=10, skipfooter=5
        )
        return cls(transactions_df, convert=True)

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Itau Bank transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Itau transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha"], format="%Y-%m-%d"
        )
        transactions_df["description"] = transactions_df["Movimientos"]
        transactions_df["imported_payee"] = transactions_df["Movimientos"]
        transactions_df["amount"] = transactions_df["Abonos"].fillna(
            0
        ) - transactions_df["Cargos"].fillna(0)
        transactions_df["amount"] = transactions_df["amount"].astype(int)
        transactions_df["city"] = ""
        transactions_df["balance"] = transactions_df["Saldo"]
        return transactions_df[
            ["date", "imported_payee", "description", "amount", "city", "balance"]
        ]


class BancoChileBankTransactions(BankTransactions, ABC):
    """Base class for handling transactions from Banco Chile."""

    @property
    def bank_name(self) -> str:
        return "Banco de Chile"


class BancoChileTCBankTransactions(BancoChileBankTransactions):
    """Class for handling transactions from Banco Chile Tarjeta de Crédito."""

    @property
    def account_type(self) -> str:
        return "Tarjeta de Crédito"

    @classmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from a Banco Chile Excel file.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0.

        Returns:
            Self: Instance with loaded transactions.
        """
        transactions_df = pd.read_excel(input_file, sheet_name=sheet_name, skiprows=17)
        return cls(transactions_df, convert=True)

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Banco Chile transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Banco Chile transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha"], format="%d/%m/%Y"
        )
        transactions_df["description"] = transactions_df["Descripción"]
        transactions_df["imported_payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = -transactions_df["Unnamed: 10"]
        transactions_df["city"] = transactions_df["Ciudad"]
        transactions_df["balance"] = 0
        return transactions_df[
            ["date", "imported_payee", "description", "amount", "city", "balance"]
        ]


class BancoChileCCBankTransactions(BancoChileBankTransactions):
    """Class for handling transactions from Banco Chile Cuenta Corriente."""

    @property
    def account_type(self) -> str:
        return "Cuenta Corriente"

    @classmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from a Banco Chile Excel file.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0.

        Returns:
            Self: Instance with loaded transactions.
        """
        transactions_df = pd.read_excel(
            input_file, sheet_name=sheet_name, skiprows=26, skipfooter=7
        )
        return cls(transactions_df, convert=True)

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Banco Chile transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Banco Chile transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha"], format="%d/%m/%Y"
        )
        transactions_df["description"] = transactions_df["Descripción"]
        transactions_df["imported_payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = transactions_df["Abonos (CLP)"].fillna(
            0
        ) - transactions_df["Cargos (CLP)"].fillna(0)
        transactions_df["amount"] = transactions_df["amount"].astype(int)
        transactions_df["city"] = transactions_df["Canal o Sucursal"]
        transactions_df["balance"] = transactions_df["Saldo (CLP)"]
        return transactions_df[
            ["date", "imported_payee", "description", "amount", "city", "balance"]
        ]
