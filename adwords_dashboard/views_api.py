from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Responsive

class HelloApiView(APIView):
    """Test API View."""

    def get(self, request, format):

        an_apiview = [
            'Uses HTTPasdasdasdasdasdasd',
            'lololol',
            'sal, asl pls',
            'Is mapped manually to URLs'
        ]

        return Response({'message': 'hello!', 'an_apiview': an_apiview})
