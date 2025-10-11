from django.core.management.base import BaseCommand
from consulta_risco.models import Estado, Cidade
import pandas as pd
import os


class Command(BaseCommand):
    help = 'Remove cidades que não estão no arquivo Excel de criminalidade'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='ResumoCriminalidadeCidades.xlsx',
            help='Caminho para o arquivo Excel'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'ERRO: Arquivo nao encontrado: {file_path}')
            )
            return

        try:
            # Ler o arquivo Excel
            self.stdout.write('Lendo arquivo Excel...')
            df = pd.read_excel(file_path)
            
            # Verificar colunas necessárias
            required_columns = ['UF', 'Municipio']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f'ERRO: Colunas nao encontradas: {missing_columns}')
                )
                return

            # Limpar dados
            df = df.dropna(subset=['UF', 'Municipio'])
            df['UF'] = df['UF'].str.strip().str.upper()
            df['Municipio'] = df['Municipio'].str.strip()
            
            # Remover duplicatas
            df = df.drop_duplicates(subset=['UF', 'Municipio'], keep='first')
            
            # Criar conjunto de cidades válidas do Excel
            cidades_validas = set()
            for _, row in df.iterrows():
                uf = row['UF']
                municipio = row['Municipio']
                cidades_validas.add((municipio.upper(), uf))
            
            self.stdout.write(f'Cidades validas no Excel: {len(cidades_validas)}')
            
            # Contar cidades antes da limpeza
            total_cidades_antes = Cidade.objects.count()
            
            # Encontrar cidades que não estão no Excel
            cidades_para_remover = []
            
            for cidade in Cidade.objects.all():
                chave_cidade = (cidade.nome.upper(), cidade.estado.sigla)
                if chave_cidade not in cidades_validas:
                    cidades_para_remover.append(cidade)
            
            self.stdout.write(f'Cidades para remover: {len(cidades_para_remover)}')
            
            if cidades_para_remover:
                # Remover cidades
                for cidade in cidades_para_remover:
                    self.stdout.write(f'  Removendo: {cidade.nome} - {cidade.estado.sigla}')
                    cidade.delete()
                
                # Estatísticas finais
                total_cidades_depois = Cidade.objects.count()
                cidades_removidas = total_cidades_antes - total_cidades_depois
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nLimpeza concluida!\n'
                        f'   Cidades removidas: {cidades_removidas}\n'
                        f'   Cidades restantes: {total_cidades_depois}\n'
                        f'   Cidades validas no Excel: {len(cidades_validas)}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Todas as cidades estao no arquivo Excel!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'ERRO ao processar arquivo: {str(e)}')
            )
