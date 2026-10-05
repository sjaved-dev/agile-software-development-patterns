"""
================================================================================
BANKING TRANSACTION PROCESSOR (CLEAN-ROOM DEMONSTRATION)
================================================================================
REGULATORY & COMPLIANCE DISCLAIMER:
Original production code for ATM transaction encoding software developed
during a software engineering internship remains protected under an active
Non-Disclosure Agreement (NDA) and is not reproduced here. This module is an
independent, from-scratch demonstration of the same underlying software
engineering principles applied during that internship: object-oriented
design following SOLID principles, a repository pattern for data access
(standing in for relational schema access), and defensive error handling
for financial transactions.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class InsufficientFundsError(Exception):
    """Raised when a withdrawal would take an account balance below zero."""
    pass


class AccountNotFoundError(Exception):
    """Raised when a transaction references an account that doesn't exist."""
    pass


@dataclass
class Account:
    account_id: str
    balance: float


# --- Open/Closed Principle -------------------------------------------------
# New transaction types can be added by creating new subclasses of
# Transaction, without modifying TransactionProcessor or existing
# transaction classes at all.

class Transaction(ABC):
    def __init__(self, account_id: str, amount: float):
        if amount <= 0:
            raise ValueError("Transaction amount must be positive.")
        self.account_id = account_id
        self.amount = amount

    @abstractmethod
    def apply(self, account: Account) -> None:
        """Mutates the given account's balance according to this transaction."""
        raise NotImplementedError


class DepositTransaction(Transaction):
    def apply(self, account: Account) -> None:
        account.balance += self.amount


class WithdrawalTransaction(Transaction):
    def apply(self, account: Account) -> None:
        if account.balance < self.amount:
            raise InsufficientFundsError(
                f"Account {account.account_id} has insufficient funds "
                f"for a withdrawal of {self.amount:.2f} "
                f"(balance: {account.balance:.2f})."
            )
        account.balance -= self.amount


# --- Dependency Inversion Principle -----------------------------------------
# TransactionProcessor depends on the AccountRepository abstraction, not on
# a concrete storage mechanism. Swapping InMemoryAccountRepository for a real
# database-backed implementation requires no change to TransactionProcessor.

class AccountRepository(ABC):
    @abstractmethod
    def get(self, account_id: str) -> Account:
        raise NotImplementedError

    @abstractmethod
    def save(self, account: Account) -> None:
        raise NotImplementedError


class InMemoryAccountRepository(AccountRepository):
    """Simulates a relational accounts table with an in-memory dictionary."""

    def __init__(self):
        self._accounts = {}

    def seed(self, account: Account) -> None:
        self._accounts[account.account_id] = account

    def get(self, account_id: str) -> Account:
        try:
            return self._accounts[account_id]
        except KeyError:
            raise AccountNotFoundError(f"No account found with id {account_id!r}.")

    def save(self, account: Account) -> None:
        self._accounts[account.account_id] = account


# --- Single Responsibility Principle ----------------------------------------
# TransactionProcessor's only job is coordinating: fetch the account, apply
# the transaction, persist the result. It doesn't know how transactions work
# internally, and it doesn't know how accounts are stored.

class TransactionProcessor:
    def __init__(self, repository: AccountRepository):
        self._repository = repository

    def process(self, transaction: Transaction) -> Account:
        account = self._repository.get(transaction.account_id)
        transaction.apply(account)
        self._repository.save(account)
        return account
