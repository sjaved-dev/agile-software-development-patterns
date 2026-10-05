import unittest
from transaction_processor import (
    Account,
    DepositTransaction,
    WithdrawalTransaction,
    InMemoryAccountRepository,
    TransactionProcessor,
    InsufficientFundsError,
    AccountNotFoundError,
)


class TestTransactionProcessor(unittest.TestCase):

    def setUp(self):
        self.repository = InMemoryAccountRepository()
        self.repository.seed(Account(account_id="ACC-001", balance=100.0))
        self.processor = TransactionProcessor(self.repository)

    def test_deposit_increases_balance(self):
        result = self.processor.process(DepositTransaction("ACC-001", 50.0))
        self.assertEqual(result.balance, 150.0)

    def test_withdrawal_decreases_balance(self):
        result = self.processor.process(WithdrawalTransaction("ACC-001", 40.0))
        self.assertEqual(result.balance, 60.0)

    def test_withdrawal_beyond_balance_raises(self):
        with self.assertRaises(InsufficientFundsError):
            self.processor.process(WithdrawalTransaction("ACC-001", 1000.0))

    def test_transaction_on_unknown_account_raises(self):
        with self.assertRaises(AccountNotFoundError):
            self.processor.process(DepositTransaction("ACC-DOES-NOT-EXIST", 10.0))

    def test_balance_persists_across_multiple_transactions(self):
        self.processor.process(DepositTransaction("ACC-001", 20.0))
        self.processor.process(WithdrawalTransaction("ACC-001", 30.0))
        final = self.repository.get("ACC-001")
        self.assertEqual(final.balance, 90.0)

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            DepositTransaction("ACC-001", -5.0)


if __name__ == "__main__":
    unittest.main()
