from django.core.management.base import BaseCommand
from consulta_risco.models import Estado, Cidade


class Command(BaseCommand):
    help = 'Popula o banco de dados com estados e cidades brasileiras'

    def handle(self, *args, **options):
        # Dados dos estados brasileiros
        estados_data = [
            {'nome': 'Acre', 'sigla': 'AC'},
            {'nome': 'Alagoas', 'sigla': 'AL'},
            {'nome': 'Amapá', 'sigla': 'AP'},
            {'nome': 'Amazonas', 'sigla': 'AM'},
            {'nome': 'Bahia', 'sigla': 'BA'},
            {'nome': 'Ceará', 'sigla': 'CE'},
            {'nome': 'Distrito Federal', 'sigla': 'DF'},
            {'nome': 'Espírito Santo', 'sigla': 'ES'},
            {'nome': 'Goiás', 'sigla': 'GO'},
            {'nome': 'Maranhão', 'sigla': 'MA'},
            {'nome': 'Mato Grosso', 'sigla': 'MT'},
            {'nome': 'Mato Grosso do Sul', 'sigla': 'MS'},
            {'nome': 'Minas Gerais', 'sigla': 'MG'},
            {'nome': 'Pará', 'sigla': 'PA'},
            {'nome': 'Paraíba', 'sigla': 'PB'},
            {'nome': 'Paraná', 'sigla': 'PR'},
            {'nome': 'Pernambuco', 'sigla': 'PE'},
            {'nome': 'Piauí', 'sigla': 'PI'},
            {'nome': 'Rio de Janeiro', 'sigla': 'RJ'},
            {'nome': 'Rio Grande do Norte', 'sigla': 'RN'},
            {'nome': 'Rio Grande do Sul', 'sigla': 'RS'},
            {'nome': 'Rondônia', 'sigla': 'RO'},
            {'nome': 'Roraima', 'sigla': 'RR'},
            {'nome': 'Santa Catarina', 'sigla': 'SC'},
            {'nome': 'São Paulo', 'sigla': 'SP'},
            {'nome': 'Sergipe', 'sigla': 'SE'},
            {'nome': 'Tocantins', 'sigla': 'TO'},
        ]

        # Dados das principais cidades por estado
        cidades_data = {
            'AC': ['Rio Branco', 'Cruzeiro do Sul', 'Sena Madureira', 'Tarauacá', 'Feijó'],
            'AL': ['Maceió', 'Arapiraca', 'Rio Largo', 'Palmeira dos Índios', 'União dos Palmares'],
            'AP': ['Macapá', 'Santana', 'Laranjal do Jari', 'Oiapoque', 'Porto Grande'],
            'AM': ['Manaus', 'Parintins', 'Itacoatiara', 'Manacapuru', 'Coari'],
            'BA': ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari', 'Juazeiro'],
            'CE': ['Fortaleza', 'Caucaia', 'Juazeiro do Norte', 'Maracanaú', 'Sobral'],
            'DF': ['Brasília', 'Gama', 'Taguatinga', 'Ceilândia', 'Sobradinho'],
            'ES': ['Vitória', 'Vila Velha', 'Cariacica', 'Serra', 'Cachoeiro de Itapemirim'],
            'GO': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis', 'Rio Verde', 'Luziânia'],
            'MA': ['São Luís', 'Imperatriz', 'São José de Ribamar', 'Timon', 'Caxias'],
            'MT': ['Cuiabá', 'Várzea Grande', 'Rondonópolis', 'Sinop', 'Tangará da Serra'],
            'MS': ['Campo Grande', 'Dourados', 'Três Lagoas', 'Corumbá', 'Ponta Porã'],
            'MG': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim'],
            'PA': ['Belém', 'Ananindeua', 'Santarém', 'Marabá', 'Parauapebas'],
            'PB': ['João Pessoa', 'Campina Grande', 'Santa Rita', 'Patos', 'Bayeux'],
            'PR': ['Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel'],
            'PE': ['Recife', 'Jaboatão dos Guararapes', 'Olinda', 'Caruaru', 'Petrolina'],
            'PI': ['Teresina', 'Parnaíba', 'Picos', 'Piripiri', 'Floriano'],
            'RJ': ['Rio de Janeiro', 'São Gonçalo', 'Duque de Caxias', 'Nova Iguaçu', 'Niterói'],
            'RN': ['Natal', 'Mossoró', 'Parnamirim', 'São Gonçalo do Amarante', 'Macaíba'],
            'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Canoas', 'Santa Maria'],
            'RO': ['Porto Velho', 'Ji-Paraná', 'Ariquemes', 'Vilhena', 'Cacoal'],
            'RR': ['Boa Vista', 'Rorainópolis', 'Caracaraí', 'Alto Alegre', 'Mucajaí'],
            'SC': ['Florianópolis', 'Joinville', 'Blumenau', 'São José', 'Criciúma'],
            'SP': ['São Paulo', 'Guarulhos', 'Campinas', 'São Bernardo do Campo', 'Santo André'],
            'SE': ['Aracaju', 'Nossa Senhora do Socorro', 'Lagarto', 'Itabaiana', 'São Cristóvão'],
            'TO': ['Palmas', 'Araguaína', 'Gurupi', 'Porto Nacional', 'Paraíso do Tocantins'],
        }

        # Criar estados
        self.stdout.write('Criando estados...')
        for estado_info in estados_data:
            estado, created = Estado.objects.get_or_create(
                sigla=estado_info['sigla'],
                defaults={'nome': estado_info['nome']}
            )
            if created:
                self.stdout.write(f'  ✓ Estado criado: {estado.nome} ({estado.sigla})')
            else:
                self.stdout.write(f'  - Estado já existe: {estado.nome} ({estado.sigla})')

        # Criar cidades
        self.stdout.write('\nCriando cidades...')
        total_cidades = 0
        for sigla, cidades in cidades_data.items():
            try:
                estado = Estado.objects.get(sigla=sigla)
                for cidade_nome in cidades:
                    cidade, created = Cidade.objects.get_or_create(
                        nome=cidade_nome,
                        estado=estado
                    )
                    if created:
                        total_cidades += 1
                        self.stdout.write(f'  ✓ Cidade criada: {cidade.nome} - {estado.sigla}')
            except Estado.DoesNotExist:
                self.stdout.write(f'  ✗ Estado não encontrado: {sigla}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ População do banco concluída!\n'
                f'   - {Estado.objects.count()} estados\n'
                f'   - {Cidade.objects.count()} cidades\n'
                f'   - {total_cidades} novas cidades adicionadas'
            )
        )









































