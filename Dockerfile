# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Impede que o Python grave arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Garante que a saída do Python seja exibida imediatamente
ENV PYTHONUNBUFFERED 1

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Cria um usuário não-root para executar a aplicação
RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

# Comando padrão para executar a aplicação
# Inicia o agendador em modo daemon por padrão.
CMD ["python", "main.py", "--action", "schedule", "--daemon"]
