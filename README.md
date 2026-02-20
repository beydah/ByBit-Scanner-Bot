# 🦅 Bybit Intelligent Scanner Bot

<div align="center">
  <img src="https://img.shields.io/badge/Status-Enterprise%20Ready-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.11+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Modern-Atomic%20Design-orange" alt="Design">
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey" alt="Database">
</div>

---

## 📖 Introduction

The **Bybit Intelligent Scanner Bot** is a high-performance, enterprise-grade market analysis tool built for traders who demand precision, speed, and reliability. Leveraging the **Bybit Unified Trading SDK (V5)**, this bot performs parallel technical analysis across hundreds of symbols simultaneously.

## 🚀 Architectural Pillars

This project adheres to strict **Structural Governance** and **Modern Engineering Patterns**:

- 🏗 **Domain-Driven Design (Backend)**: Decoupled domains for Market, Trade, Notification, and Logger.
- ⚛ **Atomic Design (Frontend)**: Highly reusable UI components built on PyQt6.
- 🔐 **Zero-Secret Policy**: Strict environment variable governance for API keys.
- 🧵 **Multi-Threaded Engine**: Optimized `ThreadPoolExecutor` prevents UI blocking and maximizes throughput.
- 🗄 **SQL Persistence**: Reliable SQLite layer replacing fragile flat-file storage.

---

## 📂 Structural Overview

To ensure maintainability, the project follows a strict **5-Folder Governance Rule**:

```text
root/
├── 📁 backend/       # Pure logic, models, and domain services
├── 📁 frontend/      # Atomic UI components and views
├── 📁 config/        # Environment and Docker infrastructure
├── 📁 docs/          # Technical guides and wiki
└── 📁 data/          # Persistent databases and local state
```

---

## ⚙️ Installation & Setup

1. **Clone & Enter**
   ```bash
   git clone https://github.com/youruser/Bybit-Scanner-Bot.git
   cd Bybit-Scanner-Bot
   ```

2. **Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Window: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure**
   Create a `.env` in the root and add your Bybit V5 credentials:
   ```env
   # Bybit API Credentials
   BYBIT_MAIN_API_KEY=YOUR_API_KEY_HERE
   BYBIT_MAIN_SECRET_KEY=YOUR_SECRET_KEY_HERE

   # Telegram Configuration
   TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
   TELEGRAM_USER_ID=YOUR_TELEGRAM_ID_HERE
   ```

---

## 🏃 Running the Bot

### 🖥 GUI Mode
Default desktop interaction with real-time tables and dashboard.
```bash
python main.py
```

### 🤖 Headless Mode
Optimized for VPS/Docker deployment with Telegram signaling only.
```bash
python headless_main.py
```

---

## 📚 Resources

| Resource                           | Description                                       |
| :--------------------------------- | :------------------------------------------------ |
| [LICENSE](LICENSE)                 | MIT License terms.                                |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Standardized coding and structural rules.         |
| [SECURITY.md](SECURITY.md)         | Vulnerability reporting procedure.                |

---

## ⚖️ Disclaimer

Trading cryptocurrencies involves significant risk. This bot is provided as-is for educational and analysis purposes. The developers are not responsible for financial losses.

<p align="center"><i>Built with 💙 for the Algorithmic Trading Community.</i></p>
