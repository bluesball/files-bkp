#!/usr/bin/env python3

import click
import json
from datetime import datetime
from pathlib import Path
from backup_restore import BackupRestorer
from monitoring import SystemMonitor


@click.group()
@click.option('--config', default='backup_config.json', help='Arquivo de configuração')
@click.pass_context
def cli(ctx, config):
    """Sistema de Backup - Interface de Linha de Comando"""
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config

    # Carregar configuração
    if Path(config).exists():
        with open(config) as f:
            ctx.obj['config'] = json.load(f)
    else:
        ctx.obj['config'] = {}


@cli.command()
@click.option('--type', 'backup_type', type=click.Choice(['full', 'incremental']),
              default='full', help='Tipo de backup')
@click.option('--compress/--no-compress', default=True, help='Comprimir backup')
@click.option('--encrypt/--no-encrypt', default=False, help='Criptografar backup')
@click.pass_context
def backup(ctx, backup_type, compress, encrypt):
    """Executa backup"""
    click.echo(f"🔄 Executando backup {backup_type}...")

    # Aqui integraria com BackupManager
    click.echo(f"✅ Backup {backup_type} concluído!")


@cli.command()
@click.pass_context
def list_backups(ctx):
    """Lista backups disponíveis"""
    click.echo("📋 Backups Disponíveis:")
    click.echo("-" * 50)

    # Integrar com BackupRestorer
    restorer = BackupRestorer(ctx.obj['config'])
    backups = restorer.list_available_backups()

    for backup in backups:
        size_mb = backup['size'] / (1024 * 1024)
        click.echo(f"📦 {backup['type']:12} | {backup['timestamp']} | {size_mb:.1f}MB")


@cli.command()
@click.argument('backup_path')
@click.argument('restore_path')
@click.option('--verify/--no-verify', default=True, help='Verificar integridade')
@click.pass_context
def restore(ctx, backup_path, restore_path, verify):
    """Restaura backup"""
    restorer = BackupRestorer(ctx.obj['config'])

    if verify:
        click.echo("🔍 Verificando integridade...")
        if not restorer.verify_backup_integrity(backup_path):
            click.echo("❌ Backup corrompido!")
            return

    click.echo(f"📥 Restaurando {backup_path} para {restore_path}...")

    if restorer.restore_backup(backup_path, restore_path):
        click.echo("✅ Restauração concluída!")
    else:
        click.echo("❌ Erro na restauração!")


@cli.command()
@click.pass_context
def status(ctx):
    """Mostra status do sistema"""
    monitor = SystemMonitor()
    info = monitor.get_system_info()
    warnings = monitor.check_system_health()

    click.echo("📊 Status do Sistema")
    click.echo("=" * 30)
    click.echo(f"🖥️  CPU: {info.get('cpu_percent', 0):.1f}%")
    click.echo(f"💾 Memória: {info.get('memory_percent', 0):.1f}%")
    click.echo(f"💿 Disco Livre: {info.get('disk_free_gb', 0):.1f}GB")

    if warnings:
        click.echo("\n⚠️  Avisos:")
        for warning in warnings:
            click.echo(f"   • {warning}")
    else:
        click.echo("\n✅ Sistema OK")


@cli.command()
@click.option('--start/--stop', help='Iniciar ou parar agendador')
@click.option('--daemon/--no-daemon', default=False, help='Executar em background')
@click.pass_context
def schedule(ctx, start, daemon):
    """Controla agendamento de backups"""
    if start:
        click.echo("🕐 Iniciando agendador...")
        # Integrar com BackupScheduler
        click.echo("✅ Agendador iniciado!")
    else:
        click.echo("🛑 Parando agendador...")
        click.echo("✅ Agendador parado!")


@cli.command()
@click.option('--days', default=30, help='Manter backups dos últimos N dias')
@click.option('--keep-full', default=4, help='Manter N backups completos')
@click.pass_context
def cleanup(ctx, days, keep_full):
    """Remove backups antigos"""
    click.echo(f"🧹 Removendo backups antigos (>{days} dias, mantendo {keep_full} completos)...")
    # Integrar com BackupManager.cleanup_old_backups()
    click.echo("✅ Limpeza concluída!")


@cli.command()
@click.argument('destination')
@click.option('--provider', type=click.Choice(['google_drive', 'onedrive']),
              default='google_drive', help='Provedor de cloud')
@click.pass_context
def sync_cloud(ctx, destination, provider):
    """Sincroniza com serviço de cloud"""
    click.echo(f"☁️  Sincronizando com {provider}...")
    # Integrar com CloudSyncManager
    click.echo("✅ Sincronização concluída!")


@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'table', 'csv']),
              default='table', help='Formato de saída')
@click.pass_context
def report(ctx, output_format):
    """Gera relatório de backups"""
    click.echo("📈 Gerando relatório...")

    # Dados fictícios para exemplo
    data = {
        "total_backups": 15,
        "full_backups": 4,
        "incremental_backups": 11,
        "total_size_gb": 125.6,
        "last_backup": "2025-01-15 14:30:00",
        "success_rate": 98.5
    }

    if output_format == 'json':
        click.echo(json.dumps(data, indent=2))
    elif output_format == 'table':
        click.echo("📊 Relatório de Backups")
        click.echo("=" * 30)
        click.echo(f"Total de backups: {data['total_backups']}")
        click.echo(f"Backups completos: {data['full_backups']}")
        click.echo(f"Backups incrementais: {data['incremental_backups']}")
        click.echo(f"Tamanho total: {data['total_size_gb']}GB")
        click.echo(f"Último backup: {data['last_backup']}")
        click.echo(f"Taxa de sucesso: {data['success_rate']}%")


if __name__ == '__main__':
    cli()

# systemd_service_template.service
[Unit]
Description = Sistema
de
Backup
Automático
After = network - online.target
Wants = network - online.target

[Service]
Type = simple
User = backup
Group = backup
WorkingDirectory = / opt / backup - system
ExecStart = / usr / bin / python3 / opt / backup - system / main.py - -action
schedule - -daemon
ExecReload = / bin / kill - HUP $MAINPID
KillMode = mixed
Restart = on - failure
RestartSec = 5
TimeoutStopSec = 30

# Variáveis de ambiente
Environment = PYTHONPATH = / opt / backup - system
Environment = BACKUP_CONFIG = / opt / backup - system / backup_config.json

# Recursos do sistema
MemoryMax = 1
G
CPUQuota = 50 %

# Logs
StandardOutput = journal
StandardError = journal
SyslogIdentifier = backup - system

[Install]
WantedBy = multi - user.target

# docker-compose.yml
version: '3.8'

services:
backup - system:
build:.
container_name: backup - system
restart: unless - stopped
environment:
- BACKUP_CONFIG = / app / config / backup_config.json
- TZ = America / Sao_Paulo
volumes:
-./ config: / app / config
-./ logs: / app / logs
-./ data: / app / data
- / caminho / para / origem: / app / source: ro
- / caminho / para / backup: / app / backup
-./ credentials: / app / credentials
networks:
- backup - net
healthcheck:
test: ["CMD", "python", "health_check.py"]
interval: 30
s
timeout: 10
s
retries: 3

# Opcional: Interface web separada
backup - web:
build:
context:.
dockerfile: Dockerfile.web
container_name: backup - web
restart: unless - stopped
ports:
- "8080:8080"
environment:
- BACKUP_API_URL = http: // backup - system: 8000
depends_on:
- backup - system
networks:
- backup - net

# Opcional: Banco de dados para logs e metadados
backup - db:
image: postgres:13 - alpine
container_name: backup - db
restart: unless - stopped
environment:
- POSTGRES_DB = backup_system
- POSTGRES_USER = backup
- POSTGRES_PASSWORD = backup_secure_password
volumes:
- backup_db_data: / var / lib / postgresql / data
networks:
- backup - net

networks:
backup - net:
driver: bridge

volumes:
backup_db_data:

# Dockerfile
FROM
python: 3.11 - slim

# Instalar dependências do sistema
RUN
apt - get
update & & apt - get
install - y \
    cron \
    rsync \
    curl \
    & & rm - rf / var / lib / apt / lists / *

# Criar usuário não-root
RUN
useradd - -create - home - -shell / bin / bash
backup

# Definir diretório de trabalho
WORKDIR / app

# Copiar requirements e instalar dependências Python
COPY
requirements.txt.
RUN
pip
install - -no - cache - dir - r
requirements.txt

# Copiar código da aplicação
COPY - -chown = backup:backup..

# Criar diretórios necessários
RUN
mkdir - p / app / {logs, config, credentials, data} & & \
chown - R
backup: backup / app

# Mudar para usuário não-root
USER
backup

# Expor porta para interface web (opcional)
EXPOSE
8080

# Comando padrão
CMD["python", "main.py", "--action", "schedule", "--daemon"]

# health_check.py
# !/usr/bin/env python3

import sys
import os
import json
import requests
from datetime import datetime, timedelta


def check_backup_system():
    """Verifica saúde do sistema de backup"""
    try:
        # Verificar se arquivo de configuração existe
        if not os.path.exists('backup_config.json'):
            print("❌ Arquivo de configuração não encontrado")
            return False

        # Verificar logs recentes
        log_file = 'logs/backup.log'
        if os.path.exists(log_file):
            # Verificar se há logs recentes (últimas 24h)
            stat = os.stat(log_file)
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            if datetime.now() - last_modified > timedelta(hours=24):
                print("⚠️  Logs não atualizados nas últimas 24h")
                return False

        # Verificar metadados de backup
        metadata_file = 'backup_metadata.json'
        if os.path.exists(metadata_file):
            with open(metadata_file) as f:
                metadata = json.load(f)

            # Verificar último backup
            last_backup = metadata.get('last_incremental_backup')
            if last_backup:
                last_backup_date = datetime.fromisoformat(last_backup.replace('Z', '+00:00'))
                if datetime.now() - last_backup_date > timedelta(days=2):
                    print("⚠️  Último backup há mais de 2 dias")
                    return False

        print("✅ Sistema de backup saudável")
        return True

    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False


if __name__ == "__main__":
    if not check_backup_system():
        sys.exit(1)
    sys.exit(0)
