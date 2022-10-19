'''
user_app.urls
'''

from django.urls import path

from . import views




app_name = 'user_app'

urlpatterns = [
    path('create/', views.UserCreate.as_view(), name='create'),
    path('login/', views.UserLogin.as_view(), name= 'login'),
    path('profile/<uuid:uuid_value>/', views.UserProfile.as_view(), name = 'profile'),
    path('update/<uuid:uuid_value>/', views.UserUpdate.as_view(), name = 'update'),

    path('password_change/', views.UserPasswordChange.as_view(), name = 'password_change'),
    path('password_reset/', views.UserPasswordReset.as_view(), name = 'password_reset'),
    path('password_reset_done/', views.UserPasswordResetDone.as_view(), name = 'password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.UserPasswordResetConfirm.as_view(), name = 'password_reset_confirm'),

    path('email_verify/', views.UserEmailVerify.as_view(), name = 'email_verify'),
    path('email_change/', views.UserEmailChange.as_view(), name = 'email_change'),

    path('token/<uuid:uuid_value>/', views.TwilioTokenSendAgain.as_view(), name = 'twilio_token_send_again'),
    path('phone_verify/<uuid:uuid_value>/', views.UserPhoneVerify.as_view(), name = 'phone_verify'),
    path('phone_change/', views.UserPhoneChange.as_view(), name = 'phone_change'),

    path('otp_verify/', views.UserOTPVerify.as_view(), name= 'otp_verify'),

    path('logout/', views.UserLogout.as_view(), name = 'logout'),

    path('delete/', views.UserDelete.as_view(), name = 'delete'),
    ]

