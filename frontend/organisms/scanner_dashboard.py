# HEADER

# Organism: Scanner Dashboard
# Description: Displays scanner status and results.

# LIBRARIES
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QProgressBar, QLabel
from frontend.atoms.labeled_input import C_LabeledInput

# CLASSES
class C_ScannerDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Status Section
        self.status_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Scanner")
        self.stop_btn = QPushButton("Stop Scanner")
        self.progress = QProgressBar()
        self.status_label = QLabel("Status: Stopped")
        
        self.status_layout.addWidget(self.start_btn)
        self.status_layout.addWidget(self.stop_btn)
        self.status_layout.addWidget(self.progress)
        self.status_layout.addWidget(self.status_label)
        
        # Results Section
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(11)
        self.results_table.setHorizontalHeaderLabels([
            "Time", "Symbol", "Period", "Direction", "Price", 
            "Pattern", "Fib 0", "Fib 0.236", "Fib 0.382", "Fib 0.5", "Fib 1.0"
        ])
        
        self.layout.addLayout(self.status_layout)
        self.layout.addWidget(self.results_table)
