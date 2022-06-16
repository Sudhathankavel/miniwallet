"""
API utility method module
"""
from api.models import DEPOSIT, WITHDRAW, Transaction
from django.db import transaction


def update_wallet_balance(amount, transaction_type, wallet_previous_balance):
    """method to update wallet on every transaction."""
    if transaction_type == DEPOSIT:
        wallet_previous_balance = wallet_previous_balance + amount
    elif transaction_type == WITHDRAW:
        wallet_previous_balance = wallet_previous_balance - amount
    return wallet_previous_balance


def create_transaction(transaction_by, status, amount, reference_id, transaction_type,
                       wallet_obj):
    """method to create atomic transaction.(deposit or withdraw)"""
    with transaction.atomic():
        wallet_deposit_obj = Transaction.objects.create(transaction_by=transaction_by,
                                                        status=status,
                                                        amount=amount,
                                                        reference_id=reference_id,
                                                        transaction_type=transaction_type)
        wallet_deposit_obj.save()
        current_balance = update_wallet_balance(amount,
                                                transaction_type,
                                                wallet_obj.balance)
        wallet_obj.balance = current_balance
        wallet_obj.save()
    return wallet_deposit_obj
