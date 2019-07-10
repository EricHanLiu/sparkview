from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from bloom import settings
from rest_framework.response import Response
from client_area.models import Mandate, MandateType, MandateAssignment
from budget.models import Client, Team, Industry, Service, ClientContact
from user_management.models import Member
from django.core.serializers import serialize
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


@csrf_exempt
@api_view(['GET'])
def get_client_details_objects(request):
    teams = Team.objects.all()
    industries = Industry.objects.all()

    data = {
        'teams': json.loads(serialize('json', teams)),
        'industries': json.loads(serialize('json', industries)),
    }
    return Response(data, status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def set_client_details(request):
    # TODO: add validation
    account_id = request.POST.get('account_id')
    bc_link = request.POST.get('bc_link')
    description = request.POST.get('description')
    notes = request.POST.get('notes')
    url = request.POST.get('url')
    contact_names = request.POST.getlist('contact_names')
    contact_emails = request.POST.getlist('contact_emails')
    contact_phones = request.POST.getlist('contact_phones')
    industry_id = request.POST.get('industry')
    team_ids = request.POST.getlist('teams')

    account = Client.objects.get(id=account_id)
    account.bc_link = bc_link
    account.description = description
    account.notes = notes
    account.url = url
    account.industry = Industry.objects.get(pk=industry_id)
    teams = Team.objects.filter(pk__in=team_ids)
    account.team.set(teams)

    for i, contact in enumerate(account.contactInfo.all()):
        contact.name = contact_names[i]
        contact.email = contact_emails[i]
        if contact_phones and contact_phones[i]:
            contact.phone = contact_phones[i]
        contact.save()

    account.save()

    return Response(status=HTTP_200_OK)
