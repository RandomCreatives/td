# SUS - An Ephemeral Anonymous Social Experiment

SUS is a research-oriented social experiment hosted on Telegram. It provides a space where people can express what they need in the moment with zero fallout, allowing for the anonymized observation of hidden patterns of desire.

## Core Principles
- **Complete Anonymity**: No names, usernames, or persistent identifiers.
- **Ephemerality**: Conversations disappear after 48 hours.
- **Zero-Persistence**: Message content is never stored.
- **Safety First**: Immediate /burn and /report functionality.

## Tech Stack
- **Python 3.12+**
- **TDLib**: Telegram Database Library (via aiotdlib).
- **Redis**: Ephemeral state storage (TTL-based).
- **PostgreSQL**: Anonymized research aggregation.
- **APScheduler**: Periodic matching cycles and salt rotation.

## Setup Instructions

### 1. Prerequisites
- Docker and Docker Compose.
- Telegram API Credentials (API_ID and API_HASH) from [my.telegram.org](https://my.telegram.org).

### 2. Configuration
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your API_ID, API_HASH, and PHONE_NUMBER
```

### 3. Running with Docker
```bash
docker-compose up --build
```
On the first run, you will need to authenticate with Telegram (enter the code sent to your Telegram account).

### 4. Running Locally (for Development)
```bash
pip install .
# Start Redis and Postgres locally, then:
export API_ID=... API_HASH=... PHONE_NUMBER=...
python src/sus/main.py
```

## Commands
- `/start`: Begin onboarding.
- `/burn`: Immediate exit and data wipe.
- `/help`: Show ethos and available commands.
- `/report`: (In space) Report partner and end interaction.
- `/graduate`: (In space) Soft exit with reflection.
- `/silence`: (Available) Pause/resume matching cycle.

## Research Data
All research data is stored in PostgreSQL. User identities are anonymized using HMAC with a salt that rotates every 7 days. Once the salt is rotated, longitudinal tracking of the same user becomes impossible by design.
