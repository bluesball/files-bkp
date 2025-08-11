# Sistema de Backup Completo - Documentação

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Instalação e Configuração](#instalação-e-configuração)
4. [Guia de Uso](#guia-de-uso)
5. [Configurações Avançadas](#configurações-avançadas)
6. [Monitoramento e Logs](#monitoramento-e-logs)
7. [Troubleshooting](#troubleshooting)
8. [Segurança](#segurança)

## 🎯 Visão Geral

Este sistema de backup oferece uma solução completa e automatizada para proteção de dados com as seguintes características principais:

### ✨ Funcionalidades Principais

- **Backup Full e Incremental**: Sistema inteligente que detecta mudanças
- **Sincronização Cloud**: Suporte para Google Drive e OneDrive
- **Agendamento Automático**: Execução programada de backups
- **Compressão e Criptografia**: Otimização de espaço e segurança
- **Interface Web**: Monitoramento via navegador
- **CLI Avançada**: Controle completo via linha de comando
- **Notificações**: Alertas por email e webhook
- **Restauração Seletiva**: Recuperação granular de arquivos

### 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Origem        │───▶│  Backup Local   │───▶│  Cloud Storage  │
│  /documentos    │    │  /backup_disk   │    │  Google Drive   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Detecção de     │    │  Compressão/    │    │ Sincronização   │
│ Mudanças (Hash) │    │  Criptografia   │    │ Automática      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 📁 Estrutura de Arquivos

```
backup_system/
├── 📄 config.py                 # Gerenciador de configurações
├── 📄 backup_manager.py         # Lógica principal de backup
├── 📄 cloud_sync.py            # Sincronização com cloud
├── 📄 scheduler.py             # Agendamento de tarefas
├── 📄 main.py                  # Interface principal
├── 📄 backup_cli.py            # Interface de linha de comando
├── 📄 encryption_manager.py    # Criptografia de arquivos
├── 📄 notification_manager.py  # Sistema de notificações
├── 📄 monitoring.py            # Monitoramento do sistema
├── 📄 backup_restore.py        # Restauração de backups
├── 📄 web_interface.py         # Interface web
├── 📄 health_check.py          # Verificação de saúde
├── 📄 run_tests.py             # Testes automatizados
├── 📄 requirements.txt         # Dependências
├── 📄 Dockerfile               # Containerização
├── 📄 docker-compose.yml       # Orquestração
└── 📁 logs/                    # Arquivos de log
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Espaço em disco suficiente para backups
- Conexão com internet para sincronização cloud
- (Opcional) Docker para containerização

### Instalação Automática

```bash
# 1. Clonar ou baixar os arquivos do sistema
cd backup_system

# 2. Executar instalação automática
python install.py

# 3. Seguir as instruções na tela
```

### Instalação Manual

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Criar diretórios
mkdir -p logs config credentials

# 3. Configurar credenciais do Google Drive (se usar)
# - Baixar credentials.json do Google Cloud Console
# - Colocar na pasta credentials/

# 4. Criar configuração inicial
cp exemplo_config.json backup_config.json

# 5. Editar configurações
nano backup_config.json
```

### Configuração do Google Drive

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Ative a Google Drive API
4. Crie credenciais OAuth 2.0
5. Baixe o arquivo `credentials.json`
6. Execute o sistema pela primeira vez para autorizar

```bash
# Primeira execução para autorizar
python main.py --action full
```

## 📖 Guia de Uso

### Interface de Linha de Comando

```bash
# Backup completo manual
python backup_cli.py backup --type full

# Backup incremental
python backup_cli.py backup --type incremental

# Listar backups disponíveis
python backup_cli.py list-backups

# Verificar status do sistema
python backup_cli.py status

# Restaurar backup
python backup_cli.py restore /caminho/backup.zip /caminho/destino

# Gerar relatório
python backup_cli.py report --format table

# Limpar backups antigos
python backup_cli.py cleanup --days 30 --keep-full 4

# Sincronizar com cloud
python backup_cli.py sync-cloud /Backups/MeuPC
```

### Interface Principal

```bash
# Backup manual completo
python main.py --action full

# Backup manual incremental  
python main.py --action incremental

# Modo agendado (interativo)
python main.py --action schedule

# Modo daemon (background)
python main.py --action schedule --daemon

# Limpeza de backups antigos
python main.py --action cleanup

# Usar configuração específica
python main.py --config minha_config.json --action full
```

### Interface Web

```bash
# Iniciar interface web
python -c "
from web_interface import start_web_interface
from main import *
config = BackupConfig()
backup_manager = BackupManager(config)
cloud_sync = CloudSyncManager(config)
start_web_interface({'config': config, 'backup_manager': backup_manager}, 8080)
"

# Acessar: http://localhost:8080
```

### Containerização com Docker

```bash
# Construir imagem
docker build -t backup-system .

# Executar container
docker run -d \
  --name backup-system \
  -v /caminho/origem:/app/source:ro \
  -v /caminho/backup:/app/backup \
  -v ./config:/app/config \
  -v ./logs:/app/logs \
  backup-system

# Usar docker-compose
docker-compose up -d
```

## ⚙️ Configurações Avançadas

### Exemplo de Configuração Completa

```json
{
    "source_directory": "/home/usuario/documentos",
    "local_backup_directory": "/media/backup_disk/backups",
    "cloud_provider": "google_drive",
    "cloud_directory": "/Backups/MeuPC",
    
    "backup_schedule": {
        "full_backup_interval_days": 7,
        "incremental_interval_hours": 6,
        "cloud_sync_interval_hours": 1
    },
    
    "retention_policy": {
        "keep_full_backups": 4,
        "keep_incremental_days": 30
    },
    
    "compression": {
        "enabled": true,
        "level": 6,
        "method": "zip"
    },
    
    "encryption": {
        "enabled": true,
        "password": "senha_super_segura_2024!",
        "algorithm": "AES256"
    },
    
    "notifications": {
        "email": {
            "enabled": true,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "backup@meudominio.com",
            "password": "senha_do_app",
            "to": "admin@meudominio.com"
        },
        "webhook": {
            "enabled": true,
            "url": "https://hooks.slack.com/services/XXX"
        }
    }
}
```

### Padrões de Exclusão Recomendados

```json
{
    "exclude_patterns": [
        "*.tmp", "*.temp", "*.cache",
        "*.log", "*.bak", "*.swp",
        "__pycache__", ".git", ".svn",
        "node_modules", "venv", ".env",
        "*.iso", "*.img", "*.vmdk",
        "Thumbs.db", ".DS_Store",
        "System Volume Information",
        "$RECYCLE.BIN", ".Trash-*",
        "*.lock", "*.pid"
    ]
}
```

### Configuração de Performance

```json
{
    "performance": {
        "max_concurrent_uploads": 3,
        "chunk_size_mb": 10,
        "timeout_seconds": 300,
        "retry_attempts": 3,
        "throttle_cpu_percent": 80,
        "max_memory_usage_gb": 2
    }
}
```

## 📊 Monitoramento e Logs

### Tipos de Log

- **backup.log**: Log principal do sistema
- **error.log**: Erros específicos
- **cloud_sync.log**: Sincronização com cloud
- **scheduler.log**: Agendamento de tarefas

### Monitoramento via Systemd (Linux)

```bash
# Instalar como serviço
sudo cp backup-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable backup-system
sudo systemctl start backup-system

# Verificar status
sudo systemctl status backup-system

# Ver logs
sudo journalctl -u backup-system -f
```

### Métricas do Sistema

```bash
# Via CLI
python backup_cli.py status

# Via logs
tail -f logs/backup.log

# Via interface web
curl http://localhost:8080/api/status
```

## 🔧 Troubleshooting

### Problemas Comuns

#### Erro de Autenticação Google Drive
```bash
# Remover token e reautenticar
rm token.json
python main.py --action full
```

#### Backup Travado
```bash
# Verificar processos
ps aux | grep python | grep backup

# Parar processo
pkill -f "python.*backup"

# Verificar logs
tail -100 logs/backup.log
```

#### Espaço Insuficiente
```bash
# Verificar espaço
df -h

# Limpar backups antigos
python backup_cli.py cleanup --days 15

# Verificar tamanhos
du -sh backups/*
```

#### Erro de Permissão
```bash
# Ajustar permissões
chmod -R 755 backup_system/
chown -R usuario:grupo backup_system/
```

### Logs de Diagnóstico

```bash
# Habilitar modo debug
export BACKUP_DEBUG=1
python main.py --action full

# Verificar integridade dos backups
python backup_cli.py list-backups
python -c "
from backup_restore import BackupRestorer
r = BackupRestorer({})
for backup in r.list_available_backups():
    print(f'{backup[\"path\"]}: {r.verify_backup_integrity(backup[\"path\"])}')
"
```

## 🔒 Segurança

### Boas Práticas

1. **Senhas Seguras**: Use senhas fortes para criptografia
2. **Permissões Restritas**: Limite acesso aos arquivos de backup
3. **Credenciais Separadas**: Use contas específicas para backup
4. **Monitoramento**: Configure alertas para falhas
5. **Teste Regular**: Verifique integridade dos backups periodicamente

### Criptografia

```bash
# Habilitar criptografia
{
    "encryption": {
        "enabled": true,
        "password": "sua_senha_muito_segura",
        "algorithm": "AES256"
    }
}
```

### Isolamento por Container

```yaml
# docker-compose.yml
services:
  backup-system:
    build: .
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    cap_add:
      - DAC_OVERRIDE
    user: "1000:1000"
```

## 📈 Exemplos de Uso

### Cenário 1: Backup Doméstico

```json
{
    "source_directory": "/home/joao/Documentos",
    "local_backup_directory": "/media/hd_externo/backups",
    "backup_schedule": {
        "full_backup_interval_days": 7,
        "incremental_interval_hours": 24
    },
    "compression": {"enabled": true},
    "cloud_provider": "google_drive"
}
```

### Cenário 2: Servidor Empresarial

```json
{
    "source_directory": "/opt/aplicacao/dados",
    "local_backup_directory": "/backup/local",
    "backup_schedule": {
        "full_backup_interval_days": 1,
        "incremental_interval_hours": 4
    },
    "retention_policy": {
        "keep_full_backups": 30,
        "keep_incremental_days": 7
    },
    "notifications": {
        "email": {"enabled": true},
        "webhook": {"enabled": true}
    },
    "encryption": {"enabled": true}
}
```

### Cenário 3: Desenvolvimento

```json
{
    "source_directory": "/home/dev/projetos",
    "exclude_patterns": [
        "node_modules", "venv", ".git",
        "*.pyc", "*.o", "build/", "dist/"
    ],
    "backup_schedule": {
        "incremental_interval_hours": 2
    },
    "compression": {"enabled": true, "level": 9}
}
```

## 🔄 Automação com Cron

```bash
# Editar crontab
crontab -e

# Backup incremental a cada 6 horas
0 */6 * * * /usr/bin/python3 /opt/backup-system/main.py --action incremental >> /var/log/backup-cron.log 2>&1

# Backup completo todo domingo às 2h
0 2 * * 0 /usr/bin/python3 /opt/backup-system/main.py --action full >> /var/log/backup-cron.log 2>&1

# Limpeza mensal
0 3 1 * * /usr/bin/python3 /opt/backup-system/backup_cli.py cleanup --days 90 >> /var/log/backup-cron.log 2>&1
```

## 📞 Suporte e Contribuição

### Relatório de Bugs

1. Execute com modo debug habilitado
2. Colete logs relevantes
3. Documente passos para reproduzir
4. Inclua configuração (sem credenciais)

### Contribuições

1. Fork do projeto
2. Criar branch para feature
3. Implementar testes
4. Documentar mudanças
5. Submeter pull request

---

**💡 Dicas Finais:**

- Teste as restaurações regularmente
- Monitore o espaço em disco
- Mantenha backups em locais separados
- Configure alertas para falhas
- Documente sua configuração
- Atualize o sistema regularmente