# config.py
import json
import os
import collections.abc

# Constante para a configuração padrão
DEFAULT_CONFIG = {
    "source_directory": "/caminho/para/diretorio/origem",
    "local_backup_directory": "/caminho/para/backup/local",
    "cloud_provider": "google_drive",
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
    "compression": {
        "enabled": True,
        "level": 6,
        "method": "zip"
    },
    "encryption": {
        "enabled": False,
        "password": None,
        "algorithm": "AES256"
    },
    "notifications": {
        "email": {
            "enabled": False
        },
        "webhook": {
            "enabled": False
        }
    },
    "exclude_patterns": ["*.tmp", "*.log", "__pycache__", ".git"],
    "performance": {
        "max_concurrent_uploads": 3,
        "chunk_size_mb": 10,
        "timeout_seconds": 300
    }
}

def deep_merge(d, u):
    """
    Mescla recursivamente dois dicionários.
    'u' é mesclado em 'd'.
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_merge(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class BackupConfig:
    def __init__(self, config_file="config_avancada.json"):
        self.config_file = config_file
        self._config = self.load_config()

    def load_config(self):
        """Carrega a configuração, mesclando com os padrões."""
        config = DEFAULT_CONFIG.copy()

        if not os.path.exists(self.config_file):
            self.save_config(config)
            return config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Mescla a configuração do usuário com a padrão
            config = deep_merge(config, user_config)

        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar o arquivo de configuração JSON: {e}")
            # Opcional: poderia lançar uma exceção ou usar a configuração padrão
        except Exception as e:
            print(f"Erro inesperado ao carregar a configuração: {e}")

        self.save_config(config) # Salva para adicionar novas chaves padrão, se houver
        return config

    def save_config(self, config=None):
        """Salva a configuração atual no arquivo."""
        if config is None:
            config = self._config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar o arquivo de configuração: {e}")

    def get(self, key, default=None):
        """Obtém um valor da configuração."""
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def source_directory(self):
        return self.get("source_directory")

    @property
    def local_backup_directory(self):
        return self.get("local_backup_directory")

    @property
    def cloud_provider(self):
        return self.get("cloud_provider")

    @property
    def backup_schedule(self):
        return self.get("backup_schedule", {})

    @property
    def retention_policy(self):
        return self.get("retention_policy", {})

    @property
    def compression_config(self):
        return self.get("compression", {})

    @property
    def encryption_config(self):
        return self.get("encryption", {})

    @property
    def exclude_patterns(self):
        return self.get("exclude_patterns", [])
