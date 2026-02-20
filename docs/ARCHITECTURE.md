# 🏗 Architecture Overview

The Bybit Intelligent Scanner Bot is built on a decoupled, modular architecture designed for high throughput and long-term maintainability.

---

## 🧬 Frontend: Atomic Design

The UI is decomposed following the **Atomic Design** methodology to ensure high reusability and isolation of concerns.

### Hierarchy:
1.  **Atoms**: Pure functional widgets (Buttons, Inputs, Labels).
2.  **Molecules**: Simple groups (Labeled Inputs, Search Bars).
3.  **Organisms**: Complex feature blocks (Scanner Dashboard, Log Table).
4.  **Templates**: Layout structures (Main Window Layout).
5.  **Pages**: High-level views (Dashboard Page, Settings Page).

---

## ⚙️ Backend: Domain-Driven Design (DDD)

The backend is structured into self-contained domains. Each domain is responsible for its own logic and state.

### Domains:
- **Core**: Infrastructure, Database (SQLite), Global Settings.
- **Market**: Bybit API Integration, SDK Governance, Rate Limiting.
- **Trade**: Strategy implementation, Fibonacci calculations, Signal generation.
- **Notification**: Telegram Bot API handling, User privilege management.
- **Logger**: Centralized audit trails and exception handling.

---

## 🧪 Data Flow

1.  **Input**: User starts scanner via GUI (Frontend).
2.  **Process**: `ScannerEngine` (Market Domain) spawns threads via `ThreadPoolExecutor`.
3.  **Analysis**: `SignalLogic` (Trade Domain) calculates technical indicators.
4.  **Persistence**: Results and logs are saved to SQLite via `Database` (Core Domain).
5.  **Output**: Signals are sent via `TelegramService` (Notification Domain) and displayed in the UI.

---

## 🔒 Security Posture

- **Zero-Secret Codebase**: No credentials stored in JSON or Python files.
- **Environment Isolation**: Uses `.env` for production keys.
- **Error Boundaries**: Centralized error decorators prevent system crashes on individual thread failures.
