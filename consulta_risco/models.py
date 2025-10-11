from django.db import models


class TipoCupom(models.Model):
    nome = models.CharField(max_length=50, unique=True, help_text="Nome da loja")
    cor_fundo = models.CharField(max_length=7, help_text="Cor de fundo em formato hexadecimal")
    cor_texto = models.CharField(max_length=7, default='#ffffff', help_text="Cor do texto em formato hexadecimal")
    descricao = models.TextField(blank=True, help_text="Descrição da loja")
    ativo = models.BooleanField(default=True, help_text="Se a loja está ativa")
    ordem_exibicao = models.IntegerField(default=1, help_text="Ordem de exibição")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordem_exibicao', 'nome']
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
    
    def __str__(self):
        return self.nome


class Estado(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=2, unique=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
    
    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='cidades')
    posicao = models.IntegerField(null=True, blank=True, help_text="Posição no ranking de criminalidade")
    
    class Meta:
        ordering = ['nome']
        unique_together = ['nome', 'estado']
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
    
    def __str__(self):
        return f"{self.nome} - {self.estado.sigla}"


class Cupom(models.Model):
    loja = models.CharField(max_length=100, help_text="Nome da loja onde o cupom é válido")
    tipo_cupom = models.ForeignKey(TipoCupom, on_delete=models.CASCADE, help_text="Tipo de cupom com cor predefinida", null=True, blank=True)
    titulo = models.CharField(max_length=200, help_text="Título do cupom")
    descricao = models.TextField(help_text="Descrição do cupom")
    codigo = models.CharField(max_length=50, null=True, blank=True, help_text="Código do cupom (opcional)")
    link_acesso = models.URLField(help_text="Link para usar o cupom")
    ativo = models.BooleanField(default=True, help_text="Se o cupom está ativo")
    data_inicio = models.DateTimeField(null=True, blank=True, help_text="Data de início da validade do cupom")
    data_validade = models.DateTimeField(null=True, blank=True, help_text="Data de validade do cupom (deixar em branco para cupom sem prazo)")
    ordem_exibicao = models.IntegerField(default=1, help_text="Ordem de exibição (menor número aparece primeiro)")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey('AdminUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='cupons_criados')
    modificado_por = models.ForeignKey('AdminUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='cupons_modificados')
    
    class Meta:
        ordering = ['ordem_exibicao', 'data_criacao']
        verbose_name = 'Cupom'
        verbose_name_plural = 'Cupons'
    
    def __str__(self):
        return f"{self.titulo} - {self.codigo}"
    
    def esta_valido(self):
        """Verifica se o cupom está válido baseado nas datas"""
        from django.utils import timezone
        import pytz
        
        agora = timezone.now()
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        # Se não está ativo manualmente, não está válido
        if not self.ativo:
            return False
        
        # Se tem data de início e ainda não chegou
        if self.data_inicio:
            if timezone.is_aware(self.data_inicio):
                data_inicio_brasilia = self.data_inicio.astimezone(brasilia_tz)
            else:
                utc_tz = pytz.timezone('UTC')
                data_inicio_utc = utc_tz.localize(self.data_inicio)
                data_inicio_brasilia = data_inicio_utc.astimezone(brasilia_tz)
            
            agora_brasilia = agora.astimezone(brasilia_tz)
            if agora_brasilia < data_inicio_brasilia:
                return False
        
        # Se tem data de validade e já passou
        if self.data_validade:
            if timezone.is_aware(self.data_validade):
                data_validade_brasilia = self.data_validade.astimezone(brasilia_tz)
            else:
                utc_tz = pytz.timezone('UTC')
                data_validade_utc = utc_tz.localize(self.data_validade)
                data_validade_brasilia = data_validade_utc.astimezone(brasilia_tz)
            
            agora_brasilia = agora.astimezone(brasilia_tz)
            if agora_brasilia > data_validade_brasilia:
                return False
        
        return True
    
    def get_status_validade(self):
        """Retorna o status de validade do cupom"""
        from django.utils import timezone
        import pytz
        
        agora = timezone.now()
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if not self.ativo:
            return "Inativo"
        
        if self.data_inicio and agora < self.data_inicio:
            # Converter data_inicio para Brasília
            if timezone.is_aware(self.data_inicio):
                data_inicio_brasilia = self.data_inicio.astimezone(brasilia_tz)
            else:
                utc_tz = pytz.timezone('UTC')
                data_inicio_utc = utc_tz.localize(self.data_inicio)
                data_inicio_brasilia = data_inicio_utc.astimezone(brasilia_tz)
            return f"Válido a partir de {data_inicio_brasilia.strftime('%d/%m/%Y %H:%M')}"
        
        if self.data_validade and agora > self.data_validade:
            # Converter data_validade para Brasília
            if timezone.is_aware(self.data_validade):
                data_validade_brasilia = self.data_validade.astimezone(brasilia_tz)
            else:
                utc_tz = pytz.timezone('UTC')
                data_validade_utc = utc_tz.localize(self.data_validade)
                data_validade_brasilia = data_validade_utc.astimezone(brasilia_tz)
            return f"Expirado em {data_validade_brasilia.strftime('%d/%m/%Y %H:%M')}"
        
        if self.data_validade:
            # Converter data_validade para Brasília
            if timezone.is_aware(self.data_validade):
                data_validade_brasilia = self.data_validade.astimezone(brasilia_tz)
            else:
                utc_tz = pytz.timezone('UTC')
                data_validade_utc = utc_tz.localize(self.data_validade)
                data_validade_brasilia = data_validade_utc.astimezone(brasilia_tz)
            return f"Válido até {data_validade_brasilia.strftime('%d/%m/%Y %H:%M')}"
        
        return "Válido sem prazo"


class AdminUser(models.Model):
    NIVEL_CHOICES = [
        ('super_admin', 'Super Administrador'),
        ('admin', 'Administrador'),
        ('editor', 'Editor'),
    ]
    
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # Será hash em produção
    email = models.EmailField(blank=True)
    nivel_acesso = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='admin')
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_criados')
    
    # Campos para reset de senha
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expires = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Usuário Admin'
        verbose_name_plural = 'Usuários Admin'
    
    def __str__(self):
        return f"{self.username} ({self.get_nivel_acesso_display()})"
    
    def pode_criar_usuarios(self):
        """Verifica se o usuário pode criar outros usuários"""
        return self.nivel_acesso in ['super_admin', 'admin']
    
    def pode_gerenciar_usuarios(self):
        """Verifica se o usuário pode gerenciar outros usuários"""
        return self.nivel_acesso in ['super_admin', 'admin']
    
    def pode_editar_super_admin(self):
        """Verifica se pode editar super administradores"""
        return self.nivel_acesso == 'super_admin'


class AvaliacaoSeguranca(models.Model):
    """Modelo para avaliações de segurança das cidades pelos usuários"""
    email = models.EmailField(help_text="Email do usuário que fez a avaliação")
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, help_text="Estado da cidade avaliada")
    cidade = models.CharField(max_length=100, help_text="Nome da cidade avaliada")
    nota = models.IntegerField(help_text="Nota de 1 a 10 para o nível de segurança")
    data_avaliacao = models.DateTimeField(auto_now_add=True, help_text="Data e hora da avaliação")
    
    class Meta:
        ordering = ['-data_avaliacao']
        unique_together = ['email', 'estado', 'cidade']
        verbose_name = 'Avaliação de Segurança'
        verbose_name_plural = 'Avaliações de Segurança'
    
    def __str__(self):
        return f"{self.email} - {self.cidade}/{self.estado.sigla}: {self.nota}/10"
    
    def clean(self):
        """Validação da nota"""
        if self.nota < 1 or self.nota > 10:
            from django.core.exceptions import ValidationError
            raise ValidationError('A nota deve estar entre 1 e 10.')


class SistemaAtualizacao(models.Model):
    """Modelo para controlar a data de última atualização do sistema"""
    data_atualizacao = models.DateTimeField(auto_now=True, help_text="Data da última atualização dos dados")
    descricao = models.CharField(max_length=200, default="Atualização automática do sistema", help_text="Descrição da atualização")
    
    class Meta:
        verbose_name = 'Atualização do Sistema'
        verbose_name_plural = 'Atualizações do Sistema'
    
    def __str__(self):
        from django.utils import timezone
        import pytz
        
        # Converter para fuso horário de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if timezone.is_aware(self.data_atualizacao):
            data_brasilia = self.data_atualizacao.astimezone(brasilia_tz)
        else:
            utc_tz = pytz.timezone('UTC')
            data_utc = utc_tz.localize(self.data_atualizacao)
            data_brasilia = data_utc.astimezone(brasilia_tz)
            
        return f"Sistema atualizado em {data_brasilia.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def get_ultima_atualizacao(cls):
        """Retorna a data da última atualização ou cria uma nova entrada"""
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={'descricao': 'Inicialização do sistema'}
        )
        return obj.data_atualizacao
    
    @classmethod
    def atualizar_sistema(cls, descricao="Atualização automática"):
        """Atualiza a data do sistema"""
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={'descricao': descricao}
        )
        if not created:
            obj.descricao = descricao
            obj.save()
        return obj.data_atualizacao


class PaginaAtualizacao(models.Model):
    """Modelo para controlar a data de última atualização de páginas específicas"""
    nome_pagina = models.CharField(max_length=100, unique=True, help_text="Nome da página (ex: lgpd, faq, sobre)")
    data_atualizacao = models.DateTimeField(auto_now=True, help_text="Data da última atualização da página")
    descricao = models.CharField(max_length=200, default="Atualização da página", help_text="Descrição da atualização")
    
    class Meta:
        verbose_name = 'Atualização de Página'
        verbose_name_plural = 'Atualizações de Páginas'
        ordering = ['nome_pagina']
    
    def __str__(self):
        from django.utils import timezone
        import pytz
        
        # Converter para fuso horário de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if timezone.is_aware(self.data_atualizacao):
            data_brasilia = self.data_atualizacao.astimezone(brasilia_tz)
        else:
            utc_tz = pytz.timezone('UTC')
            data_utc = utc_tz.localize(self.data_atualizacao)
            data_brasilia = data_utc.astimezone(brasilia_tz)
            
        return f"{self.nome_pagina.upper()} atualizada em {data_brasilia.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def get_ultima_atualizacao(cls, nome_pagina):
        """Retorna a data da última atualização de uma página específica"""
        obj, created = cls.objects.get_or_create(
            nome_pagina=nome_pagina,
            defaults={'descricao': f'Inicialização da página {nome_pagina}'}
        )
        return obj.data_atualizacao
    
    @classmethod
    def atualizar_pagina(cls, nome_pagina, descricao=None):
        """Atualiza a data de uma página específica"""
        if descricao is None:
            descricao = f'Atualização da página {nome_pagina}'
            
        obj, created = cls.objects.get_or_create(
            nome_pagina=nome_pagina,
            defaults={'descricao': descricao}
        )
        if not created:
            obj.descricao = descricao
            obj.save()
        return obj.data_atualizacao











