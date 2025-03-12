from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from .models import Transaction

class FaucetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_wallet_address = "0x0000000000000000000000000000000000000000"
        self.invalid_wallet_address = "0xInvalidAddress"
        self.fund_url = "/api/faucet/fund"
        self.stats_url = "/api/faucet/stats"

    @patch('faucet.views.Web3')
    def test_fund_wallet_success(self, MockWeb3):
        with self.subTest("should succeed if valid wallet address is provided"):
            mock_web3 = MockWeb3.return_value
            mock_web3.is_address.return_value = True
            mock_web3.eth.get_transaction_count.return_value = 1
            mock_web3.eth.gas_price = 20000000000
            mock_web3.eth.estimate_gas.return_value = 21000
            mock_web3.eth.account.sign_transaction.return_value = MagicMock(rawTransaction=b'signed_tx')
            mock_web3.eth.send_raw_transaction.return_value = b'tx_hash'
            mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock(transactionHash=b'tx_hash')

            response = self.client.post(self.fund_url, {"wallet_to": self.valid_wallet_address}, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("transaction_id", response.data)

    @patch('faucet.views.Web3')
    def test_fund_wallet_invalid_address(self, MockWeb3):
        with self.subTest("should fail if invalid wallet address is provided"):
            mock_web3 = MockWeb3.return_value
            mock_web3.is_address.return_value = False

            response = self.client.post(self.fund_url, {"wallet_to": self.invalid_wallet_address}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    @patch('faucet.views.Web3')
    def test_fund_wallet_rate_limit(self, MockWeb3):
        with self.subTest("should fail if rate limit is exceeded"):
            mock_web3 = MockWeb3.return_value
            mock_web3.is_address.return_value = True
            mock_web3.eth.get_transaction_count.return_value = 1
            mock_web3.eth.gas_price = 20000000000
            mock_web3.eth.estimate_gas.return_value = 21000
            mock_web3.eth.account.sign_transaction.return_value = MagicMock(rawTransaction=b'signed_tx')
            mock_web3.eth.send_raw_transaction.return_value = b'tx_hash'
            mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock(transactionHash=b'tx_hash')

            self.client.post(self.fund_url, {"wallet_to": self.valid_wallet_address}, format='json')
            response = self.client.post(self.fund_url, {"wallet_to": self.valid_wallet_address}, format='json')
            self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertIn("error", response.data)

    def test_faucet_stats(self):
        with self.subTest("should return correct statistics"):
            # Create some transactions
            Transaction.objects.create(wallet_to=self.valid_wallet_address, status='success', transaction_id='tx1')
            Transaction.objects.create(wallet_to=self.valid_wallet_address, status='failed', transaction_id='tx2')

            response = self.client.get(self.stats_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["successful_transactions"], 1)
            self.assertEqual(response.data["failed_transactions"], 1)
