import uuid
from django.shortcuts import render
import requests

from backend import settings# type: ignore
from .serializers import UserRegisterSerializer,LoginSerializer,PasswordResetRequestSerializer\
                            ,SetNewPasswordSerializer,LogoutUserSerializer,OTPSerializer
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from .utils import send_code_to_user
from .models import User
from rest_framework.generics import GenericAPIView# type: ignore
from .models import OneTimePassword
from rest_framework.permissions import IsAuthenticated# type: ignore
from django.utils.http import urlsafe_base64_decode# type: ignore
from django.utils.encoding import smart_str,DjangoUnicodeDecodeError# type: ignore
from django.contrib.auth.tokens import PasswordResetTokenGenerator# type: ignore
from django.core.cache import cache
from urllib.parse import quote

from .utils import generate_otp_secret, generate_otp_uri,verify_otp ,generate_qr_code

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

from django.shortcuts import redirect
from rest_framework.permissions import AllowAny  # type: ignore # Important for OAuth redirect

class RegisterUserView(GenericAPIView):
    serializer_class=UserRegisterSerializer

    def post(self,request):
        user_data=request.data
        serializer =self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            send_code_to_user(user_data['email'],user)
            return Response({
                'data':user_data,
                'message':f'hi {user_data['first_name']} thanks for signing up a passcode'
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyUserEmail(GenericAPIView):
    serializer_class=UserRegisterSerializer
    def post(self,request):
        otpcode=request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code=otpcode)
            if   not user_code_obj.user.is_verified:
                if  str(user_code_obj.code) == str(otpcode):
                    user_code_obj.user.is_verified = True
                    user_code_obj.user.is_active = True
                    user_code_obj.user.save()
                    return Response({
                        'message':'account email verified successfully'
                    },status=status.HTTP_200_OK)
            return Response(
                    {
                        'message':'code is invalid user already verified'
                    },status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({'message':'1 passcode not provided'}, status=status.HTTP_404_NOT_FOUND)

class VerifyView(GenericAPIView):
    serializer_class = OTPSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        print("Request Data:", request.data)
        if serializer.is_valid():
            id = cache.get(request.data.get("temp_token"))
            print("id ", id)
            user =User.objects.get(id=id)
            user_tokens = user.tokens()
            return Response({
                        'access_token': str(user_tokens['access']), 
                        'refresh_token': str(user_tokens['refresh'])  
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)

class  PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':"a link has been sent to  your email to reset your password"},status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    def get(self,request,uidb64,token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({'message':'token is invalid or has expired'},status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True,'message':'credentials is valid','uidb64':uidb64,'token':token},status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            return Response({'message':'token is invalid or has expired'},status=status.HTTP_401_UNAUTHORIZED)
    

class SetNewPassword(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message':'password reset successful'},status=status.HTTP_200_OK)
    

class LogoutUserView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_LogoutUserViewclasses=[IsAuthenticated]


    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Enable2FAView(GenericAPIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        user.otp_secret = generate_otp_secret()
        user.is_2fa_enabled = True
        user.save()

        otp_uri = generate_otp_uri(user)
        qr_code = generate_qr_code(otp_uri)
        print(qr_code)

        return Response({
            "otp_uri": otp_uri,
            "qr_code_url": qr_code,
        }, status=status.HTTP_200_OK)
        

class debugView(GenericAPIView):
    def get(self,request):
        user = request.user
        print(user)
        print(request)
        if (User.is_authenticated):
            print (True)
        else:
            print(False)
        return Response({"hello":"hello"},status=status.HTTP_200_OK)
class   _42Redirect(GenericAPIView):

    def get(self ,request):
        url = f"https://api.intra.42.fr/oauth/authorize?client_id={settings.API42_UID}&redirect_uri={settings.API42_REDIRECT_URI}&response_type=code&scope=public"
        return redirect(url)
    
from rest_framework.renderers import JSONRenderer # type: ignore

class CollectAuthorizeCode(GenericAPIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "No authorization code provided"}, status=400)

        token_url = "https://api.intra.42.fr/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.API42_UID,
            "client_secret": settings.API42_SECRET,
            "code": code,
            "redirect_uri": settings.API42_REDIRECT_URI,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch access token", "details": str(e)}, status=400)
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        if not access_token:
            return Response({"error": "Access token not found in response"}, status=400)

        user_url = "https://api.intra.42.fr/v2/me"

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(user_url, headers=headers)
        print("----------------------")
        print(response.text)
        print("----------------------")
        if response.status_code == 200:
            user_data = response.json()
            email = user_data.get("email")
            usr1 = User.objects.get(email=email)
            if usr1 is None:
                user = User.objects.create_user(
                id = user_data.get("id"),
                email= user_data.get("email"),
                first_name = user_data.get("first_name"),
                last_name = user_data.get("last_name"),
                )
                user.save()
                print(user)
            else:
                if user.is_2fa_enabled:
                    temp_token = str(uuid.uuid4()) 
                    cache.set(temp_token, user.id, timeout=10000)
                    return Response({"detail": "2FA required", "temp_token": temp_token},status=401)
                return Response({"access_token": access_token,"refresh_token":refresh_token}, status=200)
            #profile_image =  user_data.get("image"),
        else:
            print(f"Failed to fetch user data. Status code: {response.status_code}")
            print(f"Error message: {response.text}")
        return Response({"access_token": access_token,"refresh_token":refresh_token}, status=200)

class DeleteUser(GenericAPIView):
    def post(self ,request):
        id = request.data.get("id")
        print(id)
        user = User.objects.get(id = id)
        user.delete()
        print(user)
        return Response({"shrug":"shrug"})
    
    
def testJs(request):
    return render(request,"x.html")



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from friendship.models import Friend ,FriendshipRequest

User = get_user_model()  
class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user 
        friends = Friend.objects.friends(user) 

        friend_data = [{"id": friend.id, "username": friend.username} for friend in friends]
        return Response({"friends": friend_data})
    


# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
class send_friend_request(APIView):
        
    def post(self,request):
        from_user = request.user
        print("request " , request.data)
        email = request.data.get('email')  #
        to_user = User.objects.get(email = email)
        print("user: " , to_user)
        if Friend.objects.are_friends(from_user, to_user): 
            return  Response({"they are all ready friend"})
        if FriendshipRequest.objects.filter(from_user=from_user, to_user=to_user,  rejected__isnull=True).exists() or \
            FriendshipRequest.objects.filter(from_user=to_user, to_user=from_user, rejected__isnull=True).exists():
            return Response( {"the invitation already exist"})
        print(from_user, "   ",to_user)
        if from_user != to_user:
            print("im here 111") 
            friendship_request = friendship_request.objects.create(from_user=from_user, to_user=to_user)
            friendship_request.save() 

        return  Response({"the invitation sent successfully"})


