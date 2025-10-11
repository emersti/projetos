import pandas as pd
from django.core.management.base import BaseCommand
from consulta_risco.models import Estado, Cidade
import os


class Command(BaseCommand):
    help = 'Importa dados de criminalidade do arquivo Excel para o banco de dados'

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
                self.style.ERROR(f'ERRO: Arquivo não encontrado: {file_path}')
            )
            return

        try:
            # Ler o arquivo Excel
            self.stdout.write('Lendo arquivo Excel...')
            df = pd.read_excel(file_path)
            
            # Verificar colunas necessárias
            required_columns = ['UF', 'Municipio', 'Posicao']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f'ERRO: Colunas não encontradas: {missing_columns}')
                )
                self.stdout.write(f'Colunas disponíveis: {list(df.columns)}')
                return

            # Limpar dados
            df = df.dropna(subset=['UF', 'Municipio'])
            df['UF'] = df['UF'].str.strip().str.upper()
            df['Municipio'] = df['Municipio'].str.strip()
            df['Posicao'] = df['Posicao'].fillna(0).astype(int)
            
            # Remover duplicatas baseado em UF + Municipio
            df = df.drop_duplicates(subset=['UF', 'Municipio'], keep='first')
            self.stdout.write(f'Registros únicos após remoção de duplicatas: {len(df)}')

            # Mapear UFs para nomes completos dos estados
            uf_to_estado = {
                'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
                'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
                'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
                'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
                'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
                'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
                'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
            }

            # Criar/atualizar estados
            self.stdout.write('Criando/atualizando estados...')
            estados_criados = 0
            for uf, nome_estado in uf_to_estado.items():
                estado, created = Estado.objects.get_or_create(
                    sigla=uf,
                    defaults={'nome': nome_estado}
                )
                if created:
                    estados_criados += 1
                    self.stdout.write(f'  Estado criado: {nome_estado} ({uf})')

            # Criar/atualizar cidades
            self.stdout.write('Criando/atualizando cidades...')
            cidades_criadas = 0
            cidades_atualizadas = 0
            
            for _, row in df.iterrows():
                uf = row['UF']
                municipio = row['Municipio']
                posicao = row['Posicao']
                
                if uf in uf_to_estado:
                    try:
                        estado = Estado.objects.get(sigla=uf)
                        cidade, created = Cidade.objects.get_or_create(
                            nome=municipio,
                            estado=estado,
                            defaults={'posicao': posicao}
                        )
                        if created:
                            cidades_criadas += 1
                        else:
                            # Atualizar posição se a cidade já existir
                            if cidade.posicao != posicao:
                                cidade.posicao = posicao
                                cidade.save()
                            cidades_atualizadas += 1
                    except Estado.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  AVISO: Estado não encontrado para UF: {uf}')
                        )

            # Estatísticas finais
            total_estados = Estado.objects.count()
            total_cidades = Cidade.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nImportação concluída!\n'
                    f'   Total de registros no Excel: {len(df)}\n'
                    f'   Estados no banco: {total_estados}\n'
                    f'   Cidades no banco: {total_cidades}\n'
                    f'   Novas cidades criadas: {cidades_criadas}\n'
                    f'   Cidades atualizadas: {cidades_atualizadas}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'ERRO: Erro ao importar dados: {str(e)}')
            )
