FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY scripts ./scripts
COPY frontend ./frontend
COPY learner_engine.py vector_index.py knowledge_graph.py ./

# Copy seed knowledge database into immutable location (never directly to volume path)
RUN mkdir -p /app/seed
COPY gpat_knowledge.db /app/seed/gpat_knowledge.db

# Copy and prepare entrypoint
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Persistent mount point for volume
RUN mkdir -p /app/data /app/data/backups

ENV PORT=8000
ENV ENVIRONMENT=production
ENV DB_PATH=/app/data/gpat_knowledge.db
ENV BACKUP_DIR=/app/data/backups

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
