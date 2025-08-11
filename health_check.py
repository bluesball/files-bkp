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
