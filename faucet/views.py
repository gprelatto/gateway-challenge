from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer, FundWalletSerializer, AnalyticsSerializer
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from web3 import Web3
from django.conf import settings

@swagger_auto_schema(method='post', request_body=FundWalletSerializer, responses={201: TransactionSerializer})
@api_view(['POST'])
def fund_wallet(request):
    serializer = FundWalletSerializer(data=request.data)
    if serializer.is_valid():
        wallet_to_fund = serializer.validated_data['wallet_to']
        # Initialize web3
        web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))

        # Check if the wallet address is valid
        if not web3.is_address(wallet_to_fund):
            return Response({"error": "Invalid wallet address"}, status=status.HTTP_400_BAD_REQUEST)

        # Check rate limit
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_transactions = Transaction.objects.filter(
            created_at__gte=one_minute_ago,
            wallet_to=wallet_to_fund
        )
        if recent_transactions.exists():
            return Response({"error": "Rate limit exceeded. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # before tx, we get the gas price from network:
        gas_price = web3.eth.gas_price
        
        # Prepare the transaction
        nonce = web3.eth.get_transaction_count(settings.FAUCET_WALLET_ADDRESS)
        transaction = {
            'nonce': nonce,
            'to': wallet_to_fund,
            'value': web3.to_wei(0.0001, 'ether'),
            'gasPrice': gas_price,
            'chainId': int(settings.WEB3_CHAIN_ID)
        }

        # Then, we estimate the gas required for the transaction
        gas = web3.eth.estimate_gas(transaction)
        transaction['gas'] = gas

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, settings.FAUCET_WALLET_PK)

        # try to send the tx
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            # Save tx record
            transaction = Transaction.objects.create(
                wallet_to=wallet_to_fund,
                status='success',
                transaction_id=tx_receipt.transactionHash.hex()
            )
            transaction_serializer = TransactionSerializer(transaction)
            return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Save tx record
            transaction = Transaction.objects.create(
                wallet_to=wallet_to_fund,
                status='failed'
            )            
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: AnalyticsSerializer})
@api_view(['GET'])
def faucet_stats(request):
    one_day_ago = timezone.now() - timedelta(days=1)
    successful_transactions = Transaction.objects.filter(status='success', created_at__gte=one_day_ago).count()
    failed_transactions = Transaction.objects.filter(status='failed', created_at__gte=one_day_ago).count()
    return Response({
        "successful_transactions": successful_transactions,
        "failed_transactions": failed_transactions
    })