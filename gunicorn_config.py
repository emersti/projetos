# Configuração do Gunicorn para safetyscorebrasil.com.br

# Configurações básicas
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configurações de processo
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Configurações de logging
accesslog = "/var/www/safetyscorebrasil.com.br/logs/gunicorn_access.log"
errorlog = "/var/www/safetyscorebrasil.com.br/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
worker_tmp_dir = "/dev/shm"
forwarded_allow_ips = "*"
secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}
