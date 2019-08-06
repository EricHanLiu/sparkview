from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.http import JsonResponse
from bloom import settings
from rest_framework.response import Response
from client_area.models import Mandate, MandateType, MandateAssignment
from budget.models import Client, Team, Industry, Service, ClientContact
from user_management.models import Member
from django.core import serializers
import json
import datetime


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user or not user.is_staff:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def sample_api(request):
    data = {'sample_data': 123}
    return Response(data, status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def create_tracking_mandate(request):
    """
    Creates a mandate. Should be called from a zap. (https://zapier.com)
    :param request:
    :return:
    """
    service_type = request.data.get('service_type')
    if service_type.lower() != 'tracking onboarding':
        return Response({'error': 'Invalid service'},
                        status=HTTP_400_BAD_REQUEST)

    try:
        tracking_mandate_type = MandateType.objects.get(name='Tracking Onboarding')
    except MandateType.DoesNotExist:
        return Response({'error': 'Cannot find a mandate for tracking'},
                        status=HTTP_404_NOT_FOUND)

    account_name = request.data.get('account_name')

    try:
        account = Client.objects.get(client_name=account_name)
    except Client.DoesNotExist:
        return Response({'error': 'Cannot find that client'},
                        status=HTTP_404_NOT_FOUND)

    try:
        mandate, created = Mandate.objects.get_or_create(account=account, mandate_type=tracking_mandate_type)
    except Mandate.MultipleObjectsReturned:
        return Response({'error': 'Mandate already exists'},
                        status=HTTP_400_BAD_REQUEST)

    if not created:
        return Response({'error': 'Mandate already exists'},
                        status=HTTP_400_BAD_REQUEST)

    cost = request.data.get('cost')
    hourly = 125.0

    mandate.cost = cost
    mandate.hourly_rate = hourly

    today = datetime.datetime.today()
    in_two_weeks = today + datetime.timedelta(14)

    mandate.start_date = today
    mandate.end_date = in_two_weeks
    mandate.save()

    if settings.DEBUG:
        tracker = Member.objects.get(id=1)
    else:
        # Get Eric, this is hardcoded for now
        tracker = Member.objects.get(id=60)

    MandateAssignment.objects.create(member=tracker, mandate=mandate, percentage=100.0)

    return Response({'success': 'Mandate successfully created!'},
                    status=HTTP_200_OK)


@api_view(['POST'])
def get_budget_info(request):
    """
    Gets information about a budget
    :param request:
    :return:
    """
    pass


@api_view(['GET'])
def get_accounts(request):
    accounts = Client.objects.all()

    data = {
        'accounts': json.loads(serializers.serialize('json', accounts))
    }

    return Response(data, status=HTTP_200_OK)


@login_required
def search(request):
    query = request.POST.get('query')
    result = {
        'clients': [],
        'members': []
    }

    clients = Client.objects.filter(client_name__icontains=query)
    users = User.objects.filter(username__icontains=query)

    members = None
    if users.count() > 0:
        members = Member.objects.filter(user__in=users)

    for c in clients:
        item = {
            'name': c.client_name,
            'url': '/clients/accounts/' + str(c.id),
        }
        result['clients'].append(item)

    if members is not None:
        for u in members:
            item = {
                'name': u.user.get_full_name(),
                'url': '/user_management/members/' + str(u.id)
            }
            result['members'].append(item)
    return JsonResponse(result)
