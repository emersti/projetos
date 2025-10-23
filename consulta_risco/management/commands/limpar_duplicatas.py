from django.core.management.base import BaseCommand
from consulta_risco.models import Estado, Cidade
from django.db.models import Count


class Command(BaseCommand):
    help = 'Remove cidades duplicadas do banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Iniciando limpeza de duplicatas...')
        
        # Contar duplicatas antes da limpeza
        duplicatas_antes = Cidade.objects.values('nome', 'estado').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()
        
        self.stdout.write(f'📊 Cidades com duplicatas encontradas: {duplicatas_antes}')
        
        if duplicatas_antes == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Nenhuma duplicata encontrada!')
            )
            return
        
        # Remover duplicatas mantendo apenas a primeira ocorrência
        cidades_removidas = 0
        
        # Agrupar por nome e estado
        grupos_duplicatas = Cidade.objects.values('nome', 'estado').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for grupo in grupos_duplicatas:
            nome = grupo['nome']
            estado_id = grupo['estado']
            
            # Buscar todas as cidades com esse nome e estado
            cidades_duplicadas = Cidade.objects.filter(
                nome=nome, 
                estado_id=estado_id
            ).order_by('id')
            
            # Manter a primeira e remover as demais
            primeira_cidade = cidades_duplicadas.first()
            cidades_para_remover = cidades_duplicadas.exclude(id=primeira_cidade.id)
            
            count_removidas = cidades_para_remover.count()
            cidades_para_remover.delete()
            cidades_removidas += count_removidas
            
            if count_removidas > 0:
                estado = Estado.objects.get(id=estado_id)
                self.stdout.write(
                    f'  🗑️ Removidas {count_removidas} duplicatas de {nome} - {estado.sigla}'
                )
        
        # Estatísticas finais
        total_estados = Estado.objects.count()
        total_cidades = Cidade.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Limpeza concluída!\n'
                f'   🗑️ Cidades duplicadas removidas: {cidades_removidas}\n'
                f'   🏛️ Estados no banco: {total_estados}\n'
                f'   🏙️ Cidades únicas no banco: {total_cidades}'
            )
        )
















































