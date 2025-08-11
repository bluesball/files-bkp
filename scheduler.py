# scheduler.py
import time
import schedule
import threading
from datetime import datetime, timedelta


class BackupScheduler:
    def __init__(self, config, backup_manager, cloud_sync_manager):
        self.config = config
        self.backup_manager = backup_manager
        self.cloud_sync_manager = cloud_sync_manager
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)

    def setup_schedule(self):
        """Configura agendamento de backups"""
        schedule_config = self.config.get('backup_schedule', {})

        # Backup completo semanal
        full_interval = schedule_config.get('full_backup_interval_days', 7)
        schedule.every(full_interval).days.do(self._run_full_backup)

        # Backup incremental diário
        inc_interval = schedule_config.get('incremental_interval_hours', 24)
        schedule.every(inc_interval).hours.do(self._run_incremental_backup)

        # Sincronização com cloud
        cloud_interval = schedule_config.get('cloud_sync_interval_hours', 2)
        schedule.every(cloud_interval).hours.do(self._sync_pending_backups)

        # Limpeza semanal
        schedule.every().sunday.at("02:00").do(self._cleanup_backups)

    def _run_full_backup(self):
        """Executa backup completo"""
        self.logger.info("Executando backup completo agendado")
        backup_path = self.backup_manager.perform_full_backup()
        if backup_path:
            self._queue_for_cloud_sync(backup_path)

    def _run_incremental_backup(self):
        """Executa backup incremental"""
        self.logger.info("Executando backup incremental agendado")
        backup_path = self.backup_manager.perform_incremental_backup()
        if backup_path:
            self._queue_for_cloud_sync(backup_path)

    def _sync_pending_backups(self):
        """Sincroniza backups pendentes com cloud"""
        # Implementar fila de sincronização
        pass

    def _cleanup_backups(self):
        """Executa limpeza de backups antigos"""
        self.logger.info("Executando limpeza de backups antigos")
        self.backup_manager.cleanup_old_backups()

    def _queue_for_cloud_sync(self, backup_path):
        """Adiciona backup à fila de sincronização"""
        # Em uma implementação real, isso seria uma fila persistente
        if self.cloud_sync_manager:
            threading.Thread(
                target=self.cloud_sync_manager.sync_to_cloud,
                args=(backup_path,)
            ).start()

    def start(self):
        """Inicia o agendador"""
        if self.running:
            return

        self.setup_schedule()
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Agendador de backups iniciado")

    def stop(self):
        """Para o agendador"""
        self.running = False
        if self.thread:
            self.thread.join()
        schedule.clear()
        self.logger.info("Agendador de backups parado")

    def _run_scheduler(self):
        """Loop principal do agendador"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
