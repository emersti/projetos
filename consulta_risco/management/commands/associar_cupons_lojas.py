from django.core.management.base import BaseCommand
from consulta_risco.models import Cupom, TipoCupom


class Command(BaseCommand):
    help = 'Associa cupons às lojas corretas baseado no nome da loja'

    def handle(self, *args, **options):
        cupons = Cupom.objects.all()
        lojas = TipoCupom.objects.all()
        
        # Criar um dicionário para mapear nomes de lojas
        lojas_dict = {loja.nome.lower(): loja for loja in lojas}
        
        associados = 0
        nao_associados = []
        
        for cupom in cupons:
            loja_nome = cupom.loja.lower()
            
            # Tentar encontrar a loja correspondente
            if loja_nome in lojas_dict:
                cupom.tipo_cupom = lojas_dict[loja_nome]
                cupom.save()
                associados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Cupom {cupom.id} ({cupom.loja}) associado à loja {lojas_dict[loja_nome].nome}')
                )
            else:
                nao_associados.append(cupom.loja)
                self.stdout.write(
                    self.style.WARNING(f'Cupom {cupom.id} ({cupom.loja}) não encontrou loja correspondente')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nResumo:')
        )
        self.stdout.write(f'Cupons associados: {associados}')
        self.stdout.write(f'Cupons não associados: {len(nao_associados)}')
        
        if nao_associados:
            self.stdout.write(
                self.style.WARNING(f'Lojas não encontradas: {set(nao_associados)}')
            )




























