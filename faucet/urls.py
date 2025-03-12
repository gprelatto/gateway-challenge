from django.urls import path
from .views import fund_wallet, faucet_stats

urlpatterns = [
    path('faucet/fund', fund_wallet, name='fund_wallet'),
    path('faucet/stats', faucet_stats, name='faucet_stats'),
]