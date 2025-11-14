"""
Comando para importar coordenadas das cidades de um arquivo JSON
Útil para importar coordenadas exportadas do ambiente de desenvolvimento em produção
"""
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from consulta_risco.models import Cidade, Estado


class Command(BaseCommand):
    help = 'Importa coordenadas das cidades de um arquivo JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default='coordenadas_cidades.json',
            help='Nome do arquivo de entrada (padrão: coordenadas_cidades.json)'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Pular cidades que já têm coordenadas'
        )

    def handle(self, *args, **options):
        input_file = options['input']
        skip_existing = options['skip_existing']
        
        # Verificar se o arquivo existe
        input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), input_file)
        
        if not os.path.exists(input_path):
            self.stdout.write(
                self.style.ERROR(f'Arquivo nao encontrado: {input_path}')
            )
            self.stdout.write(
                self.style.WARNING(
                    'Dica: Use o comando "python manage.py exportar_coordenadas" '
                    'no ambiente de desenvolvimento para gerar o arquivo.'
                )
            )
            return
        
        # Ler arquivo JSON
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao ler arquivo JSON: {e}')
            )
            return
        
        total_registros = len(dados)
        self.stdout.write(f'Arquivo carregado: {total_registros} registros encontrados')
        
        # Processar importação
        atualizadas = 0
        criadas = 0
        puladas = 0
        erros = 0
        
        with transaction.atomic():
            for idx, registro in enumerate(dados, 1):
                try:
                    nome = registro.get('nome', '').strip()
                    estado_sigla = registro.get('estado_sigla', '').strip().upper()
                    latitude_str = registro.get('latitude', '').strip()
                    longitude_str = registro.get('longitude', '').strip()
                    
                    if not all([nome, estado_sigla, latitude_str, longitude_str]):
                        erros += 1
                        continue
                    
                    # Buscar estado
                    try:
                        estado = Estado.objects.get(sigla=estado_sigla)
                    except Estado.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Estado nao encontrado: {estado_sigla} (cidade: {nome})'
                            )
                        )
                        erros += 1
                        continue
                    
                    # Buscar cidade
                    try:
                        cidade = Cidade.objects.get(nome=nome, estado=estado)
                    except Cidade.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Cidade nao encontrada: {nome} - {estado_sigla}'
                            )
                        )
                        erros += 1
                        continue
                    
                    # Verificar se já tem coordenadas
                    if skip_existing and cidade.latitude is not None and cidade.longitude is not None:
                        puladas += 1
                        continue
                    
                    # Atualizar coordenadas
                    cidade.latitude = latitude_str
                    cidade.longitude = longitude_str
                    cidade.save(update_fields=['latitude', 'longitude'])
                    
                    atualizadas += 1
                    
                    if idx % 100 == 0:
                        self.stdout.write(f'Processadas {idx}/{total_registros} cidades...')
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Erro ao processar registro {idx}: {e}'
                        )
                    )
                    erros += 1
        
        # Resumo
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('RESUMO DA IMPORTACAO'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Coordenadas atualizadas: {atualizadas}'))
        if puladas > 0:
            self.stdout.write(self.style.WARNING(f'Cidades puladas (ja tinham coordenadas): {puladas}'))
        if erros > 0:
            self.stdout.write(self.style.ERROR(f'Erros: {erros}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

