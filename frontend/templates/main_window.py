# HEADER
# Template: Main Window Layout
# Description: Defines the base structure of the application window.

# LIBRARIES
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt

# CLASSES
class C_MainWindowLayout(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bybit Trading Bot")
        self.resize(1200, 800)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Pages will be added to tabs by the controller
