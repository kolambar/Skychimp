from random import randint
from django.contrib.auth.views import (PasswordResetDoneView as BasePasswordResetDoneView,
                                       PasswordResetView as BasePasswordResetView,
                                       PasswordResetConfirmView as BasePasswordResetConfirmView,
                                       PasswordResetCompleteView as BasePasswordResetCompleteView)
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from config import settings
from users.forms import UserForm
from users.models import User


# Create your views here.

class LoginView(BaseLoginView):
    template_name = 'users/login.html'


class LogoutView(BaseLogoutView):
    pass


class RegisterView(CreateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/register.html'

    def form_valid(self, form):

        # создает случайный пароль
        verified_password = ''
        for i in range(8):
            i = randint(0, 9)
            verified_password += str(i)

        # сохраняет пароль к пользователю, чтобы можно было авторизировать его
        form.verified_password = verified_password
        user = form.save(commit=False)
        user.verified_password = verified_password

        # Отправляет письмо на указанную почту со ссылкой. В ссылку встроен пароль для верификации этого пользователя
        send_mail(
            subject='Верификация почты',
            message=f'Если вы регистрировались в Skychimp, нажмите на ссылку: '
                    f'http://127.0.0.1:8000/users/verifying?code={user.verified_password}\n Так вы подтвердите почту',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def verify_view(request):
    code = int(request.GET.get('code'))  # получает код для верификации
    user = User.objects.get(verified_password=code)  # получает пользователя с этим кодом
    user.verified = True  # верифицирует его
    user.save()
    return render(request, 'users/verifying.html')


class PasswordResetView(BasePasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    from_email = settings.EMAIL_HOST_USER
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDoneView(BasePasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetCompleteView(BasePasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
    success_url = reverse_lazy('users:login')
