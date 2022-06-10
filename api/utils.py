"""
API utility method module
"""
from api.models import DEPOSIT, WITHDRAW


def update_wallet_balance(amount, transaction_type, wallet_previous_balance):
    """method to update wallet on every transaction."""
    if transaction_type == DEPOSIT:
        wallet_previous_balance = wallet_previous_balance + amount
    elif transaction_type == WITHDRAW:
        wallet_previous_balance = wallet_previous_balance - amount
    return wallet_previous_balance


