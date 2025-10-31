from django.core.management.base import BaseCommand
from consulta_risco.models import Cidade


class Command(BaseCommand):
    help = 'Remove cidades que nao tem posicao (nao estao no arquivo Excel)'

    def handle(self, *args, **options):
        # Contar cidades sem posição
        cidades_sem_posicao = Cidade.objects.filter(posicao__isnull=True)
        total_antes = Cidade.objects.count()
        
        self.stdout.write(f'Cidades sem posicao: {cidades_sem_posicao.count()}')
        self.stdout.write(f'Total de cidades antes: {total_antes}')
        
        if cidades_sem_posicao.count() > 0:
            # Remover cidades sem posição
            cidades_removidas = 0
            for cidade in cidades_sem_posicao:
                self.stdout.write(f'Removendo: {cidade.nome} - {cidade.estado.sigla}')
                cidade.delete()
                cidades_removidas += 1
            
            total_depois = Cidade.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nLimpeza concluida!\n'
                    f'   Cidades removidas: {cidades_removidas}\n'
                    f'   Cidades restantes: {total_depois}'
                )
            )
        else:
            self.stdout.write('Nenhuma cidade sem posicao encontrada!')















































