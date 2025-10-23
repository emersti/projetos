from django.core.management.base import BaseCommand
from consulta_risco.models import Cupom


class Command(BaseCommand):
    help = 'Corrige a ordem de exibição dos cupons para garantir sequência única'

    def handle(self, *args, **options):
        # Obter todos os cupons ordenados por ordem_exibicao atual
        cupons = Cupom.objects.all().order_by('ordem_exibicao', 'id')
        
        self.stdout.write(f'Encontrados {cupons.count()} cupons para reordenar...')
        
        # Reordenar com sequência única
        for index, cupom in enumerate(cupons, 1):
            if cupom.ordem_exibicao != index:
                self.stdout.write(f'Reordenando cupom "{cupom.titulo}" de {cupom.ordem_exibicao} para {index}')
                cupom.ordem_exibicao = index
                cupom.save(update_fields=['ordem_exibicao'])
        
        self.stdout.write(
            self.style.SUCCESS('Reordenação concluída com sucesso!')
        )


























