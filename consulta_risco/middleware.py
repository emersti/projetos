from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .maintenance_config import MAINTENANCE_MODE


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

















































