from django.db import models

class Transaction(models.Model):
    wallet_to = models.CharField(max_length=42)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    transaction_id = models.CharField(max_length=66, null=True, blank=True)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet_to} - {self.status}"