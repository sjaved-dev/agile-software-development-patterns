"""
Small end-to-end demo of the transaction processor, run directly to see
it working without needing a test runner.
"""
from transaction_processor import (
    Account,
    DepositTransaction,
    WithdrawalTransaction,
    InMemoryAccountRepository,
    TransactionProcessor,
    InsufficientFundsError,
)

if __name__ == "__main__":
    repository = InMemoryAccountRepository()
    repository.seed(Account(account_id="ACC-001", balance=100.0))
    processor = TransactionProcessor(repository)

    print("Starting balance:", repository.get("ACC-001").balance)

    processor.process(DepositTransaction("ACC-001", 50.0))
    print("After deposit of 50:", repository.get("ACC-001").balance)

    processor.process(WithdrawalTransaction("ACC-001", 30.0))
    print("After withdrawal of 30:", repository.get("ACC-001").balance)

    try:
        processor.process(WithdrawalTransaction("ACC-001", 1000.0))
    except InsufficientFundsError as e:
        print("Withdrawal of 1000 correctly rejected:", e)

    print("Final balance:", repository.get("ACC-001").balance)
