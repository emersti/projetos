from django.utils import timezone
from django.utils.dateformat import format

def ultima_atualizacao(request):
    """Context processor para adicionar data de última atualização em todos os templates"""
    try:
        from consulta_risco.models import SistemaAtualizacao
        data = SistemaAtualizacao.get_ultima_atualizacao()
        
        # Usar template filter para conversão de timezone
        # O Django automaticamente converte para o TIME_ZONE configurado
        return {
            'ultima_atualizacao': format(data, 'd/m/Y \à\s H:i')
        }
    except Exception as e:
        # Em caso de erro, usar data atual
        agora = timezone.now()
        return {
            'ultima_atualizacao': format(agora, 'd/m/Y \à\s H:i')
        }








