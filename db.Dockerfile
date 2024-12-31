FROM postgres:15

RUN apt-get update && apt-get install -y \
    postgresql-server-dev-15 \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/pgvector/pgvector.git /pgvector && \
    cd /pgvector && \
    make && \
    make install

CMD ["postgres"]
