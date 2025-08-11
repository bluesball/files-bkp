# scheduler.py
import time
import logging
import threading
from datetime import datetime, timedelta

class BackupScheduler:
    """Gerencia a execução de tarefas de backup de forma assíncrona e baseada em estado."""

    def __init__(self, config, backup_manager, cloud_sync_manager):
        self.config = config
        self.backup_manager = backup_manager
        self.cloud_sync_manager = cloud_sync_manager
        self.logger = logging.getLogger(__name__)
        
        self._stop_event = threading.Event()
        self._thread = None

    def _run_task(self, task_func, task_name):
        """Executa uma tarefa e lida com exceções."""
        try:
            self.logger.info(f"Iniciando tarefa agendada: {task_name}")
            task_func()
            self.logger.info(f"Tarefa agendada '{task_name}' concluída com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao executar a tarefa agendada '{task_name}': {e}", exc_info=True)

    def _schedule_runner(self):
        """Loop principal que verifica e executa tarefas pendentes."""
        self.logger.info("O loop do agendador foi iniciado.")
        
        # Dicionário para rastrear a última execução de cada tarefa
        last_run = {
            "full_backup": None,
            "incremental_backup": None,
            "cleanup": None
        }

        while not self._stop_event.is_set():
            now = datetime.now()
            schedule_config = self.config.backup_schedule

            # 1. Verificar se é hora de um backup completo
            full_interval = timedelta(days=schedule_config.get('full_backup_interval_days', 7))
            last_full_ts = self.backup_manager.metadata.get("last_full_backup_ts")
            last_full_time = datetime.fromisoformat(last_full_ts) if last_full_ts else None

            if not last_full_time or (now - last_full_time) >= full_interval:
                self.logger.info("Disparando backup completo devido ao intervalo agendado.")
                backup_path = self.backup_manager.perform_full_backup()
                if backup_path and self.cloud_sync_manager:
                    self.cloud_sync_manager.sync_to_cloud(backup_path)
                # Atualiza o timestamp da última execução, mesmo que o backup não tenha gerado arquivos
                last_run["full_backup"] = now

            # 2. Verificar se é hora de um backup incremental
            inc_interval = timedelta(hours=schedule_config.get('incremental_interval_hours', 24))
            if last_run["incremental_backup"] is None or (now - last_run["incremental_backup"]) >= inc_interval:
                if self.backup_manager.metadata.get("last_full_backup_ts"): # Só roda se já houver um completo
                    self.logger.info("Disparando backup incremental devido ao intervalo agendado.")
                    backup_path = self.backup_manager.perform_incremental_backup()
                    if backup_path and self.cloud_sync_manager:
                        self.cloud_sync_manager.sync_to_cloud(backup_path)
                    last_run["incremental_backup"] = now

            # 3. Verificar se é hora da limpeza
            cleanup_interval = timedelta(days=1) # Roda a limpeza uma vez por dia
            if last_run["cleanup"] is None or (now - last_run["cleanup"]) >= cleanup_interval:
                self.logger.info("Disparando limpeza de backups antigos.")
                self.backup_manager.cleanup_old_backups()
                last_run["cleanup"] = now

            # Espera por 60 segundos antes da próxima verificação
            self._stop_event.wait(60)

        self.logger.info("O loop do agendador foi encerrado.")

    def start(self):
        """Inicia o agendador em uma thread de segundo plano."""
        if self._thread and self._thread.is_alive():
            self.logger.warning("O agendador já está em execução.")
            return

        self.logger.info("Iniciando o agendador de backups...")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._schedule_runner, daemon=True)
        self._thread.start()

    def stop(self):
        """Sinaliza para o agendador parar e aguarda sua finalização."""
        if not self._thread or not self._thread.is_alive():
            self.logger.info("O agendador não está em execução.")
            return

        self.logger.info("Parando o agendador de backups...")
        self._stop_event.set()
        self._thread.join(timeout=10) # Aguarda até 10 segundos pela thread
        if self._thread.is_alive():
            self.logger.warning("A thread do agendador não encerrou a tempo.")
        self.logger.info("Agendador parado.")
