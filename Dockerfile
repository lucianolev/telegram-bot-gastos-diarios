# Usamos una imagen liviana de Python
FROM python:3.14-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código y la llave
COPY . .

# Cloud Run pasa el puerto por la variable de entorno PORT (por defecto 8080)
# Usamos gunicorn como servidor de producción
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
