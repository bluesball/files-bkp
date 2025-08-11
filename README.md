# Sistema de Backup Automatizado

##  Visão Geral

Este é um sistema de backup robusto e automatizado, projetado para proteger dados importantes de forma eficiente. Ele oferece backups completos e incrementais, sincronização com a nuvem (Google Drive) e um agendador inteligente que garante a execução das tarefas mesmo após reinicializações do sistema.

### Funcionalidades

- **Backups Completos e Incrementais:** Otimiza o espaço de armazenamento fazendo backup apenas de arquivos novos ou modificados.
- **Sincronização com a Nuvem:** Envia automaticamente os backups para o Google Drive para maior segurança.
- **Agendamento Resiliente:** Um agendador baseado em estado garante que os backups sejam executados nos intervalos corretos, sem perder o controle devido a reinicializações.
- **Limpeza Automática:** Remove backups antigos com base em uma política de retenção configurável.
- **Interface de Linha de Comando (CLI):** Permite a execução de tarefas manuais, como backups imediatos e limpeza.
- **Containerização:** Suporte completo para Docker, facilitando a implantação e o isolamento do ambiente.

## Estrutura de Arquivos

```
backup_system/
├── main.py                  # Ponto de entrada principal (executa o agendador)
├── cli.py                   # Interface de linha de comando para tarefas manuais
├── config.py                # Gerenciamento de configurações
├── backup_manager.py        # Lógica principal de backup e limpeza
├── cloud_sync.py            # Sincronização com o Google Drive
├── scheduler.py             # Agendador de tarefas baseado em estado
├── health_check.py          # Script para verificação de saúde (usado pelo Docker)
├── config_avancada.json     # Arquivo de configuração do usuário
├── requirements.txt         # Dependências do Python
├── Dockerfile               # Define o contêiner da aplicação
└── docker-compose.yml       # Orquestra a implantação com Docker
```

## Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Conta do Google para acesso ao Google Drive
- (Opcional) Docker e Docker Compose

### Passos

1.  **Clonar o Repositório:**
    ```bash
    git clone <url_do_repositorio>
    cd backup_system
    ```

2.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar o Google Drive:**
    - Acesse o [Google Cloud Console](https://console.cloud.google.com) e crie um projeto.
    - Ative a API do Google Drive.
    - Crie credenciais do tipo "OAuth 2.0 Client ID" para uma "Aplicação de desktop".
    - Baixe o arquivo JSON de credenciais e salve-o como `credentials.json` na raiz do projeto.

4.  **Configurar o Sistema:**
    - Renomeie ou copie `config_avancada.json.example` para `config_avancada.json`.
    - Edite `config_avancada.json` e defina pelo menos:
      - `source_directory`: O diretório que você deseja fazer backup.
      - `local_backup_directory`: Onde os backups serão armazenados localmente.
      - `cloud_directory`: A pasta no Google Drive onde os backups serão enviados.

## Guia de Uso

### Modo Automatizado (Recomendado)

O modo principal de operação é o agendador, que executa todas as tarefas (backups, limpeza, sincronização) em segundo plano.

```bash
# Inicia o sistema em modo de agendamento
python main.py --action schedule

# Para rodar em segundo plano (daemon)
python main.py --action schedule --daemon
```

Na primeira vez que o sistema precisar acessar o Google Drive, ele abrirá uma janela do navegador para que você autorize o acesso. Um arquivo `token.json` será criado para armazenar a autorização para execuções futuras.

### Interface de Linha de Comando (CLI)

A CLI é útil para tarefas manuais.

```bash
# Executar um backup completo imediatamente
python cli.py backup --type full

# Executar um backup incremental imediatamente
python cli.py backup --type incremental

# Listar todos os backups já feitos
python cli.py list-backups

# Forçar a limpeza de backups antigos
python cli.py cleanup

# Ver um status rápido do sistema
python cli.py status
```

## Containerização com Docker

Para uma implantação isolada e consistente, use o Docker.

1.  **Construir a Imagem:**
    ```bash
    docker-compose build
    ```

2.  **Iniciar o Serviço:**
    Antes de iniciar, edite o `docker-compose.yml` e ajuste os `volumes` para apontar para os diretórios corretos em sua máquina host.
    ```bash
    docker-compose up -d
    ```

O contêiner executará o `main.py` em modo daemon automaticamente e cuidará de todas as tarefas de backup.
