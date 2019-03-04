import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client
from client_area.models import PhaseTask, PhaseTaskAssignment
from notifications.models import Notification


def main():
    """
    Creates the tasks and notifications of a ninety days stuff
    :return:
    """
    accounts = Client.objects.filter(status=1)

    for account in accounts:
        phase = account.phase
        phase_day = account.phase_day
        tier = account.tier

        tasks = PhaseTask.objects.filter(phase=phase, day=phase_day, tier=tier)
        for task in tasks:
            PhaseTaskAssignment.objects.create(task=task, account=account)
            roles = task.roles
            members_by_roles = account.members_by_roles(roles)
            for member in members_by_roles:
                link = '/clients/accounts/' + int(account.id)
                Notification.objects.create(message=task.message, link=link, member=member, severity=0, type=0)
            # for member in task.members.all(): # Needs fixing
            #     link = '/clients/accounts/' + int(account.id)
            #     Notification.objects.create(message=task.message, link=link, member=member, severity=0, type=0)


main()
