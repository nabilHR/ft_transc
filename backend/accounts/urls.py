from django.urls import path

from .views import RegisterUserView,Enable2FAView ,debugView,\
        VerifyUserEmail,LoginUserView, VerifyView, TestAuthenticationView, PasswordResetConfirm,\
        PasswordResetRequestView, SetNewPassword,LogoutUserView,_42Redirect , CollectAuthorizeCode, \
        ModelManagementView,    DeleteUser,testJs,FriendListView ,send_friend_request, \
        ReceiveFriendRequestListView,SentFriendRequestListView,RespondFriendRequestView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path('register/',RegisterUserView.as_view(),name='register'),
    path('verify-email/',VerifyUserEmail.as_view(),name='verify'),
    path('login/',LoginUserView.as_view(),name='login'),
    path('profile/',TestAuthenticationView.as_view(),name='granted'),
    path('password-reset/',PasswordResetRequestView.as_view(),name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/',PasswordResetConfirm.as_view(),name='password-reset-confirm'),
    path('set-password/',SetNewPassword.as_view(),name='set-password'),
    path('logout/',LogoutUserView.as_view(),name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('enable2FA/', Enable2FAView.as_view(), name='enable_2FA'),
    path('verify2FA/', VerifyView.as_view(), name='VerifyView_2FA'),
    path('debug/', debugView.as_view(), name='debug'),
    path('Redirect42', _42Redirect.as_view(), name='redirect'),
    path('2OAuth', CollectAuthorizeCode.as_view(), name='redirect11'),
    path('delete', DeleteUser.as_view(),name="delete this mdf") ,
    path('testJS', testJs,name="testJs this mdf"),
    path('friend-requests/friends', FriendListView.as_view(),name="friends"),
    path('friend-requests/invite/', send_friend_request.as_view(),name="friends"),
    path('manageModel/', ModelManagementView.as_view(),name="manage"),
    path('friend-requests/receive/', ReceiveFriendRequestListView.as_view(),name="friendRequestReceive"),
    path('friend-requests/sent/', SentFriendRequestListView.as_view(),name="friendRequestSent"),
    path('friend-requests/accept/', RespondFriendRequestView.as_view(),name="Respond"),

]
