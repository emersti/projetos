import pandas as pd
from django.core.management.base import BaseCommand
from consulta_risco.models import Estado, Cidade, SistemaAtualizacao, PaginaAtualizacao
import os
import unicodedata


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

            # Normalizar cabeçalhos para lidar com acentos/variações (ex.: Município/Posição)
            def normalize_header(name):
                if not isinstance(name, str):
                    return name
                n = unicodedata.normalize('NFKD', name)
                n = ''.join(c for c in n if not unicodedata.combining(c))  # remove acentos
                n = n.strip().lower()
                return n

            original_cols = list(df.columns)
            normalized_cols = [normalize_header(c) for c in df.columns]
            df.columns = normalized_cols

            # Mapear para nomes canônicos esperados
            col_map = {
                'uf': 'UF',
                'municipio': 'Municipio',
                'município': 'Municipio',
                'municipio*': 'Municipio',
                'posicao': 'Posicao',
                'posição': 'Posicao',
                'posiçao': 'Posicao',
                'posição*': 'Posicao',
            }

            canonical = {}
            for c in df.columns:
                key = c
                if key in col_map:
                    canonical[col_map[key]] = c

            required_columns = ['UF', 'Municipio', 'Posicao']
            missing_columns = [col for col in required_columns if col not in canonical]
            
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f'ERRO: Colunas não encontradas: {missing_columns}')
                )
                self.stdout.write(f'Colunas disponíveis (originais): {original_cols}')
                return

            # Limpar dados
            uf_col = canonical['UF']
            mun_col = canonical['Municipio']
            pos_col = canonical['Posicao']

            df = df.dropna(subset=[uf_col, mun_col])
            df[uf_col] = df[uf_col].astype(str).str.strip().str.upper()
            df[mun_col] = df[mun_col].astype(str).str.strip()

            # Converter posição para inteiro de forma segura
            df[pos_col] = pd.to_numeric(df[pos_col], errors='coerce')
            df[pos_col] = df[pos_col].fillna(0).astype(int)
            
            # Remover duplicatas baseado em UF + Municipio
            df = df.drop_duplicates(subset=[uf_col, mun_col], keep='first')
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
                uf = row[uf_col]
                municipio = row[mun_col]
                posicao = int(row[pos_col]) if row[pos_col] is not None else 0
                
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
            
            # Atualizar sistema e páginas relacionadas
            self.stdout.write('Atualizando sistema e páginas...')
            SistemaAtualizacao.atualizar_sistema(
                f'Atualização da tabela ResumoCriminalidadeCidades.xlsx - '
                f'{cidades_criadas} novas cidades, {cidades_atualizadas} atualizadas'
            )
            PaginaAtualizacao.atualizar_pagina(
                'home',
                'Atualização dos dados de criminalidade das cidades'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nImportação concluída!\n'
                    f'   Total de registros no Excel: {len(df)}\n'
                    f'   Estados no banco: {total_estados}\n'
                    f'   Cidades no banco: {total_cidades}\n'
                    f'   Novas cidades criadas: {cidades_criadas}\n'
                    f'   Cidades atualizadas: {cidades_atualizadas}\n'
                    f'   Sistema e páginas atualizados com sucesso!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'ERRO: Erro ao importar dados: {str(e)}')
            )
