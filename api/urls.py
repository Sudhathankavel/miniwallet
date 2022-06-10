from django.urls import path
from api.views import (WalletCreateAPIView, WalletEnableAPIView, WalletDepositAPI, WalletWithdrawAPI)

urlpatterns = [
    path('init', WalletCreateAPIView.as_view(), name='wallet_create'),
    path('wallet', WalletEnableAPIView.as_view(), name='wallet-enable'),
    path('wallet/deposits', WalletDepositAPI.as_view(), name='deposit'),
    path('wallet/withdrawals', WalletWithdrawAPI.as_view(), name='withdraw'),
]
