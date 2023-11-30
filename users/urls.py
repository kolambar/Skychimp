from django.urls import path, include
from users.apps import UsersConfig
from users.views import LoginView, LogoutView, RegisterView, verify_view, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView

app_name = UsersConfig.name

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verifying/', verify_view),  # эндпоинт верификации почты

    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
