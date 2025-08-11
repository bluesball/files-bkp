# backup_manager.py
import os
import shutil
import hashlib
import zipfile
import json
import logging
import fnmatch
from datetime import datetime, timedelta
from pathlib import Path

class BackupManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backup_root_path = Path(self.config.local_backup_directory)
        self.metadata_path = self.backup_root_path / 'backup_metadata.json'
        self._metadata = None

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self._load_metadata()
        return self._metadata

    def _load_metadata(self):
        """Carrega os metadados do arquivo JSON."""
        try:
            if self.metadata_path.exists():
                with self.metadata_path.open('r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Erro ao carregar metadados: {e}")
        
        return {
            "last_full_backup_ts": None,
            "file_hashes": {},
            "backup_history": []
        }

    def _save_metadata(self):
        """Salva os metadados no arquivo JSON."""
        try:
            self.backup_root_path.mkdir(exist_ok=True)
            with self.metadata_path.open('w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=4, default=str)
        except IOError as e:
            self.logger.error(f"Erro ao salvar metadados: {e}")

    def _calculate_file_hash(self, filepath):
        """Calcula o hash SHA256 de um arquivo para detecção de mudanças."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, PermissionError) as e:
            self.logger.error(f"Não foi possível calcular o hash de {filepath}: {e}")
            return None

    def _get_files_to_backup(self, is_full_backup=False):
        """Retorna uma lista de arquivos que precisam de backup."""
        source_dir = Path(self.config.source_directory)
        if not source_dir.is_dir():
            self.logger.error(f"Diretório de origem não encontrado: {source_dir}")
            return [], {}

        files_to_backup = []
        current_hashes = {}
        exclude_patterns = self.config.exclude_patterns

        for filepath in source_dir.rglob('*'):
            if filepath.is_dir():
                continue

            # Verifica se o arquivo ou qualquer um de seus diretórios pais corresponde a um padrão de exclusão
            if any(fnmatch.fnmatch(part, pattern) for pattern in exclude_patterns for part in filepath.parts):
                continue

            new_hash = self._calculate_file_hash(filepath)
            if not new_hash:
                continue

            str_filepath = str(filepath)
            current_hashes[str_filepath] = new_hash

            if is_full_backup or self.metadata["file_hashes"].get(str_filepath) != new_hash:
                files_to_backup.append(filepath)
        
        return files_to_backup, current_hashes

    def _create_backup_archive(self, files_to_backup, backup_type, timestamp):
        """Cria um arquivo de backup (compactado ou não)."""
        source_dir = Path(self.config.source_directory)
        target_path_str = f"{backup_type}_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        target_path = self.backup_root_path / target_path_str

        try:
            if self.config.compression_config.get("enabled", True):
                target_path_zip = target_path.with_suffix('.zip')
                self.logger.info(f"Criando arquivo compactado: {target_path_zip}")
                with zipfile.ZipFile(target_path_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                    for file in files_to_backup:
                        zipf.write(file, file.relative_to(source_dir))
                return str(target_path_zip)
            else:
                self.logger.info(f"Copiando arquivos para: {target_path}")
                target_path.mkdir(parents=True, exist_ok=True)
                for file in files_to_backup:
                    dest = target_path / file.relative_to(source_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest)
                return str(target_path)
        except (IOError, PermissionError, zipfile.BadZipFile) as e:
            self.logger.error(f"Falha ao criar o arquivo de backup: {e}")
            return None

    def _perform_backup(self, is_full_backup):
        """Lógica central para executar um backup (completo ou incremental)."""
        backup_type = "full" if is_full_backup else "incremental"
        self.logger.info(f"Iniciando backup {backup_type}...")

        files_to_backup, current_hashes = self._get_files_to_backup(is_full_backup)

        if not files_to_backup:
            self.logger.info("Nenhum arquivo novo ou modificado para fazer backup.")
            return None

        self.logger.info(f"Encontrados {len(files_to_backup)} arquivos para o backup {backup_type}.")
        timestamp = datetime.now()
        archive_path = self._create_backup_archive(files_to_backup, backup_type, timestamp)

        if not archive_path:
            return None

        # Atualiza os metadados após um backup bem-sucedido
        if is_full_backup:
            self.metadata["file_hashes"] = current_hashes
            self.metadata["last_full_backup_ts"] = timestamp.isoformat()
        else:
            self.metadata["file_hashes"].update(current_hashes)

        self.metadata["backup_history"].append({
            "type": backup_type,
            "timestamp": timestamp.isoformat(),
            "path": archive_path,
            "file_count": len(files_to_backup)
        })
        self._save_metadata()
        self.logger.info(f"Backup {backup_type} concluído com sucesso: {archive_path}")
        return archive_path

    def perform_full_backup(self):
        return self._perform_backup(is_full_backup=True)

    def perform_incremental_backup(self):
        if not self.metadata.get("last_full_backup_ts"):
            self.logger.warning("Nenhum backup completo encontrado. Executando um backup completo primeiro.")
            return self.perform_full_backup()
        return self._perform_backup(is_full_backup=False)

    def cleanup_old_backups(self):
        """Remove backups antigos com base na política de retenção."""
        self.logger.info("Iniciando limpeza de backups antigos...")
        policy = self.config.retention_policy
        if not policy or not self.metadata["backup_history"]:
            self.logger.info("Nenhuma política de retenção definida ou nenhum backup para limpar.")
            return

        keep_full = policy.get('keep_full_backups', 4)
        keep_incremental_days = policy.get('keep_incremental_days', 30)
        cutoff_date = datetime.now() - timedelta(days=keep_incremental_days)

        full_backups = sorted([b for b in self.metadata["backup_history"] if b['type'] == 'full'], key=lambda x: x['timestamp'], reverse=True)
        incrementals = [b for b in self.metadata["backup_history"] if b['type'] == 'incremental']

        backups_to_keep = set()
        # Mantém os N backups completos mais recentes
        for backup in full_backups[:keep_full]:
            backups_to_keep.add(backup['path'])

        # Mantém incrementais recentes
        for backup in incrementals:
            backup_ts = datetime.fromisoformat(backup['timestamp'])
            if backup_ts >= cutoff_date:
                backups_to_keep.add(backup['path'])

        backups_to_remove = []
        updated_history = []

        for backup in self.metadata["backup_history"]:
            if backup['path'] in backups_to_keep:
                updated_history.append(backup)
            else:
                backups_to_remove.append(backup)

        for backup in backups_to_remove:
            path = Path(backup['path'])
            try:
                self.logger.info(f"Removendo backup antigo: {path}")
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            except (IOError, PermissionError) as e:
                self.logger.error(f"Erro ao remover {path}: {e}")

        self.metadata["backup_history"] = updated_history
        self._save_metadata()
        self.logger.info("Limpeza de backups concluída.")
