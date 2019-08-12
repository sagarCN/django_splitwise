from rest_framework import serializers

from .models import Category, Expense, ExpenseInfo


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ExpenseInfoSerializer(serializers.HyperlinkedModelSerializer):#
    class Meta:
        model = ExpenseInfo
        fields = ('id', 'owe', 'lend')


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ('id', 'categories_id', 'total_amount', 'description')
