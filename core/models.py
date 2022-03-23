from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete = models.CASCADE)


    def __str__(self):
        return f"{self.user.username}"



class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Profile, on_delete = models.CASCADE)
    wallet_addr = models.CharField(max_length=500, blank = False, null = False)
    wallet_bal = models.IntegerField()
    time = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.wallet_addr}"

    def return_dollar(self):
        dollars = 45000 * self.wallet_bal
        return dollars

SENT_CHOICES = (

    ('RECEIVED', 'RECEIVED'),
    ('PENDING', 'PENDING'),

)

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=500, blank=False, null = False)
    sender = models.ForeignKey(Wallet, on_delete = models.PROTECT, related_name='sender')
    receiver = models.ForeignKey(Wallet, on_delete = models.PROTECT, related_name='receiver')
    transaction_cipher_key = models.CharField(max_length=500, blank = False, null=False)
    transaction_amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=SENT_CHOICES, null = True)
    time = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.transaction_id}"


class Receive_transaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_obj = models.ForeignKey(Transaction, on_delete = models.PROTECT)
    time = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.transaction_obj}"



class Notification(models.Model):
    id = models.AutoField(primary_key = True)
    Transaction_notification = models.ForeignKey(Transaction, on_delete = models.CASCADE)


    def __str__(self):
        return f"{self.Transaction_notification.transaction_id}"