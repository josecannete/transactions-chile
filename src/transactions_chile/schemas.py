import pandera as pa


class BankTransactionsSchema(pa.DataFrameModel):
    date: pa.DateTime = pa.Field(nullable=False)
    payee: str = pa.Field(nullable=False)
    amount: int = pa.Field(nullable=False)
    description: str = pa.Field(nullable=True)
    city: str = pa.Field(nullable=True)
    balance: int = pa.Field(nullable=True)
