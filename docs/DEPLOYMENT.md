# 🚢 Deployment Guide

The bot is designed to run in diverse environments, from local workstations to cloud-based containers.

---

## 💻 Desktop Deployment

Standard execution for users requiring a visual interface.
1.  Configure `.env`.
2.  Run `python main.py`.
3.  Ensure your OS has Graphical Support (X11 for Linux, Standard Windows/macOS).

---

## 🐳 Docker Deployment (Recommended for Servers)

Ideal for 24/7 scanning on VPS or Cloud instances.

### 1. Configuration
Modify the `docker-compose.yml` in the `config/` directory if you need specific volume mappings.

### 2. Build and Run
```bash
docker-compose up -d --build
```

### 3. Monitoring
Check container health and logs:
```bash
docker logs -f bybit-bot
```

---

## 🛡 Production Hardening

When deploying to a production server:
1.  **Database Backup**: Periodically back up the `bot_data.db` file.
2.  **Rate Limiting**: Our `bybit_service.py` handles 429 errors automatically, but ensure your API key has appropriate tier limits for high-frequency scanning.
3.  **Firewall**: If using the Telegram webhook (optional), ensure port 443 is open. Outbound traffic to Bybit and Telegram APIs must be allowed.

---

## 📂 Backup & Migration

To migrate the bot to a new server:
1.  Zip the root directory (excluding `venv` and `__pycache__`).
2.  Unzip on the target machine.
3.  Copy the existing `bot_data.db` to retain all logs, users, and settings.
4.  Restart the container or python process.
