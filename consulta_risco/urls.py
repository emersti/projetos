from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),
    path('faq/', views.faq, name='faq'),
    path('lgpd/', views.lgpd, name='lgpd'),
    path('termos-uso/', views.termos_uso, name='termos_uso'),
    path('maintenance/', views.maintenance, name='maintenance'),
    path('cupons/', views.cupons, name='cupons'),
    path('api/cidades/', views.get_cidades, name='get_cidades'),
    path('api/avaliar-seguranca/', views.avaliar_seguranca, name='avaliar_seguranca'),
    path('mapa-seguranca/', views.mapa_seguranca, name='mapa_seguranca'),
    
            # URLs do sistema administrativo (alteradas para evitar conflito com Django admin)
            path('painel/login/', views.admin_login, name='admin_login'),
            path('painel/logout/', views.admin_logout, name='admin_logout'),
            path('painel/forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
            path('painel/reset-password/<str:token>/', views.admin_reset_password, name='admin_reset_password'),
            path('painel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
            path('painel/cupom/edit/', views.admin_cupom_edit, name='admin_cupom_edit'),
            path('painel/cupom/edit/<int:cupom_id>/', views.admin_cupom_edit, name='admin_cupom_edit'),
            path('painel/cupom/delete/<int:cupom_id>/', views.admin_cupom_delete, name='admin_cupom_delete'),
            
            # URLs para gerenciamento de usuários administrativos
            path('painel/usuarios/', views.admin_users_list, name='admin_users_list'),
            path('painel/usuarios/criar/', views.admin_user_create, name='admin_user_create'),
            path('painel/usuarios/editar/<int:user_id>/', views.admin_user_edit, name='admin_user_edit'),
            path('painel/usuarios/excluir/<int:user_id>/', views.admin_user_delete, name='admin_user_delete'),
            path('painel/perfil/', views.admin_profile_edit, name='admin_profile_edit'),
            
            # URL para criar usuário admin padrão (apenas desenvolvimento)
            path('painel/create-default/', views.create_default_admin, name='create_default_admin'),
            
            # URL para criar loja via AJAX
            path('painel/criar-loja/', views.criar_loja_ajax, name='criar_loja_ajax'),
            
            # URL para listar lojas
            path('painel/lojas/', views.admin_lojas_list, name='admin_lojas_list'),
            
            # URL para editar/criar loja
            path('painel/loja/edit/', views.admin_loja_edit, name='admin_loja_edit'),
            path('painel/loja/edit/<int:loja_id>/', views.admin_loja_edit, name='admin_loja_edit'),
            
            # URL para excluir loja
            path('painel/loja/delete/<int:loja_id>/', views.admin_loja_delete, name='admin_loja_delete'),
]





