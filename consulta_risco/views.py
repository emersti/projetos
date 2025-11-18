from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.timezone import localtime
from django.db import transaction
from django.db.models import Q
import hashlib
import json
import secrets
import string
import os
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import unicodedata
from .models import Estado, Cidade, Cupom, AdminUser, TipoCupom, AvaliacaoSeguranca, SistemaAtualizacao


def formatar_data_brasil(datetime_obj):
    """
    Formata uma data/hora para o timezone brasileiro (Brasília)
    """
    if datetime_obj is None:
        return None
    
    # Se a data não tem timezone (naive), assumir que já é UTC-3
    if datetime_obj.tzinfo is None:
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    
    # Se tem timezone, converter para timezone local (Brasília)
    data_local = localtime(datetime_obj)
    return data_local.strftime('%d/%m/%Y %H:%M')


def reordenar_cupons(cupom_atualizado, nova_ordem, cupom_id=None):
    """
    Reordena automaticamente os cupons quando a ordem de um cupom é alterada.
    
    Args:
        cupom_atualizado: Instância do cupom sendo editado (None se for novo)
        nova_ordem: Nova ordem de exibição
        cupom_id: ID do cupom sendo editado (None se for novo)
    """
    # Obter todos os cupons ordenados por ordem_exibicao
    cupons = list(Cupom.objects.all().order_by('ordem_exibicao', 'id'))
    
    # Remover o cupom sendo editado da lista original (se existir)
    if cupom_id is not None:
        cupons = [c for c in cupons if c.id != cupom_id]
    
    # Inserir o cupom na posição correta
    posicao_inserir = min(nova_ordem - 1, len(cupons))
    cupons.insert(posicao_inserir, cupom_atualizado)
    
    # Reordenar todos os cupons com ordem sequencial
    for index, cupom in enumerate(cupons, 1):
        if cupom.ordem_exibicao != index:
            cupom.ordem_exibicao = index
            cupom.save(update_fields=['ordem_exibicao'])


def home(request):
    """View principal do site"""
    estados = Estado.objects.all().order_by('nome')
    return render(request, 'consulta_risco/home.html', {'estados': estados})


def sobre(request):
    """View para página sobre a empresa"""
    return render(request, 'consulta_risco/sobre.html')


def faq(request):
    """View para página FAQ"""
    return render(request, 'consulta_risco/faq.html')


def lgpd(request):
    """View para página LGPD"""
    return render(request, 'consulta_risco/lgpd.html')


def termos_uso(request):
    """View para página de Termos de Uso"""
    return render(request, 'consulta_risco/termos_uso.html')


def maintenance(request):
    """View para página de manutenção"""
    return render(request, 'consulta_risco/maintenance.html')


def cupons(request):
    """View para página de cupons"""
    # Obter todos os cupons ativos
    cupons = Cupom.objects.select_related('tipo_cupom').filter(ativo=True).order_by('ordem_exibicao', 'data_criacao')
    
    # Filtrar apenas cupons válidos baseado nas datas
    cupons_validos = []
    agora = timezone.now()
    
    for cupom in cupons:
        # Verificar se o cupom está válido usando o método do modelo
        if cupom.esta_valido():
            cupons_validos.append(cupom)
    
    # Filtro por loja
    loja_pesquisa = request.GET.get('loja', '').strip()
    if loja_pesquisa:
        cupons_validos = [c for c in cupons_validos if loja_pesquisa.lower() in c.loja.lower()]
    
    return render(request, 'consulta_risco/cupons.html', {
        'cupons': cupons_validos,
        'loja_pesquisa': loja_pesquisa
    })


def get_cidades(request):
    """API para buscar cidades de um estado específico"""
    estado_id = request.GET.get('estado_id')
    if estado_id:
        cidades = Cidade.objects.filter(estado_id=estado_id).order_by('nome')
        data = [{'id': cidade.id, 'nome': cidade.nome, 'posicao': cidade.posicao} for cidade in cidades]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


@csrf_exempt
@require_POST
def avaliar_seguranca(request):
    """View para processar avaliação de segurança de uma cidade"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        estado_id = data.get('estado_id')
        cidade_nome = data.get('cidade', '').strip()
        nota = data.get('nota')
        
        # Validações
        if not email:
            return JsonResponse({'success': False, 'error': 'Email é obrigatório'})
        
        if not estado_id:
            return JsonResponse({'success': False, 'error': 'Estado é obrigatório'})
        
        if not cidade_nome:
            return JsonResponse({'success': False, 'error': 'Cidade é obrigatória'})
        
        if not nota or not isinstance(nota, int) or nota < 1 or nota > 10:
            return JsonResponse({'success': False, 'error': 'Nota deve ser um número entre 1 e 10'})
        
        # Buscar o estado
        try:
            estado = Estado.objects.get(id=estado_id)
        except Estado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Estado não encontrado'})
        
        # Usar get_or_create para atualizar se já existir
        avaliacao, created = AvaliacaoSeguranca.objects.get_or_create(
            email=email,
            estado=estado,
            cidade=cidade_nome,
            defaults={'nota': nota}
        )
        
        if not created:
            # Se já existe, atualizar a nota e a data de avaliação
            avaliacao.nota = nota
            # Usar função do modelo para garantir UTC-3
            from .models import get_brasilia_time
            avaliacao.data_avaliacao = get_brasilia_time()
            avaliacao.save()
        
        # Invalidar cache da média de avaliações para esta cidade (se cache estiver disponível)
        try:
            from django.core.cache import cache
            cache_key = f'avaliacao_media_{estado_id}_{cidade_nome.lower()}'
            cache.delete(cache_key)
        except Exception:
            # Se o cache não estiver disponível, continuar sem invalidar
            pass
        
        # Atualizar data do sistema
        SistemaAtualizacao.atualizar_sistema(f"Avaliação de segurança para {cidade_nome} recebida")
        
        # Mensagem personalizada baseada se foi criada ou atualizada
        if created:
            message = 'Avaliação salva com sucesso!'
        else:
            message = 'Avaliação atualizada com sucesso!'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'created': created,
            'nota': avaliacao.nota,
            'data_avaliacao': formatar_data_brasil(avaliacao.data_avaliacao),
            'timezone': 'America/Sao_Paulo'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})

@csrf_exempt
def obter_media_avaliacoes(request):
    """View para obter a média das avaliações de uma cidade (últimos 3 anos)"""
    try:
        estado_id = request.GET.get('estado_id')
        cidade_nome = request.GET.get('cidade', '').strip()
        
        if not estado_id or not cidade_nome:
            return JsonResponse({'success': False, 'error': 'Estado e cidade são obrigatórios'})
        
        # Tentar obter do cache (se disponível)
        cached_result = None
        try:
            from django.core.cache import cache
            cache_key = f'avaliacao_media_{estado_id}_{cidade_nome.lower()}'
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return JsonResponse(cached_result)
        except Exception:
            # Se o cache não estiver disponível, continuar sem cache
            pass
        
        # Buscar o estado
        try:
            estado = Estado.objects.get(id=estado_id)
        except Estado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Estado não encontrado'})
        
        # Calcular data limite (ano corrente - 2 anos = últimos 3 anos)
        from datetime import datetime, timedelta
        from .models import get_brasilia_time
        import pytz
        
        # Obter data atual em Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = datetime.now(brasilia_tz)
        
        # Data limite: 1º de janeiro do ano há 2 anos atrás
        ano_limite = data_atual.year - 2
        data_limite = datetime(ano_limite, 1, 1, tzinfo=brasilia_tz)
        # Remover timezone para comparar com campo que não tem timezone
        data_limite = data_limite.replace(tzinfo=None)
        
        # Buscar avaliações da cidade dos últimos 3 anos (usando índice para otimizar)
        avaliacoes = AvaliacaoSeguranca.objects.filter(
            estado=estado,
            cidade__iexact=cidade_nome,
            data_avaliacao__gte=data_limite
        ).only('nota')  # Selecionar apenas o campo necessário para otimizar
        
        if avaliacoes.exists():
            # Calcular média usando aggregate (mais eficiente)
            from django.db.models import Avg, Count
            resultado = avaliacoes.aggregate(
                media=Avg('nota'),
                quantidade=Count('id')
            )
            
            media = resultado['media']
            quantidade = resultado['quantidade']
            
            response_data = {
                'success': True,
                'tem_avaliacoes': True,
                'media': round(media, 2),
                'quantidade': quantidade
            }
            
            # Armazenar no cache por 1 hora (se cache estiver disponível)
            try:
                from django.core.cache import cache
                cache_key = f'avaliacao_media_{estado_id}_{cidade_nome.lower()}'
                cache.set(cache_key, response_data, 3600)
            except Exception:
                # Se o cache não estiver disponível, continuar sem cache
                pass
            
            return JsonResponse(response_data)
        else:
            response_data = {
                'success': True,
                'tem_avaliacoes': False
            }
            
            # Armazenar no cache por 1 hora mesmo quando não há avaliações (se cache estiver disponível)
            try:
                from django.core.cache import cache
                cache_key = f'avaliacao_media_{estado_id}_{cidade_nome.lower()}'
                cache.set(cache_key, response_data, 3600)
            except Exception:
                # Se o cache não estiver disponível, continuar sem cache
                pass
            
            return JsonResponse(response_data)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


# Sistema de Autenticação Simples
def hash_password(password):
    """Função simples para hash de senha"""
    return hashlib.sha256(password.encode()).hexdigest()


def admin_login(request):
    """View para login do administrador"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            admin_user = AdminUser.objects.get(username=username, ativo=True)
            if admin_user.password == hash_password(password):
                # Login bem-sucedido
                admin_user.ultimo_login = timezone.now()
                admin_user.save()
                
                # Armazenar sessão simples
                request.session['admin_logged_in'] = True
                request.session['admin_user_id'] = admin_user.id
                request.session['admin_username'] = admin_user.username
                request.session['admin_nivel'] = admin_user.nivel_acesso
                
                messages.success(request, f'Bem-vindo, {admin_user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Senha incorreta.')
        except AdminUser.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
    
    return render(request, 'consulta_risco/admin_login.html')


def admin_logout(request):
    """View para logout do administrador"""
    request.session.flush()
    messages.info(request, 'Você foi desconectado.')
    return redirect('admin_login')


def admin_required(view_func):
    """Decorator para verificar se o usuário está logado como admin"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            messages.error(request, 'Você precisa fazer login para acessar esta página.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Dashboard do administrador"""
    cupons = Cupom.objects.select_related('criado_por', 'modificado_por', 'tipo_cupom').all().order_by('ordem_exibicao', 'data_criacao')
    
    # Filtro por loja
    loja_pesquisa = request.GET.get('loja', '').strip()
    if loja_pesquisa:
        cupons = cupons.filter(loja__icontains=loja_pesquisa)
    
    # Obter informações do usuário atual
    admin_user_id = request.session.get('admin_user_id')
    try:
        admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    except AdminUser.DoesNotExist:
        admin_user = None
    
    return render(request, 'consulta_risco/admin_dashboard.html', {
        'cupons': cupons,
        'admin_user': admin_user,
        'loja_pesquisa': loja_pesquisa
    })


@admin_required
def admin_cupom_edit(request, cupom_id=None):
    """View para editar ou criar cupom"""
    from .models import TipoCupom
    
    cupom = None
    if cupom_id:
        cupom = get_object_or_404(Cupom, id=cupom_id)
    
    if request.method == 'POST':
        try:
            # Obter o usuário admin logado
            admin_user = None
            admin_user_id = request.session.get('admin_user_id')
            if admin_user_id:
                try:
                    admin_user = AdminUser.objects.get(id=admin_user_id)
                except AdminUser.DoesNotExist:
                    admin_user = None
            
            
            if cupom:
                # Editar cupom existente
                ordem_anterior = cupom.ordem_exibicao
                nova_ordem = int(request.POST.get('ordem_exibicao', 1))
                loja_nome = request.POST.get('loja', '').strip()
                
                # Buscar o TipoCupom correspondente à loja selecionada
                tipo_cupom = None
                if loja_nome:
                    try:
                        tipo_cupom = TipoCupom.objects.get(nome=loja_nome)
                    except TipoCupom.DoesNotExist:
                        pass
                
                cupom.loja = loja_nome
                cupom.tipo_cupom = tipo_cupom
                cupom.titulo = request.POST.get('titulo', '').strip()
                cupom.descricao = request.POST.get('descricao', '').strip()
                cupom.codigo = request.POST.get('codigo', '').strip()
                cupom.link_acesso = request.POST.get('link_acesso', '').strip()
                cupom.ativo = request.POST.get('ativo') == 'on'
                
                # Processar campos de data
                data_inicio_str = request.POST.get('data_inicio', '').strip()
                data_validade_str = request.POST.get('data_validade', '').strip()
                
                if data_inicio_str:
                    try:
                        cupom.data_inicio = timezone.datetime.fromisoformat(data_inicio_str)
                    except ValueError:
                        messages.error(request, 'Formato de data de início inválido')
                        return render(request, 'consulta_risco/admin_cupom_edit.html', {
                            'cupom': cupom,
                            'lojas': TipoCupom.objects.filter(ativo=True).order_by('ordem_exibicao', 'nome'),
                            'admin_user': admin_user
                        })
                else:
                    cupom.data_inicio = None
                
                if data_validade_str:
                    try:
                        cupom.data_validade = timezone.datetime.fromisoformat(data_validade_str)
                    except ValueError:
                        messages.error(request, 'Formato de data de validade inválido')
                        return render(request, 'consulta_risco/admin_cupom_edit.html', {
                            'cupom': cupom,
                            'lojas': TipoCupom.objects.filter(ativo=True).order_by('ordem_exibicao', 'nome'),
                            'admin_user': admin_user
                        })
                else:
                    cupom.data_validade = None
                
                cupom.modificado_por = admin_user
                cupom.save()
                
                # Reordenar cupons se a ordem foi alterada
                if ordem_anterior != nova_ordem:
                    reordenar_cupons(cupom, nova_ordem, cupom.id)
                
                # Atualizar data do sistema
                SistemaAtualizacao.atualizar_sistema(f"Cupom '{cupom.titulo}' atualizado")
                
                messages.success(request, 'Cupom atualizado com sucesso!')
            else:
                # Criar novo cupom
                nova_ordem = int(request.POST.get('ordem_exibicao', 1))
                loja_nome = request.POST.get('loja', '').strip()
                
                # Buscar o TipoCupom correspondente à loja selecionada
                tipo_cupom = None
                if loja_nome:
                    try:
                        tipo_cupom = TipoCupom.objects.get(nome=loja_nome)
                    except TipoCupom.DoesNotExist:
                        pass
                
                # Processar campos de data para novo cupom
                data_inicio_str = request.POST.get('data_inicio', '').strip()
                data_validade_str = request.POST.get('data_validade', '').strip()
                
                data_inicio = None
                data_validade = None
                
                if data_inicio_str:
                    try:
                        data_inicio = timezone.datetime.fromisoformat(data_inicio_str)
                    except ValueError:
                        messages.error(request, 'Formato de data de início inválido')
                        return render(request, 'consulta_risco/admin_cupom_edit.html', {
                            'cupom': None,
                            'lojas': TipoCupom.objects.filter(ativo=True).order_by('ordem_exibicao', 'nome'),
                            'admin_user': admin_user
                        })
                
                if data_validade_str:
                    try:
                        data_validade = timezone.datetime.fromisoformat(data_validade_str)
                    except ValueError:
                        messages.error(request, 'Formato de data de validade inválido')
                        return render(request, 'consulta_risco/admin_cupom_edit.html', {
                            'cupom': None,
                            'lojas': TipoCupom.objects.filter(ativo=True).order_by('ordem_exibicao', 'nome'),
                            'admin_user': admin_user
                        })
                
                cupom = Cupom.objects.create(
                    loja=loja_nome,
                    tipo_cupom=tipo_cupom,
                    titulo=request.POST.get('titulo', '').strip(),
                    descricao=request.POST.get('descricao', '').strip(),
                    codigo=request.POST.get('codigo', '').strip(),
                    link_acesso=request.POST.get('link_acesso', '').strip(),
                    ativo=request.POST.get('ativo') == 'on',
                    data_inicio=data_inicio,
                    data_validade=data_validade,
                    ordem_exibicao=nova_ordem,
                    criado_por=admin_user,
                    modificado_por=admin_user
                )
                
                # Reordenar cupons para o novo cupom
                reordenar_cupons(cupom, nova_ordem, None)
                
                # Atualizar data do sistema
                SistemaAtualizacao.atualizar_sistema(f"Novo cupom '{cupom.titulo}' criado")
                
                messages.success(request, 'Cupom criado com sucesso!')
            
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Erro ao salvar cupom: {str(e)}')
    
    # Obter usuário admin para contexto
    admin_user_id = request.session.get('admin_user_id')
    try:
        admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    except AdminUser.DoesNotExist:
        admin_user = None

    # Obter todas as lojas cadastradas
    lojas = TipoCupom.objects.filter(ativo=True).order_by('ordem_exibicao', 'nome')

    return render(request, 'consulta_risco/admin_cupom_edit.html', {
        'cupom': cupom,
        'lojas': lojas,
        'admin_user': admin_user
    })


@admin_required
@csrf_exempt
@require_POST
def criar_loja_ajax(request):
    """View para criar nova loja via AJAX"""
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        cor_fundo = data.get('cor_fundo', '#ff6b35')
        cor_texto = data.get('cor_texto', '#ffffff')
        descricao = data.get('descricao', '').strip()
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome da loja é obrigatório'})
        
        # Verificar se já existe uma loja com esse nome
        if TipoCupom.objects.filter(nome=nome).exists():
            return JsonResponse({'success': False, 'error': 'Já existe uma loja com esse nome'})
        
        # Criar nova loja
        loja = TipoCupom.objects.create(
            nome=nome,
            cor_fundo=cor_fundo,
            cor_texto=cor_texto,
            descricao=descricao
        )
        
        return JsonResponse({
            'success': True,
            'loja': {
                'id': loja.id,
                'nome': loja.nome,
                'cor_fundo': loja.cor_fundo,
                'cor_texto': loja.cor_texto
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@admin_required
def admin_lojas_list(request):
    """Lista de lojas cadastradas"""
    admin_user_id = request.session.get('admin_user_id')
    try:
        admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    except AdminUser.DoesNotExist:
        admin_user = None

    lojas = TipoCupom.objects.all().order_by('ordem_exibicao', 'nome')
    
    # Filtro por nome da loja
    loja_pesquisa = request.GET.get('loja', '').strip()
    if loja_pesquisa:
        lojas = lojas.filter(nome__icontains=loja_pesquisa)

    return render(request, 'consulta_risco/admin_lojas_list.html', {
        'lojas': lojas,
        'admin_user': admin_user,
        'loja_pesquisa': loja_pesquisa
    })


@admin_required
def admin_loja_edit(request, loja_id=None):
    """View para editar ou criar loja"""
    from .models import TipoCupom
    
    loja = None
    if loja_id:
        loja = get_object_or_404(TipoCupom, id=loja_id)
    
    if request.method == 'POST':
        try:
            # Obter o usuário admin logado
            admin_user = None
            admin_user_id = request.session.get('admin_user_id')
            if admin_user_id:
                try:
                    admin_user = AdminUser.objects.get(id=admin_user_id)
                except AdminUser.DoesNotExist:
                    admin_user = None
            
            if loja:
                # Editar loja existente
                loja.nome = request.POST.get('nome', '').strip()
                loja.cor_fundo = request.POST.get('cor_fundo', '#ff6b35').strip()
                loja.cor_texto = request.POST.get('cor_texto', '#ffffff').strip()
                loja.descricao = request.POST.get('descricao', '').strip()
                loja.ativo = request.POST.get('ativo') == 'on'
                loja.ordem_exibicao = int(request.POST.get('ordem_exibicao', 1))
                loja.save()
                messages.success(request, 'Loja atualizada com sucesso!')
            else:
                # Criar nova loja
                loja = TipoCupom.objects.create(
                    nome=request.POST.get('nome', '').strip(),
                    cor_fundo=request.POST.get('cor_fundo', '#ff6b35').strip(),
                    cor_texto=request.POST.get('cor_texto', '#ffffff').strip(),
                    descricao=request.POST.get('descricao', '').strip(),
                    ativo=request.POST.get('ativo') == 'on',
                    ordem_exibicao=int(request.POST.get('ordem_exibicao', 1))
                )
                messages.success(request, 'Loja criada com sucesso!')
            
            return redirect('admin_lojas_list')
        except Exception as e:
            messages.error(request, f'Erro ao salvar loja: {str(e)}')
    
    # Obter usuário admin para contexto
    admin_user_id = request.session.get('admin_user_id')
    try:
        admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    except AdminUser.DoesNotExist:
        admin_user = None

    return render(request, 'consulta_risco/admin_loja_edit.html', {
        'loja': loja,
        'admin_user': admin_user
    })


@admin_required
def admin_cupom_delete(request, cupom_id):
    """View para deletar cupom"""
    cupom = get_object_or_404(Cupom, id=cupom_id)
    if request.method == 'POST':
        cupom.delete()
        messages.success(request, 'Cupom deletado com sucesso!')
        return redirect('admin_dashboard')
    
    return render(request, 'consulta_risco/admin_cupom_delete.html', {'cupom': cupom})


@admin_required
def admin_loja_delete(request, loja_id):
    """View para deletar loja"""
    loja = get_object_or_404(TipoCupom, id=loja_id)
    
    # Verificar se a loja tem cupons associados
    cupons_count = loja.cupom_set.count()
    if cupons_count > 0:
        messages.error(request, f'Não é possível excluir a loja "{loja.nome}" pois ela possui {cupons_count} cupom(ns) associado(s).')
        return redirect('admin_lojas_list')
    
    if request.method == 'POST':
        loja_nome = loja.nome
        loja.delete()
        messages.success(request, f'Loja "{loja_nome}" deletada com sucesso!')
        return redirect('admin_lojas_list')
    
    # Obter usuário admin para contexto
    admin_user_id = request.session.get('admin_user_id')
    try:
        admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    except AdminUser.DoesNotExist:
        admin_user = None

    return render(request, 'consulta_risco/admin_loja_delete.html', {
        'loja': loja,
        'admin_user': admin_user
    })


def admin_forgot_password(request):
    """View para solicitar reset de senha"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        if not username:
            messages.error(request, 'Por favor, digite seu nome de usuário.')
            return render(request, 'consulta_risco/admin_forgot_password.html')
        
        try:
            admin_user = AdminUser.objects.get(username=username, ativo=True)
            
            # Gerar token de reset
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            admin_user.reset_token = token
            admin_user.reset_token_expires = timezone.now() + timezone.timedelta(hours=24)
            admin_user.save()
            
            # Em um ambiente real, aqui você enviaria um email com o token
            # Para desenvolvimento, vamos mostrar o token na tela
            messages.success(request, f'Token de reset gerado para {username}. Em produção, este seria enviado por email.')
            messages.info(request, f'Token de desenvolvimento: {token}')
            
            return redirect('admin_reset_password', token=token)
            
        except AdminUser.DoesNotExist:
            messages.error(request, 'Usuário não encontrado ou inativo.')
    
    return render(request, 'consulta_risco/admin_forgot_password.html')


def admin_reset_password(request, token):
    """View para redefinir senha com token"""
    try:
        admin_user = AdminUser.objects.get(reset_token=token, ativo=True)
        
        # Verificar se o token não expirou
        if admin_user.reset_token_expires and admin_user.reset_token_expires < timezone.now():
            messages.error(request, 'Token expirado. Solicite um novo reset de senha.')
            return redirect('admin_forgot_password')
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            
            if not new_password:
                messages.error(request, 'Por favor, digite uma nova senha.')
            elif len(new_password) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            elif new_password != confirm_password:
                messages.error(request, 'As senhas não coincidem.')
            else:
                # Atualizar senha
                admin_user.password = hashlib.sha256(new_password.encode()).hexdigest()
                admin_user.reset_token = None
                admin_user.reset_token_expires = None
                admin_user.save()
                
                messages.success(request, 'Senha redefinida com sucesso! Você pode fazer login agora.')
                return redirect('admin_login')
        
        return render(request, 'consulta_risco/admin_reset_password.html', {
            'token': token,
            'username': admin_user.username
        })
        
    except AdminUser.DoesNotExist:
        messages.error(request, 'Token inválido ou expirado.')
        return redirect('admin_forgot_password')


@csrf_exempt
def create_default_admin(request):
    """View para criar usuário admin padrão (apenas para desenvolvimento)"""
    if request.method == 'POST':
        username = request.POST.get('username', 'admin')
        password = request.POST.get('password', 'admin123')
        
        # Verificar se já existe
        if AdminUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Usuário já existe'}, status=400)
        
        # Criar usuário admin
        admin_user = AdminUser.objects.create(
            username=username,
            password=hash_password(password),
            email='admin@example.com'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Usuário admin criado: {username}',
            'user_id': admin_user.id
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


# Views para gerenciamento de usuários administrativos
@admin_required
def admin_users_list(request):
    """Lista de usuários administrativos"""
    admin_user_id = request.session.get('admin_user_id')
    admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    
    if not admin_user or not admin_user.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para gerenciar usuários.')
        return redirect('admin_dashboard')
    
    usuarios = AdminUser.objects.all().order_by('-data_criacao')
    return render(request, 'consulta_risco/admin_users_list.html', {
        'usuarios': usuarios,
        'admin_user': admin_user
    })


@admin_required
def admin_user_create(request):
    """Criar novo usuário administrativo"""
    admin_user_id = request.session.get('admin_user_id')
    admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    
    if not admin_user or not admin_user.pode_criar_usuarios():
        messages.error(request, 'Você não tem permissão para criar usuários.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email', '')
            nivel_acesso = request.POST.get('nivel_acesso')
            
            # Verificar se usuário já existe
            if AdminUser.objects.filter(username=username).exists():
                messages.error(request, 'Nome de usuário já existe.')
                return render(request, 'consulta_risco/admin_user_create.html', {'admin_user': admin_user})
            
            # Verificar permissões para criar super admin
            if nivel_acesso == 'super_admin' and not admin_user.pode_editar_super_admin():
                messages.error(request, 'Você não tem permissão para criar Super Administradores.')
                return render(request, 'consulta_risco/admin_user_create.html', {'admin_user': admin_user})
            
            # Criar usuário
            novo_usuario = AdminUser.objects.create(
                username=username,
                password=hash_password(password),
                email=email,
                nivel_acesso=nivel_acesso,
                criado_por=admin_user
            )
            
            messages.success(request, f'Usuário {username} criado com sucesso!')
            return redirect('admin_users_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
    
    return render(request, 'consulta_risco/admin_user_create.html', {'admin_user': admin_user})


@admin_required
def admin_user_edit(request, user_id):
    """Editar usuário administrativo"""
    admin_user_id = request.session.get('admin_user_id')
    admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    
    if not admin_user or not admin_user.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para editar usuários.')
        return redirect('admin_dashboard')
    
    usuario_editado = get_object_or_404(AdminUser, id=user_id)
    
    # Verificar se pode editar super admin
    if usuario_editado.nivel_acesso == 'super_admin' and not admin_user.pode_editar_super_admin():
        messages.error(request, 'Você não tem permissão para editar Super Administradores.')
        return redirect('admin_users_list')
    
    if request.method == 'POST':
        try:
            usuario_editado.username = request.POST.get('username')
            usuario_editado.email = request.POST.get('email', '')
            novo_nivel = request.POST.get('nivel_acesso')
            
            # Verificar permissões para alterar nível
            if novo_nivel == 'super_admin' and not admin_user.pode_editar_super_admin():
                messages.error(request, 'Você não tem permissão para definir Super Administradores.')
                return render(request, 'consulta_risco/admin_user_edit.html', {
                    'usuario_editado': usuario_editado,
                    'admin_user': admin_user
                })
            
            usuario_editado.nivel_acesso = novo_nivel
            usuario_editado.ativo = request.POST.get('ativo') == 'on'
            
            # Alterar senha se fornecida
            nova_senha = request.POST.get('password')
            if nova_senha:
                usuario_editado.password = hash_password(nova_senha)
            
            usuario_editado.save()
            messages.success(request, f'Usuário {usuario_editado.username} atualizado com sucesso!')
            return redirect('admin_users_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar usuário: {str(e)}')
    
    return render(request, 'consulta_risco/admin_user_edit.html', {
        'usuario_editado': usuario_editado,
        'admin_user': admin_user
    })


@admin_required
def admin_user_delete(request, user_id):
    """Deletar usuário administrativo"""
    admin_user_id = request.session.get('admin_user_id')
    admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    
    if not admin_user or not admin_user.pode_gerenciar_usuarios():
        messages.error(request, 'Você não tem permissão para deletar usuários.')
        return redirect('admin_dashboard')
    
    usuario_deletado = get_object_or_404(AdminUser, id=user_id)
    
    # Não permitir deletar a si mesmo
    if usuario_deletado.id == admin_user.id:
        messages.error(request, 'Você não pode deletar sua própria conta.')
        return redirect('admin_users_list')
    
    # Verificar permissões para deletar super admin
    if usuario_deletado.nivel_acesso == 'super_admin' and not admin_user.pode_editar_super_admin():
        messages.error(request, 'Você não tem permissão para deletar Super Administradores.')
        return redirect('admin_users_list')
    
    if request.method == 'POST':
        username = usuario_deletado.username
        usuario_deletado.delete()
        messages.success(request, f'Usuário {username} deletado com sucesso!')
        return redirect('admin_users_list')
    
    return render(request, 'consulta_risco/admin_user_delete.html', {
        'usuario_deletado': usuario_deletado,
        'admin_user': admin_user
    })


@admin_required
def admin_profile_edit(request):
    """Editar perfil do usuário logado"""
    admin_user_id = request.session.get('admin_user_id')
    admin_user = AdminUser.objects.get(id=admin_user_id) if admin_user_id else None
    
    if not admin_user:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('admin_login')
    
    if request.method == 'POST':
        try:
            admin_user.username = request.POST.get('username')
            admin_user.email = request.POST.get('email', '')
            
            # Alterar senha se fornecida
            nova_senha = request.POST.get('password')
            if nova_senha:
                admin_user.password = hash_password(nova_senha)
            
            admin_user.save()
            
            # Atualizar sessão se username mudou
            request.session['admin_username'] = admin_user.username
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('admin_dashboard')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
    
    return render(request, 'consulta_risco/admin_profile_edit.html', {'admin_user': admin_user})


def mapa_seguranca(request):
    """View para exibir o mapa de calor da segurança do Brasil"""
    try:
        # Caminho do arquivo Excel
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ResumoCriminalidadeCidades.xlsx')
        
        if not os.path.exists(file_path):
            messages.error(request, 'Arquivo de dados não encontrado.')
            return render(request, 'consulta_risco/mapa_seguranca.html', {'mapa_html': ''})
        
        # Ler o arquivo Excel
        df = pd.read_excel(file_path)
        
        # Normalizar cabeçalhos
        def normalize_header(name):
            if not isinstance(name, str):
                return name
            n = unicodedata.normalize('NFKD', name)
            n = ''.join(c for c in n if not unicodedata.combining(c))
            n = n.strip().lower()
            return n
        
        original_cols = list(df.columns)
        normalized_cols = [normalize_header(c) for c in df.columns]
        df.columns = normalized_cols
        
        # Procurar a coluna Indicador_Crime
        indicador_col = None
        for col in df.columns:
            if 'indicador' in col and 'crime' in col:
                indicador_col = col
                break
        
        if indicador_col is None:
            messages.error(request, 'Coluna Indicador_Crime não encontrada no arquivo Excel.')
            return render(request, 'consulta_risco/mapa_seguranca.html', {'mapa_html': ''})
        
        # Procurar colunas de município e UF
        uf_col = None
        mun_col = None
        for col in df.columns:
            if col in ['uf', 'estado']:
                uf_col = col
            elif col in ['municipio', 'município', 'cidade']:
                mun_col = col
        
        if not uf_col or not mun_col:
            messages.error(request, 'Colunas UF ou Município não encontradas no arquivo Excel.')
            return render(request, 'consulta_risco/mapa_seguranca.html', {'mapa_html': ''})
        
        # Limpar dados
        df = df.dropna(subset=[uf_col, mun_col, indicador_col])
        df[uf_col] = df[uf_col].astype(str).str.strip().str.upper()
        df[mun_col] = df[mun_col].astype(str).str.strip()
        
        # Converter Indicador_Crime para numérico
        df[indicador_col] = pd.to_numeric(df[indicador_col], errors='coerce')
        df = df.dropna(subset=[indicador_col])
        
        # Calcular valores min e max do indicador para normalização (caso necessário)
        min_val = float(df[indicador_col].min()) if len(df) > 0 else 0
        max_val = float(df[indicador_col].max()) if len(df) > 0 else 1
        
        # Criar dicionário com indicadores por cidade
        indicadores_dict = {}
        for _, row in df.iterrows():
            municipio = str(row[mun_col]).strip()
            uf = str(row[uf_col]).strip()
            indicador = float(row[indicador_col])
            indicadores_dict[(municipio.upper(), uf)] = indicador
        
        # Buscar cidades do banco com coordenadas
        cidades_com_coords = Cidade.objects.select_related('estado').filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        # Função para determinar cor baseada na posição
        def get_color_by_position(posicao):
            """Retorna a cor baseada na posição no ranking"""
            if posicao is None:
                return '#808080'  # Cinza para cidades sem posição
            
            if posicao <= 10:
                return '#8B0000'  # Vermelho escuro (1-10)
            elif posicao <= 50:
                return '#FF4500'  # Vermelho claro (11-50)
            elif posicao <= 150:
                return '#FF6347'  # Laranja escuro (51-150)
            elif posicao <= 300:
                return '#FFA500'  # Laranja claro (151-300)
            elif posicao <= 600:
                return '#FFFF00'  # Amarelo (301-600)
            elif posicao <= 2000:
                return '#87CEEB'  # Azul claro (601-2000)
            else:
                return '#00008B'  # Azul escuro (2001+)
        
        # Função para normalizar posição para o heatmap
        # Posição alta (melhor) = valor alto, Posição baixa (pior) = valor baixo
        def normalize_position(posicao, max_pos):
            """Normaliza a posição: posição alta (melhor) = valor alto, posição baixa (pior) = valor baixo"""
            if posicao is None:
                return 0.5
            # Posição alta (ex: 5000) = valor alto (1.0), posição baixa (1) = valor baixo (0.0)
            # Quanto maior a posição, maior o valor normalizado
            return (posicao - 1) / (max_pos - 1) if max_pos > 1 else 0.5
        
        # Preparar dados para o mapa de calor
        heat_data = []
        markers_data = []
        posicoes_validas = []
        
        for cidade in cidades_com_coords:
            # Buscar indicador do Excel
            chave = (cidade.nome.upper().strip(), cidade.estado.sigla)
            indicador = indicadores_dict.get(chave)
            
            # Usar posição da cidade (se disponível) ou calcular baseado no indicador
            posicao = cidade.posicao
            
            if indicador is not None or posicao is not None:
                lat = float(cidade.latitude)
                lon = float(cidade.longitude)
                
                # Coletar posições válidas
                if posicao is not None:
                    posicoes_validas.append(posicao)
                
                markers_data.append({
                    'coords': [lat, lon],
                    'municipio': cidade.nome,
                    'uf': cidade.estado.sigla,
                    'indicador': indicador,
                    'posicao': posicao,
                    'cor': get_color_by_position(posicao)
                })
        
        # Calcular máximo de posições para normalização
        max_posicao = max(posicoes_validas) if posicoes_validas else 1
        
        # Preparar dados do heatmap usando posição normalizada
        for marker in markers_data:
            lat, lon = marker['coords']
            if marker['posicao'] is not None:
                peso = normalize_position(marker['posicao'], max_posicao)
            elif marker['indicador'] is not None:
                # Fallback: usar indicador normalizado
                peso = 1.0 - ((marker['indicador'] - min_val) / (max_val - min_val)) if max_val > min_val else 0.5
            else:
                peso = 0.5
            
            heat_data.append([lat, lon, peso])
        
        if not heat_data:
            messages.warning(request, 'Nenhuma cidade com coordenadas encontrada. Execute o comando: python manage.py importar_coordenadas_ibge')
            return render(request, 'consulta_risco/mapa_seguranca.html', {'mapa_html': ''})
        
        # Criar mapa centrado no Brasil
        mapa = folium.Map(
            location=[-14.2350, -51.9253],  # Centro do Brasil
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Adicionar mapa de calor com gradiente baseado em posição
        # Valor baixo (posição baixa/pior) = vermelho, Valor alto (posição alta/melhor) = azul
        HeatMap(
            heat_data,
            min_opacity=0.2,
            max_zoom=18,
            radius=25,
            blur=25,
            gradient={
                0.0: '#8B0000',    # Vermelho escuro (posição 1 - pior)
                0.15: '#FF4500',   # Vermelho claro (11-50)
                0.3: '#FF6347',    # Laranja escuro (51-150)
                0.45: '#FFA500',   # Laranja claro (151-300)
                0.6: '#FFFF00',    # Amarelo (301-600)
                0.85: '#87CEEB',  # Azul claro (601-2000)
                1.0: '#00008B'     # Azul escuro (2001+ - melhor)
            }
        ).add_to(mapa)
        
        # Criar cluster de marcadores para exibir TODAS as cidades de forma otimizada
        marker_cluster = MarkerCluster(
            name='Cidades',
            overlay=True,
            control=True,
            icon_create_function=None
        )
        
        # Adicionar TODOS os marcadores
        # Ordenar por posição (menor posição primeiro - mais crítico)
        markers_sorted = sorted(markers_data, key=lambda x: x['posicao'] if x['posicao'] is not None else 99999)
        
        for marker in markers_sorted:
            # Usar cor baseada na posição
            cor = marker['cor']
            
            # Criar popup com informações da cidade (apenas ranking)
            info_posicao = f"<strong>Posição no Ranking:</strong> {marker['posicao']}" if marker['posicao'] else "<strong>Posição:</strong> Não disponível"
            
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 180px;">
                <h4 style="margin: 0 0 10px 0; color: var(--cor-azul-escuro); font-size: 14px; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
                    {marker['municipio']} - {marker['uf']}
                </h4>
                <p style="margin: 5px 0; font-size: 12px; color: #333;">
                    {info_posicao}
                </p>
            </div>
            """
            
            folium.CircleMarker(
                location=marker['coords'],
                radius=4,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"{marker['municipio']} - {marker['uf']}",
                color=cor,
                fill=True,
                fillColor=cor,
                fillOpacity=0.7,
                weight=1
            ).add_to(marker_cluster)
        
        # Adicionar o cluster ao mapa
        marker_cluster.add_to(mapa)
        
        # Adicionar controle de camadas
        folium.LayerControl().add_to(mapa)
        
        # Converter mapa para HTML
        mapa_html = mapa._repr_html_()
        
        return render(request, 'consulta_risco/mapa_seguranca.html', {
            'mapa_html': mapa_html,
            'total_cidades': len(markers_data)
        })
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar mapa: {str(e)}')
        return render(request, 'consulta_risco/mapa_seguranca.html', {'mapa_html': ''})


