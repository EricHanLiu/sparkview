from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from adwords_dashboard.models import DependentAccount

class ListAdwordsAccounts(APIView):
    """
    View to list all addwords accounts in system.

    * Requires authentication.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all adwords accounts.
        """
        accounts = [acc.json for acc in DependentAccount.objects.filter()]
        return Response(accounts)
