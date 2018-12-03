from bloom import celery_app
from django.shortcuts import get_object_or_404
from budget.models import Client, AccountBudgetSpendHistory
from django.contrib.auth.models import User
from client_area.models import AccountAllocatedHoursHistory
from user_management.models import Member
from datetime import datetime
from datetime import date

@celery_app.task(bind=True)
def create_notifications(self):
    pass
