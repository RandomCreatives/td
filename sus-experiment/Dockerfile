FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    gperf \
    libssl-dev \
    zlib1g-dev \
    php-cli \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install .

COPY . .

CMD ["python", "src/sus/main.py"]
