from django.core.management.base import BaseCommand
from consulta_risco.models import AdminUser
import hashlib


class Command(BaseCommand):
    help = 'Redefine a senha de um usuário admin'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário')
        parser.add_argument('password', type=str, help='Nova senha')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        try:
            user = AdminUser.objects.get(username=username)
            user.password = hashlib.sha256(password.encode()).hexdigest()
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Senha do usuário "{username}" redefinida com sucesso!')
            )
        except AdminUser.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário "{username}" não encontrado.')
            )
















