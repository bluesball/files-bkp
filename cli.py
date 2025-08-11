#!/usr/bin/env python3

import click
import logging
from config import BackupConfig
from backup_manager import BackupManager

# Configuração básica de logging para a CLI
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@click.group()
@click.option('--config', 'config_path', default='config_avancada.json', help='Caminho para o arquivo de configuração.')
@click.pass_context
def cli(ctx, config_path):
    """Interface de Linha de Comando para o Sistema de Backup."""
    try:
        config = BackupConfig(config_path)
        ctx.obj = {
            'config': config,
            'backup_manager': BackupManager(config)
        }
    except FileNotFoundError:
        click.echo(f"Erro: Arquivo de configuração '{config_path}' não encontrado.")
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Erro ao carregar a configuração: {e}")
        ctx.exit(1)

@cli.command()
@click.option('--type', 'backup_type', type=click.Choice(['full', 'incremental']), required=True, help='O tipo de backup a ser executado.')
@click.pass_context
def backup(ctx, backup_type):
    """Executa um backup completo ou incremental sob demanda."""
    manager = ctx.obj['backup_manager']
    click.echo(f"Iniciando backup {backup_type}...")
    
    try:
        if backup_type == 'full':
            result_path = manager.perform_full_backup()
        else:
            result_path = manager.perform_incremental_backup()
        
        if result_path:
            click.secho(f"Backup concluído com sucesso: {result_path}", fg='green')
        else:
            click.secho("Nenhum arquivo precisou de backup.", fg='yellow')
    except Exception as e:
        click.secho(f"Falha no backup: {e}", fg='red')
        ctx.exit(1)

@cli.command(name='list-backups')
@click.pass_context
def list_backups(ctx):
    """Lista o histórico de backups registrados nos metadados."""
    manager = ctx.obj['backup_manager']
    history = manager.metadata.get('backup_history', [])
    
    if not history:
        click.echo("Nenhum backup encontrado no histórico.")
        return

    click.echo("Histórico de Backups:")
    click.echo(f"{'Tipo':<15} {'Data e Hora':<25} {'Arquivos':<10} {'Caminho'}")
    click.echo("-" * 80)
    
    # Ordena do mais recente para o mais antigo
    for item in sorted(history, key=lambda x: x['timestamp'], reverse=True):
        click.echo(
            f"{item['type']:<15} "
            f"{item['timestamp']:<25} "
            f"{item['file_count']:<10} "
            f"{item['path']}"
        )

@cli.command()
@click.pass_context
def cleanup(ctx):
    """Executa a limpeza de backups antigos com base na política de retenção."""
    manager = ctx.obj['backup_manager']
    click.echo("Iniciando limpeza de backups antigos...")
    
    try:
        manager.cleanup_old_backups()
        click.secho("Limpeza concluída com sucesso.", fg='green')
    except Exception as e:
        click.secho(f"Falha na limpeza: {e}", fg='red')
        ctx.exit(1)

@cli.command()
@click.pass_context
def status(ctx):
    """Exibe um status rápido do sistema de backup."""
    manager = ctx.obj['backup_manager']
    metadata = manager.metadata

    click.echo("--- Status do Sistema de Backup ---")
    
    last_full = metadata.get('last_full_backup_ts')
    if last_full:
        click.echo(f"Último Backup Completo: {last_full}")
    else:
        click.secho("Nenhum backup completo executado ainda.", fg='yellow')

    total_backups = len(metadata.get('backup_history', []))
    click.echo(f"Total de Backups no Histórico: {total_backups}")

    # TODO: Adicionar mais métricas, como espaço em disco usado.

if __name__ == '__main__':
    cli()
