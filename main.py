# ----- HEADER --------------------------------------------------
# File: main.py
# Description: Main entry point for the GUI application.

# ----- LIBRARY --------------------------------------------------
import sys
from PyQt6.QtWidgets import QApplication
from frontend.controller import C_Main_Window
from backend.core import config as M_Bybit

# ----- START --------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize Settings Cache
    M_Bybit.F_Get_Settings()
    
    window = C_Main_Window()
    window.show()
    sys.exit(app.exec())
