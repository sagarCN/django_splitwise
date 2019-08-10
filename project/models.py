from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)


class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    description = models.CharField(max_length=200)
    # members = models.ManyToManyField(User, through='ExpenseInfo')


class ExpenseInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    owe = models.FloatField()
    lend = models.FloatField()

