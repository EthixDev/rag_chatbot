FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY . /app

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8080

# Start the application: Serve static files on port 8001 and the app on port 8080
CMD ["bash", "-c", "\
    python -m http.server --directory /app/staticfiles 8001 & \
    python manage.py migrate && \
    daphne -b 0.0.0.0 -p 8080 rag_chatbot.asgi:application"]
