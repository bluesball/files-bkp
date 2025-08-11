# cloud_sync.py
import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path

# Tente importar bibliotecas do Google; se falhar, o GoogleDriveProvider não funcionará.
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.http import MediaFileUpload
    import pickle
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

class CloudProvider(ABC):
    """Interface abstrata para provedores de armazenamento em nuvem."""
    @abstractmethod
    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Faz upload de um arquivo para a nuvem."""
        pass

    @abstractmethod
    def list_files(self, remote_directory: str) -> list:
        """Lista arquivos em um diretório remoto."""
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Exclui um arquivo remoto."""
        pass

class GoogleDriveProvider(CloudProvider):
    """Implementação para o Google Drive."""
    def __init__(self, config):
        if not GOOGLE_LIBS_AVAILABLE:
            raise ImportError("Bibliotecas do Google Drive não instaladas. Execute 'pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib'")
        
        self.config = config.get("cloud_credentials", {}).get("google_drive", {})
        self.token_path = Path(self.config.get("token_file", "token.json"))
        self.creds_path = Path(self.config.get("credentials_file", "credentials.json"))
        self.service = self._authenticate()
        self.logger = logging.getLogger(__name__)

    def _authenticate(self):
        """Autentica com a API do Google Drive usando OAuth 2.0."""
        creds = None
        if self.token_path.exists():
            with self.token_path.open('rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Erro ao renovar token do Google Drive: {e}")
                    creds = None # Força a re-autenticação
            
            if not creds:
                if not self.creds_path.exists():
                    self.logger.error(f"Arquivo de credenciais não encontrado: {self.creds_path}")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, ['https://www.googleapis.com/auth/drive.file']
                )
                creds = flow.run_local_server(port=0)

            with self.token_path.open('wb') as token:
                pickle.dump(creds, token)
        
        return build('drive', 'v3', credentials=creds)

    def _get_or_create_folder_id(self, remote_path: str) -> str:
        """Obtém o ID de uma pasta, criando-a se não existir."""
        if not self.service:
            return None
            
        parent_id = 'root'
        components = Path(remote_path).parts
        
        for component in components:
            query = f"name='{component}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
            response = self.service.files().list(q=query, fields="files(id)").execute()
            files = response.get('files', [])
            
            if not files:
                file_metadata = {
                    'name': component,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                parent_id = folder.get('id')
            else:
                parent_id = files[0].get('id')
        return parent_id

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        if not self.service:
            self.logger.error("Autenticação com o Google Drive falhou. Não é possível fazer o upload.")
            return False

        try:
            remote_dir = str(Path(remote_path).parent)
            folder_id = self._get_or_create_folder_id(remote_dir)
            if not folder_id:
                self.logger.error(f"Não foi possível encontrar ou criar a pasta remota: {remote_dir}")
                return False

            file_metadata = {'name': local_path.name, 'parents': [folder_id]}
            media = MediaFileUpload(str(local_path), resumable=True)
            
            self.service.files().create(
                body=file_metadata, media_body=media, fields='id'
            ).execute()
            
            self.logger.info(f"Upload para o Google Drive bem-sucedido: {local_path.name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro durante o upload para o Google Drive: {e}", exc_info=True)
            return False

    def list_files(self, remote_directory: str) -> list:
        # A ser implementado se necessário
        self.logger.warning("list_files não implementado para GoogleDriveProvider.")
        return []

    def delete_file(self, remote_path: str) -> bool:
        # A ser implementado se necessário
        self.logger.warning("delete_file não implementado para GoogleDriveProvider.")
        return False

class OneDriveProvider(CloudProvider):
    """Implementação para o OneDrive (placeholder)."""
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("O provedor OneDrive não está implementado.")

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        self.logger.warning("upload_file não implementado para OneDrive.")
        return False

    def list_files(self, remote_directory: str) -> list:
        return []

    def delete_file(self, remote_path: str) -> bool:
        return False

class CloudSyncManager:
    """Gerencia a sincronização de backups com um provedor de nuvem."""
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.provider = self._get_provider()

    def _get_provider(self) -> CloudProvider | None:
        """Retorna uma instância do provedor de nuvem com base na configuração."""
        provider_name = self.config.cloud_provider
        if provider_name == 'google_drive':
            try:
                return GoogleDriveProvider(self.config)
            except ImportError as e:
                self.logger.error(e)
                return None
        elif provider_name == 'onedrive':
            return OneDriveProvider(self.config)
        else:
            self.logger.info("Nenhum provedor de nuvem configurado.")
            return None

    def sync_to_cloud(self, local_backup_path_str: str) -> bool:
        """Sincroniza um arquivo de backup local com a nuvem."""
        if not self.provider:
            self.logger.error("Sincronização com a nuvem falhou: nenhum provedor disponível.")
            return False

        local_path = Path(local_backup_path_str)
        if not local_path.exists():
            self.logger.error(f"Arquivo de backup local não encontrado: {local_path}")
            return False

        remote_path = f"{self.config.get('cloud_directory', '/Backups')}/{local_path.name}"
        
        self.logger.info(f"Iniciando sincronização de {local_path.name} para a nuvem...")
        return self.provider.upload_file(local_path, remote_path)
