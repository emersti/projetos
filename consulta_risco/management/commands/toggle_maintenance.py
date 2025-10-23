from django.core.management.base import BaseCommand
from consulta_risco.maintenance_config import MAINTENANCE_MODE
import os


class Command(BaseCommand):
    help = 'Ativa ou desativa o modo de manutenção do site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--on',
            action='store_true',
            help='Ativa o modo de manutenção',
        )
        parser.add_argument(
            '--off',
            action='store_true',
            help='Desativa o modo de manutenção',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mostra o status atual do modo de manutenção',
        )

    def handle(self, *args, **options):
        config_file = 'consulta_risco/maintenance_config.py'
        
        if options['status']:
            status = "ATIVO" if MAINTENANCE_MODE else "INATIVO"
            self.stdout.write(
                self.style.SUCCESS(f'Modo de manutenção: {status}')
            )
            return
        
        if options['on']:
            self.activate_maintenance(config_file)
        elif options['off']:
            self.deactivate_maintenance(config_file)
        else:
            # Se nenhuma opção for especificada, alterna o estado atual
            if MAINTENANCE_MODE:
                self.deactivate_maintenance(config_file)
            else:
                self.activate_maintenance(config_file)

    def activate_maintenance(self, config_file):
        """Ativa o modo de manutenção"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substitui MAINTENANCE_MODE = False por MAINTENANCE_MODE = True
            new_content = content.replace(
                'MAINTENANCE_MODE = False',
                'MAINTENANCE_MODE = True'
            )
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Modo de manutenção ATIVADO!')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  O site agora redirecionará para a página de manutenção')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao ativar modo de manutenção: {e}')
            )

    def deactivate_maintenance(self, config_file):
        """Desativa o modo de manutenção"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substitui MAINTENANCE_MODE = True por MAINTENANCE_MODE = False
            new_content = content.replace(
                'MAINTENANCE_MODE = True',
                'MAINTENANCE_MODE = False'
            )
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Modo de manutenção DESATIVADO!')
            )
            self.stdout.write(
                self.style.SUCCESS('🎉 O site voltou ao funcionamento normal')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao desativar modo de manutenção: {e}')
            )




















































