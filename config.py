# config.py
import json
import os
from datetime import datetime, timedelta


class BackupConfig:
    def __init__(self, config_file="backup_config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        default_config = {
            "source_directory": "/caminho/para/diretorio/origem",
            "local_backup_directory": "/caminho/para/backup/local",
            "cloud_provider": "google_drive",  # ou "onedrive"
            "cloud_directory": "/Backups",
            "backup_schedule": {
                "full_backup_interval_days": 7,
                "incremental_interval_hours": 24,
                "cloud_sync_interval_hours": 2
            },
            "retention_policy": {
                "keep_full_backups": 4,
                "keep_incremental_days": 30
            },
            "compression": True,
            "encryption": False,
            "exclude_patterns": ["*.tmp", "*.log", "__pycache__", ".git"],
            "cloud_credentials": {
                "google_drive": {
                    "credentials_file": "credentials.json",
                    "token_file": "token.json"
                },
                "onedrive": {
                    "client_id": "",
                    "client_secret": "",
                    "tenant_id": ""
                }
            }
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        else:
            self.save_config(default_config)

        return default_config

    def save_config(self, config=None):
        if config is None:
            config = self.config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.config.get(key, default)