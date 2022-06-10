from rest_framework import serializers
from api.models import Wallet, Customer, DISABLED, ENABLED, Transaction, SUCCESS, DEPOSIT, WITHDRAW
from django.conf import settings
from api.utils import update_wallet_balance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer."""

    customer_xid = serializers.UUIDField()

    class Meta:
        model = Customer
        fields = ('email', 'customer_xid',)


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet."""
    wallet_id = serializers.UUIDField(required=False)

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if data.get("is_disabled"):
            internal_value.update({
                'is_disabled': data.get('is_disabled')
            })
        return internal_value

    def __init__(self, *args, **kwargs):
        """Method initializes with context values."""
        super().__init__(*args, **kwargs)
        if self.context.get('request'):
            self.user = self.context.get('request').user

    class Meta:
        model = Wallet
        fields = ('wallet_id', 'owned_by', 'status', 'enabled_at', 'disabled_at', 'balance')
        read_only_fields = ('owned_by',)

    def get_status(self, obj):
        """To get display value of status."""
        return obj.get_status_display()

    def create(self, validated_data):
        if Wallet.objects.filter(owned_by=self.user).first():
            wallet_obj = Wallet.objects.filter(owned_by=self.user).get()
            if validated_data.get('is_disabled'):
                if wallet_obj.status == ENABLED:
                    wallet_obj.status = DISABLED
                    wallet_obj.save()
                    return wallet_obj
                raise serializers.ValidationError \
                    ({"detail": "Wallet is already disabled"})
            else:
                if wallet_obj.status == DISABLED:
                    wallet_obj.status = ENABLED
                    wallet_obj.save()
                    return wallet_obj
                raise serializers.ValidationError \
                    ({"detail": "Wallet is already enabled"})
        raise serializers.ValidationError \
            ({"detail": "Wallet not found"})


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions."""
    transaction_id = serializers.UUIDField(required=False)

    def __init__(self, *args, **kwargs):
        """Method initializes with context values."""
        super().__init__(*args, **kwargs)
        if self.context.get('request'):
            self.user = self.context.get('request').user
        if self.context.get('transaction'):
            self.transaction = self.context.get('transaction')

    class Meta:
        model = Transaction
        fields = ('transaction_id', 'transaction_by', 'status', 'transaction_at', 'amount',
                  'reference_id', 'transaction_type')
        read_only_fields = ('transaction_by',)

    def create(self, validated_data):
        if Wallet.objects.filter(owned_by=self.user).first():
            wallet_obj = Wallet.objects.filter(owned_by=self.user).get()
            if wallet_obj.status == ENABLED:
                if self.transaction == 'deposit':
                    wallet_deposit_obj = Transaction.objects.create(transaction_by=self.user,
                                                                    status=SUCCESS,
                                                                    amount=validated_data.get('amount'),
                                                                    reference_id=validated_data.
                                                                    get('reference_id'),
                                                                    transaction_type=DEPOSIT)
                    wallet_deposit_obj.save()
                    if validated_data.get('amount'):
                        current_balance = update_wallet_balance(validated_data.get('amount'), DEPOSIT,
                                                               wallet_obj.balance)
                        wallet_obj.balance = current_balance
                        wallet_obj.save()
                    return wallet_deposit_obj
                elif self.transaction == 'withdraw':
                    if validated_data.get('amount') <= wallet_obj.balance:
                        wallet_deposit_obj = Transaction.objects.create(transaction_by=self.user,
                                                                        status=SUCCESS,
                                                                        amount=validated_data.get(
                                                                            'amount'),
                                                                        reference_id=validated_data.
                                                                        get('reference_id'),
                                                                        transaction_type=WITHDRAW)
                        if validated_data.get('amount'):
                            current_balance = update_wallet_balance(validated_data.get('amount'),
                                                                    WITHDRAW,
                                                                    wallet_obj.balance)
                            wallet_obj.balance = current_balance
                            wallet_obj.save()
                        return wallet_deposit_obj
                raise serializers.ValidationError \
                    ({"detail": "Wallet is disabled"})
