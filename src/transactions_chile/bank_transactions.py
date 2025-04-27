from abc import ABC, abstractmethod
from typing import Self, Dict, Any, Type, Union
from enum import Enum
import pandera as pa
import pandas as pd


class Bank(str, Enum):
    """Enum for supported banks"""

    SANTANDER = "santander"
    ITAU = "itau"
    BANCO_CHILE = "bchile"

    @property
    def display_name(self) -> str:
        """
        Get a human-readable bank name.

        Returns:
            str: The formatted name of the bank.
        """
        display_names = {
            Bank.SANTANDER: "Santander",
            Bank.ITAU: "Itau",
            Bank.BANCO_CHILE: "Banco de Chile",
        }
        return display_names.get(self, self.name.title().replace("_", " "))


class AccountType(str, Enum):
    """Enum for supported account types"""

    CHECKING = "checking"
    CREDIT_BILLED = "credit-billed"
    CREDIT_UNBILLED = "credit-unbilled"

    @property
    def display_name(self) -> str:
        """
        Get a human-readable account type name.

        Returns:
            str: The formatted name of the account type.
        """
        display_names = {
            AccountType.CHECKING: "Checking Account",
            AccountType.CREDIT_BILLED: "Credit Card (Billed)",
            AccountType.CREDIT_UNBILLED: "Credit Card (Unbilled)",
        }
        return display_names.get(self, self.name.title().replace("_", " "))


STANDARD_COLUMNS = ["date", "payee", "description", "amount", "city", "balance"]


class BankMixin(ABC):
    """Abstract base mixin for bank-specific functionality.

    This mixin defines the interface for bank-specific implementations
    and provides common functionality derived from the bank enum.
    """

    @property
    @abstractmethod
    def bank_enum(self) -> Bank:
        """
        Get the bank enum value.

        Returns:
            Bank: The enum value for this bank.
        """
        pass

    @property
    def bank_name(self) -> str:
        """
        Get a human-readable bank name derived from the enum.

        Returns:
            str: The formatted name of the bank.
        """
        return self.bank_enum.display_name


class SantanderBankMixin(BankMixin):
    """Mixin for Santander Bank specific functionality."""

    @property
    def bank_enum(self) -> Bank:
        return Bank.SANTANDER


class ItauBankMixin(BankMixin):
    """Mixin for Itau Bank specific functionality."""

    @property
    def bank_enum(self) -> Bank:
        return Bank.ITAU


class BancoChileBankMixin(BankMixin):
    """Mixin for Banco de Chile specific functionality."""

    @property
    def bank_enum(self) -> Bank:
        return Bank.BANCO_CHILE


class AccountTypeMixin(ABC):
    """Abstract base mixin for account type functionality.

    This mixin defines the interface for account type implementations
    and provides common functionality derived from the account type enum.
    """

    @property
    @abstractmethod
    def account_type_enum(self) -> AccountType:
        """
        Get the account type enum value.

        Returns:
            AccountType: The enum value for this account type.
        """
        pass

    @property
    def account_type(self) -> str:
        """
        Get a human-readable account type name derived from the enum.

        Returns:
            str: The formatted name of the account type.
        """
        return self.account_type_enum.display_name


class CheckingAccountMixin(AccountTypeMixin):
    """Mixin for checking account specific functionality."""

    @property
    def account_type_enum(self) -> AccountType:
        return AccountType.CHECKING


class CreditCardMixin(AccountTypeMixin):
    """Base mixin for credit card functionality."""

    @property
    def is_billed(self) -> bool:
        """
        Determine if the credit card transactions are billed or unbilled.
        This is derived from the account_type_enum property.

        Returns:
            bool: True for billed transactions, False for unbilled
        """
        return self.account_type_enum == AccountType.CREDIT_BILLED


class BilledCreditCardMixin(CreditCardMixin):
    """Mixin for billed credit card transactions."""

    @property
    def account_type_enum(self) -> AccountType:
        return AccountType.CREDIT_BILLED

    @property
    def account_subtype(self) -> str:
        return "Billed"


class UnbilledCreditCardMixin(CreditCardMixin):
    """Mixin for unbilled (pending) credit card transactions."""

    @property
    def account_type_enum(self) -> AccountType:
        return AccountType.CREDIT_UNBILLED

    @property
    def account_subtype(self) -> str:
        return "Unbilled"


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

    @property
    def bank(self) -> Bank:
        """
        Get the bank enum value.
        Only available if a BankMixin is used.

        Returns:
            Bank: The enum value for the bank.

        Raises:
            AttributeError: If not implemented by a mixin
        """
        if hasattr(self, "bank_enum"):
            return self.bank_enum
        raise AttributeError("bank property not implemented")

    @property
    def account_type_value(self) -> AccountType:
        """
        Get the account type enum value.
        Only available if an AccountTypeMixin is used.

        Returns:
            AccountType: The enum value for the account type.

        Raises:
            AttributeError: If not implemented by a mixin
        """
        if hasattr(self, "account_type_enum"):
            return self.account_type_enum
        raise AttributeError("account_type_value property not implemented")

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


class SantanderCheckingAccountBankTransactions(
    SantanderBankMixin, CheckingAccountMixin, BankTransactions
):
    """Class for handling transactions from Santander Bank Checking Account."""

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


class ItauCheckingAccountBankTransactions(
    ItauBankMixin, CheckingAccountMixin, BankTransactions
):
    """Class for handling transactions from Itau Bank Checking Account."""

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


class BancoChileCheckingAccountBankTransactions(
    BancoChileBankMixin, CheckingAccountMixin, BankTransactions
):
    """Class for handling transactions from Banco Chile Checking Account."""

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


class ItauBilledCreditCardBankTransactions(
    ItauBankMixin, BilledCreditCardMixin, BankTransactions
):
    """Class for handling billed transactions from Itau Bank Credit Card."""

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Itau Billed Credit Card-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": list(range(52)) + [53], "skipfooter": 35}

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Itau Bank billed credit card transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Itau transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        transactions_df.dropna(subset=["Monto operación"], inplace=True)
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha operación"], format="%Y-%m-%d"
        )
        transactions_df["description"] = transactions_df[
            "Descripción operación o cobro"
        ]
        transactions_df["payee"] = transactions_df["Descripción operación o cobro"]
        transactions_df["amount"] = -transactions_df["Monto operación"].astype(int)
        transactions_df["city"] = transactions_df["Lugar de operación"]
        transactions_df["balance"] = 0
        return transactions_df[STANDARD_COLUMNS]


class ItauUnbilledCreditCardBankTransactions(
    ItauBankMixin, UnbilledCreditCardMixin, BankTransactions
):
    """Class for handling unbilled (pending) transactions from Itau Bank Credit Card."""

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Itau Unbilled Credit Card-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 9, "skipfooter": 5}  # Same as the original implementation

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Itau Bank unbilled credit card transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Itau unbilled transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        # This is the original implementation from ItauCreditCardBankTransactions
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha compra"], format="%Y-%m-%d"
        )
        transactions_df["description"] = transactions_df["Descripción"]
        transactions_df["payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = -transactions_df["Monto"]
        transactions_df["city"] = transactions_df["Ciudad"]
        transactions_df["balance"] = 0
        return transactions_df[STANDARD_COLUMNS]


class BancoChileBilledCreditCardBankTransactions(
    BancoChileBankMixin, BilledCreditCardMixin, BankTransactions
):
    """Class for handling billed transactions from Banco Chile Credit Card."""

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Banco Chile Billed Credit Card-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 17}

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Banco Chile billed credit card transactions format to standard format.

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
        transactions_df["amount"] = -transactions_df["Monto ($)"]
        transactions_df["city"] = ""
        transactions_df["balance"] = 0
        return transactions_df[STANDARD_COLUMNS]


class BancoChileUnbilledCreditCardBankTransactions(
    BancoChileBankMixin, UnbilledCreditCardMixin, BankTransactions
):
    """Class for handling unbilled (pending) transactions from Banco Chile Credit Card."""

    @classmethod
    def get_excel_parameters(cls) -> Dict[str, Any]:
        """
        Get Banco Chile Unbilled Credit Card-specific Excel loading parameters.

        Returns:
            Dict[str, Any]: Parameters to pass to pd.read_excel
        """
        return {"skiprows": 17}  # Same as the original implementation

    def _convert_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Banco Chile unbilled credit card transactions format to standard format.

        Args:
            transactions_df (pd.DataFrame): Original Banco Chile unbilled transactions.

        Returns:
            pd.DataFrame: Standardized transactions.
        """
        # This is the original implementation from BancoChileCreditCardBankTransactions
        transactions_df["date"] = pd.to_datetime(
            transactions_df["Fecha"], format="%d/%m/%Y"
        )
        transactions_df["description"] = transactions_df["Descripción"]
        transactions_df["payee"] = transactions_df["Descripción"]
        transactions_df["amount"] = -transactions_df["Unnamed: 10"]
        transactions_df["city"] = transactions_df["Ciudad"]
        transactions_df["balance"] = 0
        return transactions_df[STANDARD_COLUMNS]


class BankTransactionsFactory:
    """Factory class for creating bank transaction objects.

    This class centralizes the creation of bank transaction objects based on the bank and account type.
    It decouples the client code from the concrete implementations and makes it easier to add new types.
    """

    _registry: Dict[tuple[Bank, AccountType], Type[BankTransactions]] = {
        (
            Bank.SANTANDER,
            AccountType.CHECKING,
        ): SantanderCheckingAccountBankTransactions,
        (Bank.ITAU, AccountType.CHECKING): ItauCheckingAccountBankTransactions,
        (
            Bank.BANCO_CHILE,
            AccountType.CHECKING,
        ): BancoChileCheckingAccountBankTransactions,
        (Bank.ITAU, AccountType.CREDIT_BILLED): ItauBilledCreditCardBankTransactions,
        (
            Bank.ITAU,
            AccountType.CREDIT_UNBILLED,
        ): ItauUnbilledCreditCardBankTransactions,
        (
            Bank.BANCO_CHILE,
            AccountType.CREDIT_BILLED,
        ): BancoChileBilledCreditCardBankTransactions,
        (
            Bank.BANCO_CHILE,
            AccountType.CREDIT_UNBILLED,
        ): BancoChileUnbilledCreditCardBankTransactions,
    }

    @classmethod
    def create_from_excel(
        cls,
        bank: Union[Bank, str],
        account_type: Union[AccountType, str],
        input_file: str,
        sheet_name: int = 0,
    ) -> BankTransactions:
        """
        Create a bank transactions object from an Excel file.

        Args:
            bank (Union[Bank, str]): The bank type (can be enum or string).
            account_type (Union[AccountType, str]): The account type (can be enum or string).
            input_file (str): Path to the Excel file.
            sheet_name (int, optional): Sheet index to read from. Defaults to 0.

        Returns:
            BankTransactions: The appropriate bank transactions object.

        Raises:
            ValueError: If the bank and account type combination is not supported.
        """
        # Ensure bank and account_type are enums
        if isinstance(bank, str):
            bank = Bank(bank.lower())

        if isinstance(account_type, str):
            account_type = AccountType(account_type.lower())

        # Get the appropriate class based on bank and account type
        transaction_class = cls._registry.get((bank, account_type))

        if transaction_class is None:
            raise ValueError(
                f"Unsupported combination of bank '{bank}' and account type '{account_type}'"
            )

        # Create the instance from the Excel file
        return transaction_class.from_excel(input_file, sheet_name=sheet_name)

    @classmethod
    def create(
        cls,
        bank: Union[Bank, str],
        account_type: Union[AccountType, str],
        transactions_df: pd.DataFrame,
        convert: bool = True,
    ) -> BankTransactions:
        """
        Create a bank transactions object from a DataFrame.

        Args:
            bank (Union[Bank, str]): The bank type (can be enum or string).
            account_type (Union[AccountType, str]): The account type (can be enum or string).
            transactions_df (pd.DataFrame): DataFrame containing transactions.
            convert (bool, optional): Whether to convert the DataFrame format. Defaults to True.

        Returns:
            BankTransactions: The appropriate bank transactions object.

        Raises:
            ValueError: If the bank and account type combination is not supported.
        """
        # Ensure bank and account_type are enums
        if isinstance(bank, str):
            bank = Bank(bank.lower())

        if isinstance(account_type, str):
            account_type = AccountType(account_type.lower())

        # Get the appropriate class based on bank and account type
        transaction_class = cls._registry.get((bank, account_type))

        if transaction_class is None:
            raise ValueError(
                f"Unsupported combination of bank '{bank}' and account type '{account_type}'"
            )

        # Create the instance from the DataFrame
        return transaction_class(transactions_df, convert=convert)

    @classmethod
    def register(
        cls,
        bank: Bank,
        account_type: AccountType,
        transaction_class: Type[BankTransactions],
    ) -> None:
        """
        Register a new bank transaction class.

        Args:
            bank (Bank): The bank enum.
            account_type (AccountType): The account type enum.
            transaction_class (Type[BankTransactions]): The transaction class to register.
        """
        cls._registry[(bank, account_type)] = transaction_class
