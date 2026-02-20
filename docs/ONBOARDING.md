# 📖 Onboarding & Setup Guide

Welcome to the **Bybit Intelligent Scanner Bot** development team. Follow this guide to set up your local environment and understand our standards.

---

## 🛠 Environmental Setup

### 1. Python Environment
We recommend using Python 3.11. Create a virtual environment to isolate dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\activate  # Windows
```

### 2. Dependencies
Install the required enterprise libraries:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
The bot requires a `.env` file for secure credential management.
**MANDATORY KEYS:**
- `BYBIT_MAIN_API_KEY`: Your Bybit V5 API Key.
- `BYBIT_MAIN_SECRET_KEY`: Your Bybit V5 API Secret.

---

## 📏 Structural Governance

Our project follows strict structural rules to prevent architectural entropy:

### Root Directory
- **Folders**: Maximum 5 (Current: `backend`, `frontend`, `config`, `docs`, `shared`).
- **Files**: Maximum 10 (Current: `main.py`, `headless_main.py`, `requirements.txt`, etc.).

### Subdirectories
- **Folders**: Maximum 10 per directory.
- **Files**: Maximum 15 per directory.

---

## ✍️ Coding Standards

### Naming Conventions
- **Files/Folders**: `snake_case`
- **Classes**: `C_Snake_Case` (e.g., `C_Main_Window`)
- **Functions**: `F_Snake_Case` (e.g., `F_Start_Scanner`)
- **Params**: `p_snake_case` (e.g., `p_symbol`)
- **Constants**: `SNAKE_CASE`

### File Regions
Every Python file must include the following regions:
- `HEADER`: File description and metadata.
- `LIBRARY`: Import statements.
- `VARIABLE`: Global/Module-level variables.
- `CLASS`: Class definitions.
- `FUNCTION`: Function definitions.
- `START`: Execution entry point (if applicable).

### Comments
- **English only**.
- **Single-line only**.
- Allowed only under region, class, or function headers. No inline comments.

---

## 🧪 Verification
After setup, run the database verification to ensure persistence is working:
```bash
python -c "from backend.core.database import init_db; init_db(); print('DB Initialized')"
```
