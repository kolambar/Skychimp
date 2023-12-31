from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email='admin@gmail.com').exists():
            user = User.objects.create(
                email='admin@gmail.com',  # Логин
                first_name='Admin',
                last_name='Admin',
                verified_password=1,
                verified=True,
                is_superuser=True,
                is_staff=True,
                is_active=True
            )

            user.set_password('6002')  # Пароль
            user.save()
