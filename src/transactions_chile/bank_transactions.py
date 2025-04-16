from abc import ABC, abstractmethod
from typing import Self, Dict, Any
import pandera as pa
import pandas as pd


STANDARD_COLUMNS = ["date", "payee", "description", "amount", "city", "balance"]


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
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get bank-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {}

    @classmethod
    def from_excel(cls, input_file: str, sheet_name: int = 0) -> Self:
        """
        Read transactions from an Excel file using bank-specific parameters.

        Args:
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0 (first sheet).

        Returns:
            Self: Instance of the class with loaded transactions.
        """
        excel_params = cls.get_excel_parameters()
        transactions_df = pd.read_excel(
            input_file, sheet_name=sheet_name, **excel_params
        )
        return cls(transactions_df, convert=True)

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


class SantanderBankTransactions(BankTransactions, ABC):
    """Base class for handling transactions from Santander Bank."""

    @property
    def bank_name(self) -> str:
        return "Santander"


class SantanderCheckingAccountBankTransactions(SantanderBankTransactions):
    """Class for handling transactions from Santander Bank Checking Account."""

    @property
    def account_type(self) -> str:
        return "Checking Account"

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Santander-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 1, "header": 1}

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
        transactions_df["payee"] = transactions_df["description"]
        transactions_df["balance"] = transactions_df["Saldo ($)"]
        transactions_df["city"] = ""

        return transactions_df[STANDARD_COLUMNS]


class ItauBankTransactions(BankTransactions, ABC):
    """Base class for handling transactions from Itau Bank."""

    @property
    def bank_name(self) -> str:
        return "Itau"


class ItauCreditCardBankTransactions(ItauBankTransactions):
    """Class for handling transactions from Itau Bank Credit Card."""

    @property
    def account_type(self) -> str:
        return "Credit Card"

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Itau Credit Card-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 9, "skipfooter": 5}

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
        transactions_df["payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = -transactions_df["Monto"]
        transactions_df["city"] = transactions_df["Ciudad"]
        transactions_df["balance"] = 0
        return transactions_df[STANDARD_COLUMNS]


class ItauCheckingAccountBankTransactions(ItauBankTransactions):
    """Class for handling transactions from Itau Bank Checking Account."""

    @property
    def account_type(self) -> str:
        return "Checking Account"

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Itau Checking Account-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 10, "skipfooter": 5}

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
        transactions_df["payee"] = transactions_df["Movimientos"]
        transactions_df["amount"] = transactions_df["Abonos"].fillna(
            0
        ) - transactions_df["Cargos"].fillna(0)
        transactions_df["amount"] = transactions_df["amount"].astype(int)
        transactions_df["city"] = ""
        transactions_df["balance"] = transactions_df["Saldo"]
        return transactions_df[STANDARD_COLUMNS]


class BancoChileBankTransactions(BankTransactions, ABC):
    """Base class for handling transactions from Banco Chile."""

    @property
    def bank_name(self) -> str:
        return "Banco de Chile"


class BancoChileCreditCardBankTransactions(BancoChileBankTransactions):
    """Class for handling transactions from Banco Chile Credit Card."""

    @property
    def account_type(self) -> str:
        return "Credit Card"

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Banco Chile Credit Card-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 17}

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
        transactions_df["payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = -transactions_df["Unnamed: 10"]
        transactions_df["city"] = transactions_df["Ciudad"]
        transactions_df["balance"] = 0
        return transactions_df[STANDARD_COLUMNS]


class BancoChileCheckingAccountBankTransactions(BancoChileBankTransactions):
    """Class for handling transactions from Banco Chile Checking Account."""

    @property
    def account_type(self) -> str:
        return "Checking Account"

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Banco Chile Checking Account-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 26, "skipfooter": 7}

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
        transactions_df["payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = transactions_df["Abonos (CLP)"].fillna(
            0
        ) - transactions_df["Cargos (CLP)"].fillna(0)
        transactions_df["amount"] = transactions_df["amount"].astype(int)
        transactions_df["city"] = transactions_df["Canal o Sucursal"]
        transactions_df["balance"] = transactions_df["Saldo (CLP)"]
        return transactions_df[STANDARD_COLUMNS]
