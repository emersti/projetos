from django.core.management.base import BaseCommand
from consulta_risco.models import PaginaAtualizacao

class Command(BaseCommand):
    help = 'Atualiza a data de última atualização de uma página específica'

    def add_arguments(self, parser):
        parser.add_argument('pagina', type=str, help='Nome da página (ex: lgpd, faq, sobre)')
        parser.add_argument('--descricao', type=str, help='Descrição da atualização')

    def handle(self, *args, **options):
        pagina = options['pagina']
        descricao = options.get('descricao', f'Atualização da página {pagina}')
        
        try:
            data_atualizada = PaginaAtualizacao.atualizar_pagina(pagina, descricao)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Página "{pagina}" atualizada com sucesso!\n'
                    f'📅 Data: {data_atualizada.strftime("%d/%m/%Y às %H:%M")}\n'
                    f'📝 Descrição: {descricao}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao atualizar página "{pagina}": {str(e)}')
            )



















