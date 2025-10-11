from django.core.management.base import BaseCommand
from consulta_risco.models import Estado, Cidade
import pandas as pd
import os


class Command(BaseCommand):
    help = 'Verifica cidades que nao estao no arquivo Excel'

    def handle(self, *args, **options):
        file_path = 'ResumoCriminalidadeCidades.xlsx'
        
        if not os.path.exists(file_path):
            self.stdout.write('ERRO: Arquivo nao encontrado')
            return

        try:
            # Ler o arquivo Excel
            df = pd.read_excel(file_path)
            df = df.dropna(subset=['UF', 'Municipio'])
            df['UF'] = df['UF'].str.strip().str.upper()
            df['Municipio'] = df['Municipio'].str.strip()
            df = df.drop_duplicates(subset=['UF', 'Municipio'], keep='first')
            
            # Criar conjunto de cidades válidas do Excel
            cidades_validas = set()
            for _, row in df.iterrows():
                uf = row['UF']
                municipio = row['Municipio']
                cidades_validas.add((municipio.upper(), uf))
            
            self.stdout.write(f'Cidades no Excel: {len(cidades_validas)}')
            self.stdout.write(f'Cidades no banco: {Cidade.objects.count()}')
            
            # Verificar cidades que nao estao no Excel
            cidades_nao_encontradas = []
            for cidade in Cidade.objects.all():
                chave_cidade = (cidade.nome.upper(), cidade.estado.sigla)
                if chave_cidade not in cidades_validas:
                    cidades_nao_encontradas.append((cidade.nome, cidade.estado.sigla))
            
            self.stdout.write(f'Cidades nao encontradas no Excel: {len(cidades_nao_encontradas)}')
            
            if cidades_nao_encontradas:
                self.stdout.write('\nPrimeiras 20 cidades nao encontradas:')
                for i, (nome, uf) in enumerate(cidades_nao_encontradas[:20]):
                    self.stdout.write(f'  {i+1}. {nome} - {uf}')
                
                if len(cidades_nao_encontradas) > 20:
                    self.stdout.write(f'  ... e mais {len(cidades_nao_encontradas) - 20} cidades')

        except Exception as e:
            self.stdout.write(f'ERRO: {str(e)}')





























