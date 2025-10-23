from django.core.management.base import BaseCommand
from consulta_risco.models import Cupom, TipoCupom


class Command(BaseCommand):
    help = 'Atribui tipo de cupom padrão para cupons que não possuem tipo'

    def handle(self, *args, **options):
        # Obter o tipo de cupom padrão (Desconto)
        try:
            tipo_padrao = TipoCupom.objects.get(nome='Desconto')
        except TipoCupom.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Tipo de cupom "Desconto" não encontrado. Execute primeiro o comando popular_tipos_cupom.')
            )
            return

        # Atribuir tipo padrão para cupons sem tipo
        cupons_sem_tipo = Cupom.objects.filter(tipo_cupom__isnull=True)
        count = cupons_sem_tipo.count()
        
        if count > 0:
            cupons_sem_tipo.update(tipo_cupom=tipo_padrao)
            self.stdout.write(
                self.style.SUCCESS(f'{count} cupom(ns) atualizado(s) com tipo padrão "Desconto".')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Todos os cupons já possuem tipo atribuído.')
            )
































