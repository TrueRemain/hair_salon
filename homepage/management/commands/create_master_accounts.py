from django.core.management.base import BaseCommand
from homepage.models import MasterAccount
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Создание начальных аккаунтов для мастеров'
    
    def handle(self, *args, **kwargs):
        masters_data = [
            {
                'username': 'alexander',
                'password': 'alex123',  # Простой пароль для примера
                'master_code': 'alexander',
                'display_name': 'Александр Петров'
            },
            {
                'username': 'mikhail',
                'password': 'misha123',
                'master_code': 'mikhail',
                'display_name': 'Михаил Козлов'
            },
            {
                'username': 'dmitry',
                'password': 'dima123',
                'master_code': 'dmitry',
                'display_name': 'Дмитрий Соколов'
            },
            {
                'username': 'admin',
                'password': '1234',
                'master_code': 'admin',
                'display_name': 'Администратор'
            }
        ]
        
        created_count = 0
        for master_data in masters_data:
            if not MasterAccount.objects.filter(username=master_data['username']).exists():
                MasterAccount.objects.create(
                    username=master_data['username'],
                    password=make_password(master_data['password']),
                    master_code=master_data['master_code'],
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Создан аккаунт для {master_data["display_name"]}')
                )
                created_count += 1
            else:
                # Обновляем пароль если аккаунт уже существует
                account = MasterAccount.objects.get(username=master_data['username'])
                account.password = make_password(master_data['password'])
                account.save()
                self.stdout.write(
                    self.style.WARNING(f'Обновлен пароль для {master_data["display_name"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Создано/обновлено {created_count} аккаунтов мастеров')
        )