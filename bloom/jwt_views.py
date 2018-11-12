from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework import serializers
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from bloom import settings
import json
import jwt

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  @classmethod
  def get_token(cls, user):
    token = super(CustomTokenObtainPairSerializer, cls).get_token(user)

    #Add Custom Claims
    token['username'] = user.username
    token['id'] = user.id

    return token

class CustomTokenObtainPairView(TokenObtainPairView):
  serializer_class = CustomTokenObtainPairSerializer 


class CustomTokenVerifyView(TokenVerifyView):
  
  def post(self, request):
    try:
      claims = jwt.decode(json.loads(request.body)['token'], settings.SECRET_KEY)
    except jwt.exceptions.ExpiredSignature:
      raise InvalidToken

    super().post(request)
    ctx = {"id":claims["user_id"], "username": claims["username"]}
    
    
    return Response(ctx)
