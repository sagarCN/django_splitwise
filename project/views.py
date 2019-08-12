from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets

from project.lib.utils import create_response, validate_users, get_balances
from project.models import ExpenseInfo, Expense, Category
from .serializers import CategoriesSerializer
from rest_framework.utils import json


def login_required():
    def view_name(func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return func(request, *args, **kwargs)
            else:
                return create_response(401)
        return wrapper
    return view_name


@csrf_exempt
@require_http_methods(['POST'])
def signup(request):
    request_body = json.loads(request.body)
    try:
        user = User.objects.create_user(username=request_body['email'],
                                        password=request_body['password'])
        resp = {"id": user.id}
        return create_response(201, resp)
    except KeyError:
        return create_response(400)
    except:
        return  create_response(403)


@csrf_exempt
@require_http_methods(['POST'])
def signin(request):
    request_body = json.loads(request.body)
    try:
        user = authenticate(request, username=request_body['email'],
                            password=request_body['password'])
        if user is not None:
            login(request, user)
            return create_response(200)
        else:
            return create_response(401)
    except:
        return create_response(400)


@csrf_exempt
@require_http_methods(['POST'])
def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return  create_response(204)
    return create_response(400)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
@login_required()
def expense(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        try:
            if validate_users(request_body['users'], request_body['total_amount'], request.user.id) == 0:
                return create_response(400)

            expense = Expense.objects.create(description=request_body['description'],
                                             total_amount=request_body['total_amount'],
                                             categories_id=request_body['categories']['id'])
            expense_infos = []
            for user in request_body['users']:
                expense_infos.append(ExpenseInfo(user_id=user['id'],
                                                 expense_id=expense.id,
                                                 owe=user['owe'],
                                                 lend=user['lend']
                                                 ))
            ExpenseInfo.objects.bulk_create(expense_infos)
            return create_response(201)
        except IntegrityError:
            return create_response(404)
        except:
            return create_response(400)

    if request.method == 'GET':
        expensesinfo_data = ExpenseInfo.objects.filter(user_id=request.user.id)

        expenses = {}
        for expense in expensesinfo_data:
            id = expense.expense_id
            if id not in expenses:
                expenses[id] = {}
            info = Expense.objects.get(id=id)
            expenses[id]['id'] = id
            expenses[id]['categories'] = {'id': info.categories_id}
            expenses[id]['description'] = info.description
            expenses[id]['total_amount'] = info.total_amount
            expenses[id]['users'] = []
            info = info.expenseinfo_set.all()
            for data in info:
                expenses[id]['users'].append({'id': data.user_id,
                                              'owe': data.owe,
                                              'lend': data.lend})
        resp = {
            'count': len(expenses),
            'expenses': list(expenses.values())
        }
        return create_response(200, resp)


@csrf_exempt
@require_http_methods(['GET', 'PUT', 'DELETE'])
@login_required()
def expense_id(request, e_id):
    if request.method == 'PUT':
        try:
            request_body = json.loads(request.body)

            if not ExpenseInfo.objects.filter(user_id=request.user.id, expense_id=e_id).exists():
                return create_response(403)

            info = Expense.objects.get(id=e_id)
            info.categories_id = request_body['categories']['id'] if 'categories' in request_body else {'id': info.categories_id}
            info.description = request_body['description'] if 'description' in request_body else info.description
            total_amount = info.total_amount
            info.total_amount = request_body['total_amount'] if 'total_amount' in request_body else info.total_amount

            if 'users' in request_body:
                if validate_users(request_body['users'], info.total_amount, request.user.id) == 0:
                    return create_response(400)

                ExpenseInfo.objects.filter(expense_id=e_id).delete()
                expense_infos = []
                for user in request_body['users']:
                    expense_infos.append(ExpenseInfo(user_id=user['id'],
                                                     expense_id=e_id,
                                                     owe=user['owe'],
                                                     lend=user['lend']
                                                     ))
                ExpenseInfo.objects.bulk_create(expense_infos)
            elif total_amount != info.total_amount:
                    return create_response(400)

            info.save()
            return create_response(201)
        except IntegrityError:
            return create_response(404)
        except:
            return create_response(400)

    if request.method == 'GET':
        try:
            is_present = ExpenseInfo.objects.filter(user_id=request.user.id, expense_id=e_id)

            if len(is_present) == 0:
                return create_response(403)

            expense = {}
            info = Expense.objects.get(id=e_id)
            expense['id'] = e_id
            expense['categories'] = {'id': info.categories_id}
            expense['description'] = info.description
            expense['total_amount'] = info.total_amount
            expense['users'] = []
            info = info.expenseinfo_set.all()
            for data in info:
                expense['users'].append({'id': data.user_id,
                                         'owe': data.owe,
                                         'lend': data.lend})
            resp = {'expenses': expense}
            return create_response(200, resp)
        except:
            return create_response(400)

    if request.method == 'DELETE':
        try:
            is_present = ExpenseInfo.objects.filter(user_id=request.user.id, expense_id=e_id)

            if len(is_present) == 0:
                return create_response(403)

            Expense.objects.get(id=e_id).delete()
            return create_response(200)

        except:
            return create_response(400)


@csrf_exempt
@require_http_methods(['GET'])
@login_required()
def balances(request):
    balances = get_balances(request.user.id)
    return create_response(200, balances)


@csrf_exempt
@require_http_methods(['GET'])
@login_required()
def balances_id(request, u_id):
    balances = get_balances(request.user.id, u_id)
    return create_response(200, balances)


@csrf_exempt
@require_http_methods(['POST'])
@login_required()
def settle(request):
    request_body = json.loads(request.body)
    u1 = request.user.id
    u2 = request_body['users']['id']
    balance = get_balances(u1, u2)['amount']

    if balance == 0:
        return create_response(200)
    else:
        expense = Expense.objects.create(description='Settlement',
                                         total_amount=abs(balance),
                                         categories_id=-1)
        ExpenseInfo.objects.create(user_id=u1,
                                   expense_id=expense.id,
                                   owe=balance if balance > 0 else 0,
                                   lend=-balance if balance < 0 else 0
                                   )
        ExpenseInfo.objects.create(user_id=u2,
                                   expense_id=expense.id,
                                   owe=-balance if balance < 0 else 0,
                                   lend=balance if balance > 0 else 0
                                   )
        resp = {'id': expense.id}
        return create_response(201, resp)


@csrf_exempt
@require_http_methods(['GET'])
@login_required()
def profile(request):
    u1 = request.user.id
    balances = get_balances(u1)
    outstanding = 0
    for val in balances['balances']:
        outstanding += val['amount']
    resp = {
        'outstanding_amount': outstanding
    }
    return create_response(200, resp)


class categoriesViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
