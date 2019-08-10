from rest_framework import serializers

from .models import Category, Expense, ExpenseInfo


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

#
# class ExpenseInfoSerializer(serializers.HyperlinkedModelSerializer):
#     id = serializers.ReadOnlyField(source='User.id')
#
#     class Meta:
#         model = ExpenseInfo
#         fields = ('id', 'owe', 'lend')
        # read_only_fields = ('expense_id')
#
#
# class ExpenseSerializer(serializers.ModelSerializer):
#     members = ExpenseInfoSerializer(source='expenseinfo_set', many=True)
#
#     class Meta:
#         model = Expense
#         fields = ('id', 'categories_id', 'total_amount', 'description', 'members')


    # def create(self, validated_data):
    #     return Expense.objects.create(**validated_data)


