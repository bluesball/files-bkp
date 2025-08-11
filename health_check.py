#!/usr/bin/env python3

import sys
import os
import json
from datetime import datetime, timedelta

CONFIG_FILE = os.getenv("BACKUP_CONFIG", "config_avancada.json")

def check_backup_system():
    """Verifica a saúde do sistema de backup com base nos metadados."""
    try:
        # Carregar a configuração para encontrar o diretório de backup
        if not os.path.exists(CONFIG_FILE):
            print(f"CRITICAL: Arquivo de configuração '{CONFIG_FILE}' não encontrado.")
            return 2

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        backup_dir = config.get("local_backup_directory")
        if not backup_dir or not os.path.isdir(backup_dir):
            print(f"WARNING: Diretório de backup não configurado ou não encontrado.")
            return 1

        metadata_file = os.path.join(backup_dir, 'backup_metadata.json')
        if not os.path.exists(metadata_file):
            print("CRITICAL: Arquivo de metadados (backup_metadata.json) não encontrado.")
            return 2

        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Verificar o último backup completo
        last_full_ts = metadata.get('last_full_backup_ts')
        if not last_full_ts:
            print("WARNING: Nenhum backup completo foi executado ainda.")
            return 1

        full_backup_interval_days = config.get("backup_schedule", {}).get("full_backup_interval_days", 7)
        last_full_date = datetime.fromisoformat(last_full_ts)
        if datetime.now() - last_full_date > timedelta(days=full_backup_interval_days * 1.1): # 10% de tolerância
            print(f"CRITICAL: O último backup completo foi há mais de {full_backup_interval_days} dias.")
            return 2

        print("OK: Sistema de backup parece saudável.")
        return 0

    except Exception as e:
        print(f"UNKNOWN: Ocorreu um erro inesperado durante a verificação: {e}")
        return 3

if __name__ == "__main__":
    exit_code = check_backup_system()
    sys.exit(exit_code)
