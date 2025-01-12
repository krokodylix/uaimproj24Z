# Dockerfile

# Użyj oficjalnego obrazu Python jako bazowego
FROM python:3.11

# Ustaw zmienną środowiskową, aby Python działał w trybie niebuforowanym
ENV PYTHONUNBUFFERED=1

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik requirements.txt do katalogu roboczego
COPY docker_req.txt .

# Zainstaluj zależności
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r docker_req.txt

# Skopiuj cały kod aplikacji do katalogu roboczego
COPY app.py .
COPY main.py .
COPY db_models.py .

# Eksponuj port, na którym aplikacja będzie działać
EXPOSE 5000

# Ustaw zmienne środowiskowe z pliku .env (opcjonalnie)
# Możesz też przekazywać zmienne podczas uruchamiania kontenera
#COPY .env .env

# Komenda do uruchomienia aplikacji za pomocą Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
