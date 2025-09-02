FROM postgres:15

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-server-dev-15 \
        build-essential \
        curl \
        ca-certificates && \
    update-ca-certificates && \
    curl -L https://github.com/pgvector/pgvector/archive/refs/tags/v0.7.4.tar.gz \
        | tar xz -C /tmp && \
    make -C /tmp/pgvector-0.7.4 && \
    make -C /tmp/pgvector-0.7.4 install && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

CMD ["postgres"]
