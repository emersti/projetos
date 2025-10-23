from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.timezone import localtime
from django.db import transaction
import hashlib
import json
import secrets
import string
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


