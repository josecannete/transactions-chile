"""
Test module for the bank_transactions module.

This module provides comprehensive test coverage for the bank_transactions module,
including tests for base functionality, specific bank implementations, data conversion,
validation, and edge cases.
"""

import os
import tempfile
import unittest
import pandas as pd
import pandera as pa
from parameterized import parameterized

from transactions_chile.bank_transactions import (
    BankTransactions,
    SantanderBankTransactions,
    SantanderCheckingAccountBankTransactions,
    ItauBankTransactions,
    ItauCreditCardBankTransactions,
    ItauCheckingAccountBankTransactions,
    BancoChileBankTransactions,
    BancoChileCreditCardBankTransactions,
    BancoChileCheckingAccountBankTransactions,
    STANDARD_COLUMNS,
)
from transactions_chile.schemas import BankTransactionsSchema


# Create a concrete test class that can be reused across tests
class MockBankTransactions(BankTransactions):
    """A concrete implementation of the abstract BankTransactions class for testing."""

    @property
    def bank_name(self):
        return "Test Bank"

    @property
    def account_type(self):
        return "Test Account"

    def _convert_dataframe(self, df):
        return df


class TestBankTransactionsBase(unittest.TestCase):
    """Test the base BankTransactions functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a standard test DataFrame with all required columns
        self.valid_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2025-04-01"]),
                "payee": ["Test Transaction"],
                "description": ["Test Transaction"],
                "amount": [1000],
                "city": ["Santiago"],
                "balance": [1000],
            }
        )

        # Create a DataFrame missing required columns
        self.invalid_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2025-04-01"]),
                # Missing "payee" column which is required
                "description": ["Test Transaction"],
                "amount": [1000],
                "city": ["Santiago"],
                "balance": [1000],
            }
        )

    def test_standard_columns_constant(self):
        """Test the STANDARD_COLUMNS constant."""
        expected = ["date", "payee", "description", "amount", "city", "balance"]
        self.assertEqual(STANDARD_COLUMNS, expected)

    def test_to_csv_basic(self):
        """Test the to_csv method with basic parameters."""
        # Create an instance of our test class with the valid DataFrame
        transactions = MockBankTransactions(self.valid_df, convert=False)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Export to CSV
            transactions.to_csv(temp_filename)

            # Check if the file exists
            self.assertTrue(os.path.exists(temp_filename))

            # Read back the file and check content
            df_read = pd.read_csv(temp_filename, parse_dates=["date"])
            self.assertEqual(len(df_read), 1)
            self.assertEqual(df_read["amount"].iloc[0], 1000)
            self.assertEqual(df_read["payee"].iloc[0], "Test Transaction")
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_to_csv_custom_params(self):
        """Test the to_csv method with custom delimiter and encoding."""
        # Create an instance with the valid DataFrame
        transactions = MockBankTransactions(self.valid_df, convert=False)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Export to CSV with custom delimiter
            transactions.to_csv(temp_filename, delimiter=";", encoding="utf-8")

            # Read the file as text to check the delimiter
            with open(temp_filename, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("date;payee;description", content)
                self.assertIn("2025-04-01;Test Transaction;Test Transaction", content)
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_validate_success(self):
        """Test the validate method with valid data."""
        # Create an instance with the valid DataFrame
        transactions = MockBankTransactions(self.valid_df, convert=False)

        # Validate
        result = transactions.validate(BankTransactionsSchema)
        self.assertTrue(result)

    def test_validate_failure(self):
        """Test the validate method with invalid data."""
        # Create an instance with the invalid DataFrame
        transactions = MockBankTransactions(self.invalid_df, convert=False)

        # Validate should fail
        with self.assertRaises(pa.errors.SchemaError):
            transactions.validate(BankTransactionsSchema)

    def test_validate_and_save_success(self):
        """Test the validate_and_save method with valid data."""
        # Create an instance with the valid DataFrame
        transactions = MockBankTransactions(self.valid_df, convert=False)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Validate and save
            result = transactions.validate_and_save(
                BankTransactionsSchema, temp_filename
            )

            # Should return True for success
            self.assertTrue(result)

            # File should exist
            self.assertTrue(os.path.exists(temp_filename))

            # Check contents
            df_read = pd.read_csv(temp_filename, parse_dates=["date"])
            self.assertEqual(len(df_read), 1)
            self.assertEqual(df_read["amount"].iloc[0], 1000)
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_validate_and_save_failure(self):
        """Test the validate_and_save method with invalid data."""
        # Create an instance with the invalid DataFrame
        transactions = MockBankTransactions(self.invalid_df, convert=False)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Validation should fail with a SchemaError
            with self.assertRaises(pa.errors.SchemaError):
                transactions.validate_and_save(BankTransactionsSchema, temp_filename)
        finally:
            # Clean up if the file somehow got created
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


# Rest of the test classes remain unchanged


class TestSantanderBankTransactions(unittest.TestCase):
    """Test the Santander bank transactions classes."""

    def test_inheritance_hierarchy(self):
        """Test that the inheritance hierarchy is correct."""
        self.assertTrue(
            issubclass(
                SantanderCheckingAccountBankTransactions, SantanderBankTransactions
            )
        )
        self.assertTrue(issubclass(SantanderBankTransactions, BankTransactions))

    def test_properties(self):
        """Test the Santander bank properties."""
        # Create a mock DataFrame for testing
        mock_df = pd.DataFrame(
            {
                "Fecha": ["01-04-2025"],
                "Detalle": ["Test Transaction"],
                "Monto abono ($)": [1000],
                "Monto cargo ($)": [0],
                "Saldo ($)": [1000],
            }
        )

        # Create an instance with convert=False to test properties
        transactions = SantanderCheckingAccountBankTransactions(mock_df, convert=False)

        # Test the properties
        self.assertEqual(transactions.bank_name, "Santander")
        self.assertEqual(transactions.account_type, "Checking Account")


class TestSantanderCheckingAccountBankTransactions(unittest.TestCase):
    """Test the Santander Checking Account bank transactions class."""

    def setUp(self):
        """Set up test fixtures for Santander Checking Account."""
        # Create test data with various transaction types
        self.credit_transaction_df = pd.DataFrame(
            {
                "Fecha": ["01-04-2025"],
                "Detalle": ["DEPOSITO EN EFECTIVO"],
                "Monto abono ($)": [150000],
                "Monto cargo ($)": [0],
                "Saldo ($)": [150000],
            }
        )

        self.debit_transaction_df = pd.DataFrame(
            {
                "Fecha": ["02-04-2025"],
                "Detalle": ["COMPRA TARJETA DEBITO"],
                "Monto abono ($)": [0],
                "Monto cargo ($)": [25000],
                "Saldo ($)": [125000],
            }
        )

        self.mixed_transactions_df = pd.DataFrame(
            {
                "Fecha": ["01-04-2025", "02-04-2025", "03-04-2025", "04-04-2025"],
                "Detalle": [
                    "DEPOSITO EN EFECTIVO",
                    "COMPRA TARJETA DEBITO",
                    "TRANSFERENCIA RECIBIDA",
                    "PAGO CUENTA",
                ],
                "Monto abono ($)": [150000, 0, 75000, 0],
                "Monto cargo ($)": [0, 25000, 0, 35000],
                "Saldo ($)": [150000, 125000, 200000, 165000],
            }
        )

        self.transactions_with_nulls_df = pd.DataFrame(
            {
                "Fecha": ["01-04-2025", "02-04-2025"],
                "Detalle": ["DEPOSITO EN EFECTIVO", "COMPRA TARJETA DEBITO"],
                "Monto abono ($)": [150000, None],
                "Monto cargo ($)": [None, 25000],
                "Saldo ($)": [150000, 125000],
            }
        )

    def test_convert_dataframe_credit_transaction(self):
        """Test converting a credit transaction in Santander Checking Account."""
        transactions = SantanderCheckingAccountBankTransactions(
            self.credit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.credit_transaction_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], 150000
        )  # Credit amount should be positive
        self.assertEqual(result_df["payee"].iloc[0], "DEPOSITO EN EFECTIVO")
        self.assertEqual(result_df["description"].iloc[0], "DEPOSITO EN EFECTIVO")
        self.assertEqual(result_df["balance"].iloc[0], 150000)

        # Verify date conversion is correct
        expected_date = pd.to_datetime("01-04-2025", format="%d-%m-%Y")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

        # Verify all expected columns are present
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)

    def test_convert_dataframe_debit_transaction(self):
        """Test converting a debit transaction in Santander Checking Account."""
        transactions = SantanderCheckingAccountBankTransactions(
            self.debit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.debit_transaction_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -25000
        )  # Debit amount should be negative
        self.assertEqual(result_df["payee"].iloc[0], "COMPRA TARJETA DEBITO")
        self.assertEqual(result_df["description"].iloc[0], "COMPRA TARJETA DEBITO")
        self.assertEqual(result_df["balance"].iloc[0], 125000)

        # Verify date conversion is correct
        expected_date = pd.to_datetime("02-04-2025", format="%d-%m-%Y")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

    def test_convert_dataframe_mixed_transactions(self):
        """Test converting multiple mixed transactions in Santander Checking Account."""
        transactions = SantanderCheckingAccountBankTransactions(
            self.mixed_transactions_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.mixed_transactions_df)

        # Verify number of transactions
        self.assertEqual(len(result_df), 4)

        # Verify amounts are correct (credits positive, debits negative)
        self.assertEqual(result_df["amount"].iloc[0], 150000)  # Credit
        self.assertEqual(result_df["amount"].iloc[1], -25000)  # Debit
        self.assertEqual(result_df["amount"].iloc[2], 75000)  # Credit
        self.assertEqual(result_df["amount"].iloc[3], -35000)  # Debit

        # Verify balances are correct
        self.assertEqual(result_df["balance"].iloc[0], 150000)
        self.assertEqual(result_df["balance"].iloc[1], 125000)
        self.assertEqual(result_df["balance"].iloc[2], 200000)
        self.assertEqual(result_df["balance"].iloc[3], 165000)

        # Verify payees are set correctly
        for i in range(4):
            self.assertEqual(
                result_df["payee"].iloc[i],
                self.mixed_transactions_df["Detalle"].iloc[i],
            )

    def test_convert_dataframe_with_null_values(self):
        """Test handling of null values in Santander Checking Account transactions."""
        transactions = SantanderCheckingAccountBankTransactions(
            self.transactions_with_nulls_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.transactions_with_nulls_df)

        # Verify null values are handled correctly
        self.assertEqual(result_df["amount"].iloc[0], 150000)  # Only credit amount
        self.assertEqual(result_df["amount"].iloc[1], -25000)  # Only debit amount

        # Make sure no NaN values in the result
        self.assertFalse(result_df["amount"].isnull().any())

    def test_convert_dataframe_returns_required_columns(self):
        """Test that the result has exactly the required columns in the right order."""
        transactions = SantanderCheckingAccountBankTransactions(
            self.credit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.credit_transaction_df)

        # Verify columns are in correct order
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)


class TestItauBankTransactions(unittest.TestCase):
    """Test the Itau bank transactions classes."""

    def test_inheritance_hierarchy(self):
        """Test that the inheritance hierarchy is correct."""
        self.assertTrue(
            issubclass(ItauCreditCardBankTransactions, ItauBankTransactions)
        )
        self.assertTrue(
            issubclass(ItauCheckingAccountBankTransactions, ItauBankTransactions)
        )
        self.assertTrue(issubclass(ItauBankTransactions, BankTransactions))


class TestItauCreditCardBankTransactions(unittest.TestCase):
    """Test the Itau Credit Card bank transactions class."""

    def setUp(self):
        """Set up test fixtures for Itau Credit Card."""
        # Sample credit card purchases
        self.regular_purchase_df = pd.DataFrame(
            {
                "Fecha compra": ["2025-04-01"],
                "Descripción": ["FARMACIA AHUMADA"],
                "Monto": [15400],
                "Ciudad": ["SANTIAGO"],
            }
        )

        self.foreign_purchase_df = pd.DataFrame(
            {
                "Fecha compra": ["2025-04-02"],
                "Descripción": ["AMAZON.COM"],
                "Monto": [48750],
                "Ciudad": ["SEATTLE"],
            }
        )

        # Multiple transactions with different cities
        self.multiple_transactions_df = pd.DataFrame(
            {
                "Fecha compra": ["2025-04-01", "2025-04-02", "2025-04-03"],
                "Descripción": ["FARMACIA AHUMADA", "AMAZON.COM", "SUPERMERCADO JUMBO"],
                "Monto": [15400, 48750, 32150],
                "Ciudad": ["SANTIAGO", "SEATTLE", "SANTIAGO"],
            }
        )

        # Transaction with missing data
        self.transaction_with_nulls_df = pd.DataFrame(
            {
                "Fecha compra": ["2025-04-01", "2025-04-02"],
                "Descripción": ["FARMACIA AHUMADA", "AMAZON.COM"],
                "Monto": [15400, 48750],
                "Ciudad": ["SANTIAGO", None],
            }
        )

    def test_convert_dataframe_regular_purchase(self):
        """Test converting a regular credit card purchase in Itau Credit Card."""
        transactions = ItauCreditCardBankTransactions(
            self.regular_purchase_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.regular_purchase_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -15400
        )  # Credit card amounts should be negative
        self.assertEqual(result_df["payee"].iloc[0], "FARMACIA AHUMADA")
        self.assertEqual(result_df["description"].iloc[0], "FARMACIA AHUMADA")
        self.assertEqual(result_df["city"].iloc[0], "SANTIAGO")
        self.assertEqual(
            result_df["balance"].iloc[0], 0
        )  # Credit cards don't show balance

        # Verify date conversion is correct
        expected_date = pd.to_datetime("2025-04-01")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

        # Verify all expected columns are present
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)

    def test_convert_dataframe_foreign_purchase(self):
        """Test converting a foreign purchase in Itau Credit Card."""
        transactions = ItauCreditCardBankTransactions(
            self.foreign_purchase_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.foreign_purchase_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -48750
        )  # Credit card amounts should be negative
        self.assertEqual(result_df["payee"].iloc[0], "AMAZON.COM")
        self.assertEqual(result_df["city"].iloc[0], "SEATTLE")

        # Verify date conversion is correct
        expected_date = pd.to_datetime("2025-04-02")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

    def test_convert_dataframe_multiple_transactions(self):
        """Test converting multiple transactions in Itau Credit Card."""
        transactions = ItauCreditCardBankTransactions(
            self.multiple_transactions_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.multiple_transactions_df)

        # Verify number of transactions
        self.assertEqual(len(result_df), 3)

        # Verify amounts are all negative (credit card purchases)
        self.assertEqual(result_df["amount"].iloc[0], -15400)
        self.assertEqual(result_df["amount"].iloc[1], -48750)
        self.assertEqual(result_df["amount"].iloc[2], -32150)

        # Verify cities are correct
        self.assertEqual(result_df["city"].iloc[0], "SANTIAGO")
        self.assertEqual(result_df["city"].iloc[1], "SEATTLE")
        self.assertEqual(result_df["city"].iloc[2], "SANTIAGO")

    def test_convert_dataframe_with_null_values(self):
        """Test handling of null values in Itau Credit Card transactions."""
        transactions = ItauCreditCardBankTransactions(
            self.transaction_with_nulls_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.transaction_with_nulls_df)

        # Verify that null city is preserved
        self.assertEqual(result_df["city"].iloc[0], "SANTIAGO")
        self.assertTrue(pd.isna(result_df["city"].iloc[1]))

    def test_convert_dataframe_returns_required_columns(self):
        """Test that the result has exactly the required columns in the right order."""
        transactions = ItauCreditCardBankTransactions(
            self.regular_purchase_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.regular_purchase_df)

        # Verify columns are in correct order
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)


class TestItauCheckingAccountBankTransactions(unittest.TestCase):
    """Test the Itau Checking Account bank transactions class."""

    def setUp(self):
        """Set up test fixtures for Itau Checking Account."""
        # Deposit transaction
        self.deposit_transaction_df = pd.DataFrame(
            {
                "Fecha": ["2025-04-01"],
                "Movimientos": ["DEPOSITO EN EFECTIVO"],
                "Abonos": [250000],
                "Cargos": [None],
                "Saldo": [250000],
            }
        )

        # Withdrawal transaction
        self.withdrawal_transaction_df = pd.DataFrame(
            {
                "Fecha": ["2025-04-02"],
                "Movimientos": ["GIRO CAJERO AUTOMATICO"],
                "Abonos": [None],
                "Cargos": [50000],
                "Saldo": [200000],
            }
        )

        # Multiple transactions with mixed types
        self.mixed_transactions_df = pd.DataFrame(
            {
                "Fecha": ["2025-04-01", "2025-04-02", "2025-04-03", "2025-04-04"],
                "Movimientos": [
                    "DEPOSITO EN EFECTIVO",
                    "GIRO CAJERO AUTOMATICO",
                    "TRANSFERENCIA RECIBIDA",
                    "PAGO CUENTA",
                ],
                "Abonos": [250000, None, 75000, None],
                "Cargos": [None, 50000, None, 35000],
                "Saldo": [250000, 200000, 275000, 240000],
            }
        )

        # Transactions with some 0 values instead of NaN
        self.transactions_with_zeros_df = pd.DataFrame(
            {
                "Fecha": ["2025-04-01", "2025-04-02"],
                "Movimientos": ["DEPOSITO EN EFECTIVO", "GIRO CAJERO AUTOMATICO"],
                "Abonos": [250000, 0],
                "Cargos": [0, 50000],
                "Saldo": [250000, 200000],
            }
        )

    def test_convert_dataframe_deposit_transaction(self):
        """Test converting a deposit transaction in Itau Checking Account."""
        transactions = ItauCheckingAccountBankTransactions(
            self.deposit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.deposit_transaction_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], 250000
        )  # Deposit should be positive
        self.assertEqual(result_df["payee"].iloc[0], "DEPOSITO EN EFECTIVO")
        self.assertEqual(result_df["description"].iloc[0], "DEPOSITO EN EFECTIVO")
        self.assertEqual(result_df["balance"].iloc[0], 250000)
        self.assertEqual(result_df["city"].iloc[0], "")  # City should be empty

        # Verify date conversion is correct
        expected_date = pd.to_datetime("2025-04-01")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

        # Verify all expected columns are present
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)

    def test_convert_dataframe_withdrawal_transaction(self):
        """Test converting a withdrawal transaction in Itau Checking Account."""
        transactions = ItauCheckingAccountBankTransactions(
            self.withdrawal_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.withdrawal_transaction_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -50000
        )  # Withdrawal should be negative
        self.assertEqual(result_df["payee"].iloc[0], "GIRO CAJERO AUTOMATICO")
        self.assertEqual(result_df["balance"].iloc[0], 200000)

        # Verify date conversion is correct
        expected_date = pd.to_datetime("2025-04-02")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

    def test_convert_dataframe_mixed_transactions(self):
        """Test converting multiple mixed transactions in Itau Checking Account."""
        transactions = ItauCheckingAccountBankTransactions(
            self.mixed_transactions_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.mixed_transactions_df)

        # Verify number of transactions
        self.assertEqual(len(result_df), 4)

        # Verify amounts are correct (credits positive, debits negative)
        self.assertEqual(result_df["amount"].iloc[0], 250000)  # Deposit
        self.assertEqual(result_df["amount"].iloc[1], -50000)  # Withdrawal
        self.assertEqual(result_df["amount"].iloc[2], 75000)  # Transfer received
        self.assertEqual(result_df["amount"].iloc[3], -35000)  # Payment

        # Verify balances are correct
        self.assertEqual(result_df["balance"].iloc[0], 250000)
        self.assertEqual(result_df["balance"].iloc[1], 200000)
        self.assertEqual(result_df["balance"].iloc[2], 275000)
        self.assertEqual(result_df["balance"].iloc[3], 240000)

    def test_convert_dataframe_with_zero_values(self):
        """Test handling of zero values instead of NaN in Itau Checking Account transactions."""
        transactions = ItauCheckingAccountBankTransactions(
            self.transactions_with_zeros_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.transactions_with_zeros_df)

        # Verify zero values are handled correctly
        self.assertEqual(result_df["amount"].iloc[0], 250000)  # Only abono (deposit)
        self.assertEqual(result_df["amount"].iloc[1], -50000)  # Only cargo (withdrawal)

    def test_convert_dataframe_returns_required_columns(self):
        """Test that the result has exactly the required columns in the right order."""
        transactions = ItauCheckingAccountBankTransactions(
            self.deposit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.deposit_transaction_df)

        # Verify columns are in correct order
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)


class TestBancoChileBankTransactions(unittest.TestCase):
    """Test the Banco Chile bank transactions classes."""

    def test_inheritance_hierarchy(self):
        """Test that the inheritance hierarchy is correct."""
        self.assertTrue(
            issubclass(BancoChileCreditCardBankTransactions, BancoChileBankTransactions)
        )
        self.assertTrue(
            issubclass(
                BancoChileCheckingAccountBankTransactions, BancoChileBankTransactions
            )
        )
        self.assertTrue(issubclass(BancoChileBankTransactions, BankTransactions))


class TestBancoChileCreditCardBankTransactions(unittest.TestCase):
    """Test the Banco Chile Credit Card bank transactions class."""

    def setUp(self):
        """Set up test fixtures for Banco Chile Credit Card."""
        # Regular purchase
        self.regular_purchase_df = pd.DataFrame(
            {
                "Fecha": ["01/04/2025"],
                "Descripción": ["SUPERMERCADO LIDER"],
                "Unnamed: 10": [45280],
                "Ciudad": ["SANTIAGO"],
            }
        )

        # International purchase
        self.international_purchase_df = pd.DataFrame(
            {
                "Fecha": ["02/04/2025"],
                "Descripción": ["NETFLIX"],
                "Unnamed: 10": [12990],
                "Ciudad": ["LOS GATOS"],
            }
        )

        # Multiple transactions
        self.multiple_transactions_df = pd.DataFrame(
            {
                "Fecha": ["01/04/2025", "02/04/2025", "03/04/2025"],
                "Descripción": ["SUPERMERCADO LIDER", "NETFLIX", "UBER EATS"],
                "Unnamed: 10": [45280, 12990, 22500],
                "Ciudad": ["SANTIAGO", "LOS GATOS", "SANTIAGO"],
            }
        )

        # Transaction with missing city
        self.transaction_missing_city_df = pd.DataFrame(
            {
                "Fecha": ["01/04/2025"],
                "Descripción": ["COMPRA ONLINE"],
                "Unnamed: 10": [35670],
                "Ciudad": [None],
            }
        )

    def test_convert_dataframe_regular_purchase(self):
        """Test converting a regular purchase in Banco Chile Credit Card."""
        transactions = BancoChileCreditCardBankTransactions(
            self.regular_purchase_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.regular_purchase_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -45280
        )  # Credit card amount should be negative
        self.assertEqual(result_df["payee"].iloc[0], "SUPERMERCADO LIDER")
        self.assertEqual(result_df["description"].iloc[0], "SUPERMERCADO LIDER")
        self.assertEqual(result_df["city"].iloc[0], "SANTIAGO")
        self.assertEqual(
            result_df["balance"].iloc[0], 0
        )  # Credit cards don't track balance

        # Verify date conversion is correct
        expected_date = pd.to_datetime("01/04/2025", format="%d/%m/%Y")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

        # Verify all expected columns are present
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)

    def test_convert_dataframe_international_purchase(self):
        """Test converting an international purchase in Banco Chile Credit Card."""
        transactions = BancoChileCreditCardBankTransactions(
            self.international_purchase_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.international_purchase_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -12990
        )  # Credit card amount should be negative
        self.assertEqual(result_df["payee"].iloc[0], "NETFLIX")
        self.assertEqual(result_df["city"].iloc[0], "LOS GATOS")

        # Verify date conversion is correct
        expected_date = pd.to_datetime("02/04/2025", format="%d/%m/%Y")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

    def test_convert_dataframe_multiple_transactions(self):
        """Test converting multiple transactions in Banco Chile Credit Card."""
        transactions = BancoChileCreditCardBankTransactions(
            self.multiple_transactions_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.multiple_transactions_df)

        # Verify number of transactions
        self.assertEqual(len(result_df), 3)

        # Verify amounts are all negative (credit card purchases)
        self.assertEqual(result_df["amount"].iloc[0], -45280)
        self.assertEqual(result_df["amount"].iloc[1], -12990)
        self.assertEqual(result_df["amount"].iloc[2], -22500)

        # Verify cities are correct
        self.assertEqual(result_df["city"].iloc[0], "SANTIAGO")
        self.assertEqual(result_df["city"].iloc[1], "LOS GATOS")
        self.assertEqual(result_df["city"].iloc[2], "SANTIAGO")

    def test_convert_dataframe_missing_city(self):
        """Test handling of missing city in Banco Chile Credit Card transactions."""
        transactions = BancoChileCreditCardBankTransactions(
            self.transaction_missing_city_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.transaction_missing_city_df)

        # Verify that null city is preserved
        self.assertTrue(pd.isna(result_df["city"].iloc[0]))

    def test_convert_dataframe_returns_required_columns(self):
        """Test that the result has exactly the required columns in the right order."""
        transactions = BancoChileCreditCardBankTransactions(
            self.regular_purchase_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.regular_purchase_df)

        # Verify columns are in correct order
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)


class TestBancoChileCheckingAccountBankTransactions(unittest.TestCase):
    """Test the Banco Chile Checking Account bank transactions class."""

    def setUp(self):
        """Set up test fixtures for Banco Chile Checking Account."""
        # Deposit transaction
        self.deposit_transaction_df = pd.DataFrame(
            {
                "Fecha": ["01/04/2025"],
                "Descripción": ["DEPOSITO EN EFECTIVO"],
                "Abonos (CLP)": [350000],
                "Cargos (CLP)": [0],
                "Saldo (CLP)": [350000],
                "Canal o Sucursal": ["SUCURSAL PROVIDENCIA"],
            }
        )

        # Withdrawal transaction
        self.withdrawal_transaction_df = pd.DataFrame(
            {
                "Fecha": ["02/04/2025"],
                "Descripción": ["GIRO ATM"],
                "Abonos (CLP)": [0],
                "Cargos (CLP)": [100000],
                "Saldo (CLP)": [250000],
                "Canal o Sucursal": ["CAJERO AUTOMATICO"],
            }
        )

        # Multiple transactions
        self.mixed_transactions_df = pd.DataFrame(
            {
                "Fecha": ["01/04/2025", "02/04/2025", "03/04/2025", "04/04/2025"],
                "Descripción": [
                    "DEPOSITO EN EFECTIVO",
                    "GIRO ATM",
                    "TRANSFERENCIA RECIBIDA",
                    "PAGO CUENTA",
                ],
                "Abonos (CLP)": [350000, 0, 50000, 0],
                "Cargos (CLP)": [0, 100000, 0, 35000],
                "Saldo (CLP)": [350000, 250000, 300000, 265000],
                "Canal o Sucursal": [
                    "SUCURSAL PROVIDENCIA",
                    "CAJERO AUTOMATICO",
                    "INTERNET",
                    "INTERNET",
                ],
            }
        )

        # Transaction with null channel
        self.transaction_null_channel_df = pd.DataFrame(
            {
                "Fecha": ["01/04/2025"],
                "Descripción": ["COMPRA POS"],
                "Abonos (CLP)": [0],
                "Cargos (CLP)": [15000],
                "Saldo (CLP)": [235000],
                "Canal o Sucursal": [None],
            }
        )

    def test_convert_dataframe_deposit_transaction(self):
        """Test converting a deposit transaction in Banco Chile Checking Account."""
        transactions = BancoChileCheckingAccountBankTransactions(
            self.deposit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.deposit_transaction_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], 350000
        )  # Deposit amount should be positive
        self.assertEqual(result_df["payee"].iloc[0], "DEPOSITO EN EFECTIVO")
        self.assertEqual(result_df["description"].iloc[0], "DEPOSITO EN EFECTIVO")
        self.assertEqual(result_df["balance"].iloc[0], 350000)
        self.assertEqual(
            result_df["city"].iloc[0], "SUCURSAL PROVIDENCIA"
        )  # Channel should be in city field

        # Verify date conversion is correct
        expected_date = pd.to_datetime("01/04/2025", format="%d/%m/%Y")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

        # Verify all expected columns are present
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)

    def test_convert_dataframe_withdrawal_transaction(self):
        """Test converting a withdrawal transaction in Banco Chile Checking Account."""
        transactions = BancoChileCheckingAccountBankTransactions(
            self.withdrawal_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.withdrawal_transaction_df)

        # Verify the transaction was processed correctly
        self.assertEqual(
            result_df["amount"].iloc[0], -100000
        )  # Withdrawal amount should be negative
        self.assertEqual(result_df["payee"].iloc[0], "GIRO ATM")
        self.assertEqual(result_df["balance"].iloc[0], 250000)
        self.assertEqual(result_df["city"].iloc[0], "CAJERO AUTOMATICO")

        # Verify date conversion is correct
        expected_date = pd.to_datetime("02/04/2025", format="%d/%m/%Y")
        self.assertEqual(result_df["date"].iloc[0], expected_date)

    def test_convert_dataframe_mixed_transactions(self):
        """Test converting multiple mixed transactions in Banco Chile Checking Account."""
        transactions = BancoChileCheckingAccountBankTransactions(
            self.mixed_transactions_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.mixed_transactions_df)

        # Verify number of transactions
        self.assertEqual(len(result_df), 4)

        # Verify amounts are correct (credits positive, debits negative)
        self.assertEqual(result_df["amount"].iloc[0], 350000)  # Deposit
        self.assertEqual(result_df["amount"].iloc[1], -100000)  # ATM withdrawal
        self.assertEqual(result_df["amount"].iloc[2], 50000)  # Transfer received
        self.assertEqual(result_df["amount"].iloc[3], -35000)  # Payment

        # Verify balances are correct
        self.assertEqual(result_df["balance"].iloc[0], 350000)
        self.assertEqual(result_df["balance"].iloc[1], 250000)
        self.assertEqual(result_df["balance"].iloc[2], 300000)
        self.assertEqual(result_df["balance"].iloc[3], 265000)

        # Verify channels are mapped to city field
        self.assertEqual(result_df["city"].iloc[0], "SUCURSAL PROVIDENCIA")
        self.assertEqual(result_df["city"].iloc[1], "CAJERO AUTOMATICO")
        self.assertEqual(result_df["city"].iloc[2], "INTERNET")
        self.assertEqual(result_df["city"].iloc[3], "INTERNET")

    def test_convert_dataframe_null_channel(self):
        """Test handling of null channel in Banco Chile Checking Account transactions."""
        transactions = BancoChileCheckingAccountBankTransactions(
            self.transaction_null_channel_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.transaction_null_channel_df)

        # Verify that null channel is preserved in city field
        self.assertTrue(pd.isna(result_df["city"].iloc[0]))

    def test_convert_dataframe_returns_required_columns(self):
        """Test that the result has exactly the required columns in the right order."""
        transactions = BancoChileCheckingAccountBankTransactions(
            self.deposit_transaction_df, convert=False
        )
        result_df = transactions._convert_dataframe(self.deposit_transaction_df)

        # Verify columns are in correct order
        self.assertListEqual(list(result_df.columns), STANDARD_COLUMNS)


class TestIntegrationTests(unittest.TestCase):
    """Integration tests that test multiple components together."""

    def test_validate_and_save_flow(self):
        """Test the complete validate-and-save flow with a sample DataFrame."""
        # Create sample data
        sample_data = {
            "date": pd.to_datetime(["2025-04-01", "2025-04-02", "2025-04-03"]),
            "payee": ["Deposit", "Withdrawal", "Purchase"],
            "description": ["Salary Deposit", "ATM Withdrawal", "Grocery Shopping"],
            "amount": [5000, -1000, -500],
            "city": ["Santiago", "Valparaiso", "Concepcion"],
            "balance": [5000, 4000, 3500],
        }
        sample_df = pd.DataFrame(sample_data)

        # Create a bank transactions instance using our shared MockBankTransactions class
        transactions = MockBankTransactions(sample_df, convert=False)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Validate and save
            result = transactions.validate_and_save(
                BankTransactionsSchema, temp_filename
            )
            self.assertTrue(result)

            # Read back the file and check content
            df_read = pd.read_csv(temp_filename, parse_dates=["date"])

            # Check row count
            self.assertEqual(len(df_read), 3)

            # Check specific values
            self.assertEqual(df_read["amount"].iloc[0], 5000)
            self.assertEqual(df_read["amount"].iloc[1], -1000)
            self.assertEqual(df_read["payee"].iloc[2], "Purchase")
            self.assertEqual(df_read["balance"].iloc[2], 3500)

            # Check date column type
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_read["date"]))
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    @parameterized.expand(
        [
            # Test with different date formats
            ({"date_str": "01-04-2025", "date_format": "%d-%m-%Y"}, "01-04-2025"),
            ({"date_str": "2025-04-01", "date_format": "%Y-%m-%d"}, "2025-04-01"),
            ({"date_str": "01/04/2025", "date_format": "%d/%m/%Y"}, "01/04/2025"),
        ]
    )
    def test_date_format_handling(self, date_info, expected_str):
        """Test handling of different date formats."""
        date_str = date_info["date_str"]
        date_format = date_info["date_format"]

        # Create a mock DataFrame
        mock_df = pd.DataFrame({"date_col": [date_str], "other_col": ["value"]})

        # Create a test class with specific date handling
        class DateTestClass(BankTransactions):
            @property
            def bank_name(self):
                return "Test Bank"

            @property
            def account_type(self):
                return "Test Account"

            def _convert_dataframe(self, df):
                df_copy = df.copy()
                df_copy["date"] = pd.to_datetime(
                    df_copy["date_col"], format=date_format
                )
                df_copy["payee"] = df_copy["other_col"]
                df_copy["description"] = df_copy["other_col"]
                df_copy["amount"] = 0
                df_copy["city"] = ""
                df_copy["balance"] = 0
                return df_copy[STANDARD_COLUMNS]

        # Create an instance and convert
        transactions = DateTestClass(mock_df, convert=True)

        # The date should now be a datetime object
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(transactions.transactions["date"])
        )

        # Check the columns are correct
        self.assertListEqual(list(transactions.transactions.columns), STANDARD_COLUMNS)


if __name__ == "__main__":
    unittest.main()
