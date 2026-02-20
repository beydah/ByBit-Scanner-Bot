# HEADER

# Atom: Labeled Input
# Description: A reusable input field with a label.

# LIBRARIES
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit

# CLASSES
class C_LabeledInput(QWidget):
    def __init__(self, p_label_text, p_default_value=""):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(p_label_text)
        self.input = QLineEdit(str(p_default_value))
        
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        
    def F_Get_Text(self):
        return self.input.text()
        
    def F_Set_Text(self, p_text):
        self.input.setText(str(p_text))
