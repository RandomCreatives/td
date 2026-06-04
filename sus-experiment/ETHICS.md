# SUS Ethical Framework

## 1. Informed Consent
Participants are presented with a clear consent script detailing the research nature of the project. Participation is strictly voluntary, and an age gate (21+) is enforced.

## 2. Anonymity & Privacy
- **No PII**: Telegram User IDs and phone numbers are never stored in the research database.
- **HMAC Anonymization**: Identities are hashed using HMAC-SHA256 with a 32-byte salt.
- **Salt Destruction**: The salt is rotated every 7 days, and the old salt is destroyed. This prevents long-term tracking of individuals.
- **Zero-Persistence**: Message content is relayed in real-time and never persisted to disk or long-term memory.

## 3. Ephemerality
All interactions are temporary. Temporary spaces auto-expire after 48 hours, and all associated metadata is cleared from live state (Redis).

## 4. User Agency
The `/burn` command provides an immediate "kill switch" for users to erase their current session and any active space.

## 5. Safety
A reporting system allows users to flag behavior. Reported accounts are shadow-banned, protecting the community without escalating conflict.

## 6. Research Intent
The system is designed for observation of aggregate patterns, not for individual profiling or behavioral manipulation. No recommendation engines or compatibility scores are used.
