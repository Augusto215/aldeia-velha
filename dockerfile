# Usar imagem oficial do Python
FROM python:3.10

# Definir diretório de trabalho no container
WORKDIR /app

# Copiar arquivos do projeto para dentro do container
COPY . /app/

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências do projeto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Criar pasta de mídia e estática
RUN mkdir -p /app/static /app/media

# Expõe a porta 8000 no container
EXPOSE 8001

# Comando para rodar o servidor Django
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "reservaApp.wsgi:application"]