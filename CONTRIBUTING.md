# Contributing to ByBit Trading Bot

First off, thank you for considering contributing to ByBit Trading Bot! It's people like you that make the open source community such a great place to learn, inspire, and create.

## 📋 Table of Contents

1. [Code of Conduct](#-code-of-conduct)
2. [Getting Started](#-getting-started)
3. [How to Contribute](#-how-to-contribute)
4. [Reporting Bugs](#-reporting-bugs)
5. [Suggesting Enhancements](#-suggesting-enhancements)
6. [Code Style and Standards](#-code-style-and-standards)
7. [Pull Request Process](#-pull-request-process)
8. [Development Setup](#-development-setup)
9. [License](#-license)

## ✨ Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/ByBit-Scanner-Bot.git
   cd ByBit-Scanner-Bot
   ```
3. **Set up** the development environment (see [Development Setup](#-development-setup))
4. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💡 How to Contribute

### 🐛 Reporting Bugs

1. **Check** if the bug has already been reported in the [Issues](https://github.com/beydah/ByBit-Scanner-Bot/issues) section
2. If not, **open a new issue** with a clear title and description
3. Include **steps to reproduce** the issue
4. Add **screenshots** or **logs** if applicable
5. Specify your **environment** (OS, Python version, etc.)

### 💡 Suggesting Enhancements

1. **Check** if the enhancement has already been suggested
2. **Open an issue** with a clear title and description
3. Explain why this enhancement would be useful
4. Include any relevant **screenshots** or **mockups**

## 🛠 Development Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/beydah/ByBit-Scanner-Bot.git
   cd ByBit-Scanner-Bot
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix or MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

5. **Run the application**
   ```bash
   python main.py
   ```

## 📝 Code Style and Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep lines under 120 characters
- Use meaningful variable and function names
- Add comments to explain complex logic

## 🔄 Pull Request Process

1. Fork the repository and create your branch from `main`
2. Make your changes
3. Add tests if applicable
4. Update the documentation
5. Ensure the test suite passes
6. Make sure your code lints
7. Submit the pull request

### Pull Request Guidelines

- Fill in the pull request template
- Reference any related issues
- Include screenshots or animated GIFs if your changes affect the UI
- Follow the pull request template guidelines

## 📖 Documentation

- Keep the README.md up to date with any changes
- Add comments to explain complex sections of code
- Update the CHANGELOG.md with notable changes

## 📜 License

By contributing, you agree that your contributions will be licensed under its MIT License.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped improve this project
- Special thanks to ByBit for their API
- Inspired by TradingView's technical analysis tools

---

Thank you for your interest in contributing to ByBit Trading Bot! Your contributions help make it better for everyone.
