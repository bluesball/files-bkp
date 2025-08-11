# main.py
import sys
import argparse
import logging


def main():
    parser = argparse.ArgumentParser(description='Sistema de Backup')
    parser.add_argument('--config', default='backup_config.json',
                        help='Arquivo de configuração')
    parser.add_argument('--action', choices=['full', 'incremental', 'schedule', 'cleanup'],
                        default='schedule', help='Ação a executar')
    parser.add_argument('--daemon', action='store_true',
                        help='Executar como daemon')

    args = parser.parse_args()

    # Carregar configuração
    config = BackupConfig(args.config)

    # Inicializar componentes
    backup_manager = BackupManager(config)
    cloud_sync_manager = CloudSyncManager(config)

    try:
        if args.action == 'full':
            backup_path = backup_manager.perform_full_backup()
            if backup_path and cloud_sync_manager:
                cloud_sync_manager.sync_to_cloud(backup_path)

        elif args.action == 'incremental':
            backup_path = backup_manager.perform_incremental_backup()
            if backup_path and cloud_sync_manager:
                cloud_sync_manager.sync_to_cloud(backup_path)

        elif args.action == 'cleanup':
            backup_manager.cleanup_old_backups()

        elif args.action == 'schedule':
            scheduler = BackupScheduler(config, backup_manager, cloud_sync_manager)
            scheduler.start()

            if args.daemon:
                import signal

                def signal_handler(signum, frame):
                    logging.info("Parando agendador...")
                    scheduler.stop()
                    sys.exit(0)

                signal.signal(signal.SIGINT, signal_handler)
                signal.signal(signal.SIGTERM, signal_handler)

                # Manter processo rodando
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()
            else:
                print("Agendador iniciado. Pressione Ctrl+C para parar.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()

    except Exception as e:
        logging.error(f"Erro durante execução: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())