from django.core.management.base import BaseCommand
from consulta_risco.models import TipoCupom


class Command(BaseCommand):
    help = 'Popula os tipos de cupom com cores predefinidas'

    def handle(self, *args, **options):
        tipos_cupom = [
            {
                'nome': 'Desconto',
                'cor_fundo': '#28a745',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons de desconto geral',
                'ordem_exibicao': 1
            },
            {
                'nome': 'Frete Grátis',
                'cor_fundo': '#17a2b8',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons para frete grátis',
                'ordem_exibicao': 2
            },
            {
                'nome': 'Cashback',
                'cor_fundo': '#ffc107',
                'cor_texto': '#000000',
                'descricao': 'Cupons de cashback',
                'ordem_exibicao': 3
            },
            {
                'nome': 'Primeira Compra',
                'cor_fundo': '#6f42c1',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons para primeira compra',
                'ordem_exibicao': 4
            },
            {
                'nome': 'Black Friday',
                'cor_fundo': '#dc3545',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons especiais de Black Friday',
                'ordem_exibicao': 5
            },
            {
                'nome': 'Natal',
                'cor_fundo': '#e83e8c',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons de Natal',
                'ordem_exibicao': 6
            },
            {
                'nome': 'Dia das Mães',
                'cor_fundo': '#fd7e14',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons para Dia das Mães',
                'ordem_exibicao': 7
            },
            {
                'nome': 'Dia dos Pais',
                'cor_fundo': '#20c997',
                'cor_texto': '#ffffff',
                'descricao': 'Cupons para Dia dos Pais',
                'ordem_exibicao': 8
            }
        ]

        for tipo_data in tipos_cupom:
            tipo, created = TipoCupom.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de cupom "{tipo.nome}" criado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tipo de cupom "{tipo.nome}" já existe.')
                )

        self.stdout.write(
            self.style.SUCCESS('Processo de popular tipos de cupom concluído!')
        )

































