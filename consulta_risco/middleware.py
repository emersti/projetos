from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .maintenance_config import MAINTENANCE_MODE
import logging

logger = logging.getLogger(__name__)


class MaintenanceMiddleware:
    """
    Middleware para controlar o modo de manutenção do site.
    Quando MAINTENANCE_MODE = True, redireciona todas as requisições
    para a página de manutenção, exceto a própria página de manutenção.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Se o modo de manutenção estiver ativo
        if MAINTENANCE_MODE:
            # Permite acesso à página de manutenção e APIs essenciais
            allowed_paths = [
                '/maintenance/',
                '/admin/',
                '/static/',
                '/favicon.ico',
            ]
            
            # Verifica se a requisição é para um caminho permitido
            if not any(request.path.startswith(path) for path in allowed_paths):
                # Redireciona para a página de manutenção
                return HttpResponseRedirect('/maintenance/')

        response = self.get_response(request)
        return response


class AcessoPaginaMiddleware:
    """
    Middleware para rastrear acessos às páginas do site.
    Registra apenas as páginas especificadas: home, cupons, lgpd, fale conosco, faq, termos de uso e sobre.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que DEVEM ser rastreadas (apenas estas páginas específicas)
        self.allowed_paths = [
            '/',  # home
            '/cupons/',
            '/lgpd/',
            '/faq/',
            '/termos-uso/',
            '/sobre/',
            '/mapa-seguranca/',  # mapa de segurança
            # Nota: Se existir página "fale conosco" ou "contato", adicionar aqui
            # Exemplo: '/fale-conosco/', '/contato/'
        ]
    
    def __call__(self, request):
        # Verificar se deve rastrear este acesso
        # Apenas registrar se for GET e se a URL estiver na lista permitida
        should_track = request.method == 'GET'
        should_track = should_track and request.path in self.allowed_paths
        
        if should_track:
            try:
                self._registrar_acesso(request)
            except Exception as e:
                # Não interromper o fluxo se houver erro no rastreamento
                logger.error('Erro ao registrar acesso: %s', str(e))
        
        response = self.get_response(request)
        return response
    
    def _registrar_acesso(self, request):
        """Registra o acesso à página"""
        from .models import AcessoPagina
        
        # Obter informações básicas
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        url = request.path
        nome_pagina = self._get_nome_pagina(url)
        
        # Tentar obter localização por IP (opcional, não bloqueia se falhar)
        cidade = ''
        estado = ''
        
        try:
            # Usar API gratuita para geolocalização (ip-api.com - sem autenticação)
            # Limite: 45 requisições por minuto
            # Em desenvolvimento, tenta mesmo com IPs locais (pode não funcionar)
            if ip_address:
                # Para desenvolvimento: tentar mesmo com IPs locais
                # Em produção, apenas IPs públicos serão geolocalizados
                try:
                    import requests
                    response = requests.get(
                        f'http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,query&lang=pt-BR',
                        timeout=2  # Aumentado para 2 segundos
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'success':
                            # Aceitar qualquer país, não apenas Brazil (para testes)
                            country = data.get('country', '')
                            if country == 'Brazil' or country == 'Brasil':
                                cidade = data.get('city', '')
                                estado_nome = data.get('regionName', '')
                                estado = self._converter_estado_para_sigla(estado_nome)
                                
                                # Log para debug (apenas em desenvolvimento)
                                if not cidade or not estado:
                                    logger.debug(f'Geolocalização parcial - IP: {ip_address}, Cidade: {cidade}, Estado: {estado_nome} -> {estado}')
                            else:
                                logger.debug(f'IP não é do Brasil - IP: {ip_address}, País: {country}')
                        else:
                            logger.debug(f'API retornou erro - IP: {ip_address}, Status: {data.get("status")}, Message: {data.get("message")}')
                except requests.exceptions.Timeout:
                    logger.debug(f'Timeout ao buscar geolocalização para IP: {ip_address}')
                except requests.exceptions.RequestException as e:
                    logger.debug(f'Erro na requisição de geolocalização - IP: {ip_address}, Erro: {str(e)}')
                except Exception as e:
                    logger.debug(f'Erro inesperado na geolocalização - IP: {ip_address}, Erro: {str(e)}')
            else:
                logger.debug('IP não disponível para geolocalização')
        except Exception as e:
            logger.debug(f'Erro geral na geolocalização: {str(e)}')
        
        # Registrar acesso (usar create com try/except para não bloquear)
        try:
            AcessoPagina.objects.create(
                url=url,
                nome_pagina=nome_pagina,
                ip_address=ip_address,
                cidade=cidade,
                estado=estado,
                user_agent=user_agent,
                referer=referer
            )
            # Log para debug
            if cidade and estado:
                logger.debug(f'Acesso registrado com localização - URL: {url}, Cidade: {cidade}, Estado: {estado}')
            else:
                logger.debug(f'Acesso registrado sem localização - URL: {url}, IP: {ip_address}')
        except Exception as e:
            # Log do erro mas não interrompe o fluxo
            logger.error('Erro ao registrar acesso: %s', str(e))
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_nome_pagina(self, url):
        """Retorna nome amigável da página baseado na URL"""
        nomes = {
            '/': 'Home',
            '/sobre/': 'Sobre',
            '/faq/': 'FAQ',
            '/lgpd/': 'LGPD',
            '/termos-uso/': 'Termos de Uso',
            '/cupons/': 'Cupons',
            '/mapa-seguranca/': 'Mapa de Segurança',
            '/fale-conosco/': 'Fale Conosco',
            '/contato/': 'Fale Conosco',
        }
        return nomes.get(url, url)
    
    def _converter_estado_para_sigla(self, estado_nome):
        """Converte nome do estado para sigla"""
        estados = {
            'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
            'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF',
            'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA',
            'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG',
            'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR', 'Pernambuco': 'PE',
            'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
            'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR',
            'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE',
            'Tocantins': 'TO'
        }
        return estados.get(estado_nome, estado_nome[:2].upper() if estado_nome else '')

















































