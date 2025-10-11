from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.simple_tag
def get_ultima_atualizacao():
    """Retorna a data atual como fallback"""
    try:
        # Tentar importar e usar o modelo
        from consulta_risco.models import SistemaAtualizacao
        data = SistemaAtualizacao.get_ultima_atualizacao()
        
        # Converter explicitamente para fuso horário de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if timezone.is_aware(data):
            # Se a data é timezone-aware, converter para Brasília
            data_brasilia = data.astimezone(brasilia_tz)
        else:
            # Se não é timezone-aware, assumir UTC e converter
            utc_tz = pytz.timezone('UTC')
            data_utc = utc_tz.localize(data)
            data_brasilia = data_utc.astimezone(brasilia_tz)
        
        return data_brasilia.strftime('%d/%m/%Y às %H:%M')
    except Exception:
        # Fallback para data atual no fuso de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        agora_brasilia = timezone.now().astimezone(brasilia_tz)
        return agora_brasilia.strftime('%d/%m/%Y às %H:%M')

@register.simple_tag
def get_ultima_atualizacao_pagina(nome_pagina):
    """Retorna a data de última atualização de uma página específica"""
    try:
        from consulta_risco.models import PaginaAtualizacao
        data = PaginaAtualizacao.get_ultima_atualizacao(nome_pagina)
        
        # Converter explicitamente para fuso horário de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if timezone.is_aware(data):
            data_brasilia = data.astimezone(brasilia_tz)
        else:
            utc_tz = pytz.timezone('UTC')
            data_utc = utc_tz.localize(data)
            data_brasilia = data_utc.astimezone(brasilia_tz)
        
        return data_brasilia.strftime('%d de %B de %Y').replace('January', 'janeiro').replace('February', 'fevereiro').replace('March', 'março').replace('April', 'abril').replace('May', 'maio').replace('June', 'junho').replace('July', 'julho').replace('August', 'agosto').replace('September', 'setembro').replace('October', 'outubro').replace('November', 'novembro').replace('December', 'dezembro')
    except Exception:
        # Fallback para data atual no fuso de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        agora_brasilia = timezone.now().astimezone(brasilia_tz)
        return agora_brasilia.strftime('%d de %B de %Y').replace('January', 'janeiro').replace('February', 'fevereiro').replace('March', 'março').replace('April', 'abril').replace('May', 'maio').replace('June', 'junho').replace('July', 'julho').replace('August', 'agosto').replace('September', 'setembro').replace('October', 'outubro').replace('November', 'novembro').replace('December', 'dezembro')
