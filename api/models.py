import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User, UserManager
from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

DISABLED = 1
ENABLED = 2
WALLET_STATUS = (
    (DISABLED, _('Disabled')),
    (ENABLED, _('Enabled'))
)

status = [('success', 'success'), ('failed', 'failed')]
transaction = [('deposit', 'deposit'), ('withdraw', 'withdraw')]
SUCCESS = 1
FAILED = 2
TRANSACTION_STATUS = (
    (SUCCESS, _('Success')),
    (FAILED, _('Failed')),
)

DEPOSIT = 1
WITHDRAW = 2
TRANSACTION_TYPE = (
    (DEPOSIT, _("Deposit")),
    (WITHDRAW, _('Withdraw'))
)


class UserManager(BaseUserManager):
    """Custom manager class for user model."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given username, email, and password."""
        email = self.normalize_email(email)
        username = str(email).lower()
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """Create user override method."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create super user override method."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Customer(AbstractUser):
    customer_xid = models.UUIDField(max_length=500, primary_key=True, default=uuid.uuid4)
    phone_no = models.CharField(max_length=10)
    USERNAME_FIELD = 'customer_xid'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return "{}".format(self.customer_xid)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


@receiver(post_save, sender=Customer)
def create_token(sender, instance=None, created=False, **kwargs):
    """To create token on user create."""
    if created:
        Token.objects.create(user=instance)


class Wallet(models.Model):
    """Model for Wallet"""
    wallet_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    owned_by = models.ForeignKey(Customer, related_name='wallet_cust',
                                 on_delete=models.deletion.CASCADE)
    status = models.PositiveSmallIntegerField(choices=WALLET_STATUS, default=DISABLED)
    enabled_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    disabled_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    balance = models.IntegerField(default=0, null=True, blank=True)


class Transaction(models.Model):
    """Model for Transaction"""
    transaction_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    transaction_by = models.ForeignKey(Customer, related_name='transaction_cust',
                                       on_delete=models.deletion.CASCADE)
    status = models.PositiveSmallIntegerField(choices=TRANSACTION_STATUS, null=True, blank=True)

    transaction_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    amount = models.IntegerField(default=0, null=False, blank=False)
    reference_id = models.UUIDField(default=uuid.uuid4, unique=True)
    transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPE, null=True,
                                                        blank=True)


