from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import UserSerializer, UserListSerializer, BlockUserSerializer, UnblockUserSerializer, TokenSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db import IntegrityError
import pytz
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


"""signup api view which uses the django token authentication
class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            # Check for specific constraint violations
            if 'username' in str(e):  # Username constraint violation
                return Response({'error': 'Username already exists. Choose a different username.'}, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in str(e):  # Email constraint violation
                return Response({'error': 'Email already exists. Use a different email address.'}, status=status.HTTP_400_BAD_REQUEST)
            else:  # Unidentified constraint violation (optional)
                return Response({'error': 'An error occurred during registration. Please try again later.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

#signup api view that uses the jwt refresh and access tokenn
class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                # Handle specific constraint violations for username and email
                if 'username' in str(e):
                    error_message = 'Username already exists. Choose a different username.'
                elif 'email' in str(e):
                    error_message = 'Email already exists. Use a different email address.'
                else:
                    error_message = 'An error occurred during registration. Please try again later.'
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as e:  # Catch custom validation errors from UserSerializer
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""login api view that uses the django token authentication
class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_blocked:
                return Response({'error': 'User is blocked. Please contact administrator.'}, status=status.HTTP_403_FORBIDDEN)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
"""

#login api view using jwt authentication
class LoginAPIView(APIView):
    token_expire_minutes = 1  # Set access token expiration to 1 minutes

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Implement user authentication logic (e.g., using Django's authenticate)
        try:
            user = authenticate(username=username, password=password)
        except Exception as e:  # Catch any exceptions during authentication
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        if user:
            # Check if user is blocked before generating token
            if user.is_blocked:
                return Response({'error': 'User is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

            # Set expiration time for access token
            access_token = RefreshToken.for_user(user)
            access_token.set_exp(lifetime=timedelta(minutes=self.token_expire_minutes))


            return Response({'access': str(access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    


class RootView(APIView):
    def get(self, request):
        return Response ({"Message": "Api is up and running."}, status=status.HTTP_200_OK)
    


class DeleteUserView(APIView):
    def delete(self, request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=204)
    
    
class BlockUserView(APIView):
    def post(self, request):
        serializer = BlockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user_to_block = User.objects.get(email=email)
            if user_to_block.is_blocked:
                raise ValidationError("User with this email is already blocked.")
            user_to_block.is_blocked = True
            user_to_block.save()
            return Response({"Message": "User blocked successfully."})
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")

class UnblockUserView(APIView):
    def post(self, request):
        serializer = UnblockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user_to_unblock = User.objects.get(email=email)
            if not user_to_unblock.is_blocked:
                raise ValidationError("User with this email is not blocked.")
            user_to_unblock.is_blocked = False
            user_to_unblock.save()
            return Response({"message": "User unblocked successfully."})
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")
        

class ListBlockedUsersAPIView(APIView):
    # Optional: Permission class to restrict access (replace with your logic)
    # permission_classes = [IsAdminUser]  # Example permission class

    def get(self, request):
        # Filter blocked users based on the is_blocked field
        blocked_users = get_user_model().objects.filter(is_blocked=True)
        serializer = UserSerializer(blocked_users, many=True) 
        # Replace with your User Serializer
        if blocked_users:
            return Response((serializer.data), status=status.HTTP_302_FOUND)
        return Response({"There are no blocked users"}, status=status.HTTP_204_NO_CONTENT)