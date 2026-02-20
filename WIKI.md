# 📔 Project Wiki

Welcome to the internal documentation for the **Bybit Intelligent Scanner Bot**.

---

## 🛠 1. Development Environment

### Technology Stack
- **Language**: Python 3.11
- **GUI Framework**: PyQt6
- **Database**: SQLite 3
- **SDK**: Pybit (Bybit Unified Trading V5)
- **Containerization**: Docker & Docker Compose

### Structural Governance
We enforce a maximum of:
- 5 folders in `root/`
- 10 files in `root/`
- 10 folders per subdirectory
- 15 files per subdirectory

---

## 🏗 2. Architecture Deep-Dive

### Backend Domains
- `backend/market`: Handles API requests, rate limiting backoff, and market data normalization.
- `backend/trade`: Contains the core Fibonacci and ZigZag signal generation logic.
- `backend/notification`: Manages Telegram bot interactions and automated alerts.
- `backend/core`: The infrastructure layer (Database, Configuration, Validation).

### Frontend Atoms
UI components are built using **Atomic Design**:
- `atoms`: Buttons, Labels, Icons.
- `molecules`: Form inputs, search fields.
- `organisms`: Live tables, dashboard widgets.
- `templates`: Window layouts.

---

## 🔐 3. Security & Rate Limiting

### Secret Management
Secrets are **NEVER** stored in code. The `config.py` module validates that `BYBIT_MAIN_API_KEY` and `BYBIT_MAIN_SECRET_KEY` are present in the environment before any service starts.

### Backoff Strategy
The bot implements a **Centralized Rate Limit Handler** in `bybit_service.py`. When a `429` error is detected, the bot automatically:
1. Pauses the offending thread.
2. Performs exponential backoff.
3. Logs the event for audit.

---

## 🐳 4. Deployment

### Docker
The bot is fully containerized. Use the `config/Dockerfile` to build an image that can be deployed anywhere.
```bash
docker build -f config/Dockerfile -t bybit-bot .
```

---

## ❓ 5. Troubleshooting

**Q: Bot fails to start with "CRITICAL: Missing environment variables"**
A: Ensure your `.env` file is in the root directory and contains the keys specified in the README.

**Q: GUI doesn't open on Linux.**
A: Ensure you have `libxcb` and other Qt6 dependencies installed, or run in headless mode.
