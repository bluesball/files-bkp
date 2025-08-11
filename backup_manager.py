# backup_manager.py
import os
import shutil
import hashlib
import zipfile
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import fnmatch


class BackupManager:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        self.metadata_file = os.path.join(
            config.get('local_backup_directory'),
            'backup_metadata.json'
        )
        self.metadata = self.load_metadata()

    def setup_logging(self):
        log_dir = os.path.join(self.config.get('local_backup_directory'), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'backup.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {
            "last_full_backup": None,
            "last_incremental_backup": None,
            "file_hashes": {},
            "backup_history": []
        }

    def save_metadata(self):
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)

    def calculate_file_hash(self, filepath):
        """Calcula hash MD5 de um arquivo"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao calcular hash de {filepath}: {e}")
            return None

    def should_exclude_file(self, filepath):
        """Verifica se arquivo deve ser excluído baseado nos padrões"""
        exclude_patterns = self.config.get('exclude_patterns', [])
        filename = os.path.basename(filepath)

        for pattern in exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def get_files_to_backup(self, backup_type="full"):
        """Obtém lista de arquivos para backup"""
        source_dir = self.config.get('source_directory')
        files_to_backup = []

        for root, dirs, files in os.walk(source_dir):
            # Excluir diretórios baseado em padrões
            dirs[:] = [d for d in dirs if not any(
                fnmatch.fnmatch(d, pattern)
                for pattern in self.config.get('exclude_patterns', [])
            )]

            for file in files:
                filepath = os.path.join(root, file)

                if self.should_exclude_file(filepath):
                    continue

                if backup_type == "full":
                    files_to_backup.append(filepath)
                elif backup_type == "incremental":
                    # Incluir apenas arquivos modificados
                    current_hash = self.calculate_file_hash(filepath)
                    if current_hash and (
                            filepath not in self.metadata["file_hashes"] or
                            self.metadata["file_hashes"][filepath] != current_hash
                    ):
                        files_to_backup.append(filepath)

        return files_to_backup

    def create_backup_archive(self, files, backup_type, timestamp):
        """Cria arquivo de backup comprimido"""
        backup_dir = self.config.get('local_backup_directory')
        os.makedirs(backup_dir, exist_ok=True)

        archive_name = f"backup_{backup_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip"
        archive_path = os.path.join(backup_dir, archive_name)

        source_dir = self.config.get('source_directory')

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                # Caminho relativo dentro do arquivo
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

        return archive_path

    def perform_full_backup(self):
        """Executa backup completo"""
        self.logger.info("Iniciando backup completo...")
        timestamp = datetime.now()

        files = self.get_files_to_backup("full")
        if not files:
            self.logger.info("Nenhum arquivo para backup")
            return None

        self.logger.info(f"Fazendo backup de {len(files)} arquivos")

        if self.config.get('compression'):
            archive_path = self.create_backup_archive(files, "full", timestamp)
        else:
            # Backup sem compressão (cópia direta)
            backup_dir = os.path.join(
                self.config.get('local_backup_directory'),
                f"full_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(backup_dir, exist_ok=True)

            source_dir = self.config.get('source_directory')
            for file_path in files:
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(backup_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)

            archive_path = backup_dir

        # Atualizar metadados
        for file_path in files:
            self.metadata["file_hashes"][file_path] = self.calculate_file_hash(file_path)

        self.metadata["last_full_backup"] = timestamp
        self.metadata["backup_history"].append({
            "type": "full",
            "timestamp": timestamp,
            "path": archive_path,
            "file_count": len(files)
        })

        self.save_metadata()
        self.logger.info(f"Backup completo finalizado: {archive_path}")
        return archive_path

    def perform_incremental_backup(self):
        """Executa backup incremental"""
        self.logger.info("Iniciando backup incremental...")
        timestamp = datetime.now()

        files = self.get_files_to_backup("incremental")
        if not files:
            self.logger.info("Nenhum arquivo modificado para backup incremental")
            return None

        self.logger.info(f"Fazendo backup incremental de {len(files)} arquivos")

        if self.config.get('compression'):
            archive_path = self.create_backup_archive(files, "incremental", timestamp)
        else:
            backup_dir = os.path.join(
                self.config.get('local_backup_directory'),
                f"incremental_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(backup_dir, exist_ok=True)

            source_dir = self.config.get('source_directory')
            for file_path in files:
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(backup_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)

            archive_path = backup_dir

        # Atualizar metadados
        for file_path in files:
            self.metadata["file_hashes"][file_path] = self.calculate_file_hash(file_path)

        self.metadata["last_incremental_backup"] = timestamp
        self.metadata["backup_history"].append({
            "type": "incremental",
            "timestamp": timestamp,
            "path": archive_path,
            "file_count": len(files)
        })

        self.save_metadata()
        self.logger.info(f"Backup incremental finalizado: {archive_path}")
        return archive_path

    def cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        retention = self.config.get('retention_policy', {})
        keep_full = retention.get('keep_full_backups', 4)
        keep_incremental_days = retention.get('keep_incremental_days', 30)

        cutoff_date = datetime.now() - timedelta(days=keep_incremental_days)

        # Filtrar backups a serem mantidos
        full_backups = [b for b in self.metadata["backup_history"] if b["type"] == "full"]
        incremental_backups = [b for b in self.metadata["backup_history"] if b["type"] == "incremental"]

        # Manter os últimos N backups completos
        full_backups.sort(key=lambda x: x["timestamp"], reverse=True)
        backups_to_keep = full_backups[:keep_full]

        # Manter backups incrementais dentro do período
        for backup in incremental_backups:
            backup_date = datetime.fromisoformat(backup["timestamp"].replace('Z', '+00:00')) if isinstance(
                backup["timestamp"], str) else backup["timestamp"]
            if backup_date > cutoff_date:
                backups_to_keep.append(backup)

        # Remover backups antigos
        for backup in self.metadata["backup_history"][:]:
            if backup not in backups_to_keep:
                try:
                    if os.path.exists(backup["path"]):
                        if os.path.isfile(backup["path"]):
                            os.remove(backup["path"])
                        else:
                            shutil.rmtree(backup["path"])
                    self.metadata["backup_history"].remove(backup)
                    self.logger.info(f"Backup antigo removido: {backup['path']}")
                except Exception as e:
                    self.logger.error(f"Erro ao remover backup {backup['path']}: {e}")

        self.save_metadata()
