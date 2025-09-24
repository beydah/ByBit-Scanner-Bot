# ===== RULE ========================================================================================================

# -*- coding: utf-8 -*-

# ===== LIBRARY ========================================================================================================

from PyQt6.QtCore import QTimer as L_Timer, Qt as L_Qt, QDate as L_Date
from PyQt6.QtWidgets import (
    QWidget as L_Widget, QVBoxLayout as L_V_Box_Layout, QTabWidget as L_Tab_Widget, QLabel as L_Label, QPushButton as L_Push_Button,
    QTableWidget as L_Table_Widget, QGridLayout as L_Grid_Layout, QFormLayout as L_Form_Layout, QLineEdit as L_Line_Edit, QHeaderView as L_Header_View,
    QDateEdit as L_Date_Edit, QProgressBar as L_Progress_Bar, QTextEdit as L_Text_Edit, QGroupBox as L_Group_Box,
    QHBoxLayout as L_H_Box_Layout, QCheckBox as L_Check_Box, QComboBox as L_Combo_Box
)

from PyQt6.QtGui import QIcon as L_Icon, QFont as L_Font
import sys as L_SYS
import os as L_OS

from d_model import b_bybit as M_Bybit

# ===== VARIABLE ========================================================================================================

L_SYS.path.append(L_OS.path.dirname(L_OS.path.dirname(L_OS.path.abspath(__file__))))

# ===== CLASS ========================================================================================================

class C_Ui_Main_Window(object):
    def F_Setup_Ui(self, p_main_window):
        p_main_window.setObjectName("MainWindow")
        p_main_window.setWindowTitle("Manalive Bybit Bot")
        p_main_window.resize(1400, 900)
        self.centralwidget = L_Widget(p_main_window)
        self.mainLayout = L_V_Box_Layout(self.centralwidget)
        self.tabWidget = L_Tab_Widget(self.centralwidget)
        self.mainLayout.addWidget(self.tabWidget)
        self.F_Create_Dashboard_Tab()
        self.F_Create_Settings_Tab()
        self.F_Create_Users_Tab()
        self.F_Create_Logs_Tab()
        p_main_window.setCentralWidget(self.centralwidget)
        self.F_Apply_Stylesheet(p_main_window)

    def F_Create_Dashboard_Tab(self):
        self.dashboardTab = L_Widget()
        self.tabWidget.addTab(self.dashboardTab, "📊 Dashboard")
        layout = L_V_Box_Layout(self.dashboardTab)
        control_group = L_Group_Box("Scanner Control")
        control_layout = L_H_Box_Layout(control_group)
        self.scannerStatusLabel = L_Label("STOPPED")
        self.scannerStatusLabel.setAlignment(L_Qt.AlignmentFlag.AlignCenter)
        self.scannerStatusLabel.setObjectName("statusLabel")
        self.scannerStatusLabel.setFont(L_Font("Segoe UI", 16, L_Font.Weight.Bold))
        self.startButton = L_Push_Button("Start Scanner")
        self.stopButton = L_Push_Button("Stop Scanner")
        self.startButton.setMinimumHeight(40)
        self.stopButton.setMinimumHeight(40)
        control_layout.addWidget(self.scannerStatusLabel)
        control_layout.addWidget(self.startButton)
        control_layout.addWidget(self.stopButton)
        layout.addWidget(control_group)
        activity_group = L_Group_Box("Recent Activities")
        activity_layout = L_V_Box_Layout(activity_group)
        self.activityTable = L_Table_Widget()
        self.activityTable.setColumnCount(10)
        self.activityTable.setHorizontalHeaderLabels([
            "Symbol", "Volume", "Period", "Price", "Pattern", "Fib(0.0)", "Fib(0.01)", "Fib(0.236)", "Fib(0.382)", "Fib(1.0)"
        ])

        self.activityTable.horizontalHeader().setSectionResizeMode(L_Header_View.ResizeMode.Stretch)
        self.activityTable.setMaximumHeight(120)
        activity_layout.addWidget(self.activityTable)
        layout.addWidget(activity_group)
        status_group = L_Group_Box("Scanner Status")
        status_layout = L_H_Box_Layout(status_group)
        stats_layout = L_V_Box_Layout()
        self.totalSymbolsLabel = L_Label("Total Symbols: 0")
        self.scannedSymbolsLabel = L_Label("Scanned Symbols: 0")
        self.remainingSymbolsLabel = L_Label("Remaining Symbols: 0")
        self.foundSignalsLabel = L_Label("Signals Found: 0")
        self.currentSymbolLabel = L_Label("Current Symbol: -")
        self.scanProgressLabel = L_Label("Progress: %0")
        for label in [self.totalSymbolsLabel, self.scannedSymbolsLabel, self.remainingSymbolsLabel, 
                     self.foundSignalsLabel, self.currentSymbolLabel, self.scanProgressLabel]:
            label.setFont(L_Font("Segoe UI", 10))
            stats_layout.addWidget(label)

        self.scanProgressBar = L_Progress_Bar()
        self.scanProgressBar.setMinimum(0)
        self.scanProgressBar.setMaximum(100)
        self.scanProgressBar.setValue(0)
        self.scanProgressBar.setFormat("%p% Complete")
        stats_layout.addWidget(self.scanProgressBar)
        status_layout.addLayout(stats_layout)
        status_layout.addStretch()
        layout.addWidget(status_group)
        signals_group = L_Group_Box("Found Signals")
        signals_layout = L_V_Box_Layout(signals_group)
        self.signalsTable = L_Table_Widget()
        self.signalsTable.setColumnCount(5)
        self.signalsTable.setHorizontalHeaderLabels(["Time", "Symbol", "Period", "Direction", "Price"])
        self.signalsTable.horizontalHeader().setSectionResizeMode(L_Header_View.ResizeMode.Stretch)
        self.signalsTable.setMaximumHeight(200)
        signals_layout.addWidget(self.signalsTable)
        layout.addWidget(signals_group)

    def F_Create_Logs_Tab(self):
        self.logsTab = L_Widget()
        self.tabWidget.addTab(self.logsTab, "📄 Logs")
        layout = L_Grid_Layout(self.logsTab)
        self.logDateEdit = L_Date_Edit(L_Date.currentDate())
        self.logDateEdit.setCalendarPopup(True)
        self.logTypeCombo = L_Line_Edit("error, alert, transaction")
        self.fetchLogsButton = L_Push_Button("Fetch Logs")
        filter_layout = L_Grid_Layout()
        filter_layout.addWidget(L_Label("Date:"), 0, 0)
        filter_layout.addWidget(self.logDateEdit, 0, 1)
        filter_layout.addWidget(L_Label("Log Type:"), 0, 2)
        filter_layout.addWidget(self.logTypeCombo, 0, 3)
        filter_layout.addWidget(self.fetchLogsButton, 0, 4)
        layout.addLayout(filter_layout, 0, 0)
        self.logsTable = L_Table_Widget()
        self.logsTable.setColumnCount(3)
        self.logsTable.setHorizontalHeaderLabels(["Time", "Title", "Description"])
        self.logsTable.horizontalHeader().setSectionResizeMode(L_Header_View.ResizeMode.Stretch)
        self.logsTable.horizontalHeader().setSectionResizeMode(2, L_Header_View.ResizeMode.Interactive)
        layout.addWidget(self.logsTable, 1, 0)

    def F_Create_Settings_Tab(self):
        self.settingsTab = L_Widget()
        self.tabWidget.addTab(self.settingsTab, "⚙️ Settings")
        layout = L_Form_Layout(self.settingsTab)
        self.settings_inputs = {}
        setting_keys = [
            "parity", "min_leverage", "min_volume", 
            "zigzag_period", "wait_time"
        ]

        for key in setting_keys:
            self.settings_inputs[key] = L_Line_Edit()
            layout.addRow(L_Label(f"{key.replace('_', ' ').title()}:"), self.settings_inputs[key])

        self.settings_inputs["period_1"] = L_Combo_Box()
        self.settings_inputs["period_2"] = L_Combo_Box()
        layout.addRow(L_Label("Period 1:"), self.settings_inputs["period_1"])
        layout.addRow(L_Label("Period 2:"), self.settings_inputs["period_2"])
        self.saveSettingsButton = L_Push_Button("Save Settings")
        layout.addRow(self.saveSettingsButton)
        self._settings_updating = False
        self.settings_timer = L_Timer()
        self.settings_timer.timeout.connect(self.F_Update_Settings_From_Model)
        self.settings_timer.start(3000)

    def F_Update_Settings_From_Model(self):
        if self._settings_updating: return
        settings = M_Bybit.F_Get_Settings()
        for key in ["parity", "min_leverage", "min_volume", "zigzag_period", "wait_time"]:
            if key in self.settings_inputs: self.settings_inputs[key].setText(str(settings.get(key, "")))

        for period_key in ["period_1", "period_2"]:
            if period_key in self.settings_inputs:
                combo: L_Combo_Box = self.settings_inputs[period_key]
                value = settings.get(period_key, "")
                idx = combo.findText(value)
                if idx == -1 and value:
                    combo.addItem(value)
                    idx = combo.findText(value)

                if idx != -1: combo.setCurrentIndex(idx)

    def F_Create_Users_Tab(self):
        self.usersTab = L_Widget()
        self.tabWidget.addTab(self.usersTab, "👥 Users")
        main_layout = L_H_Box_Layout(self.usersTab)
        list_group = L_Group_Box("User List")
        list_layout = L_V_Box_Layout(list_group)
        self.usersTable = L_Table_Widget()
        self.usersTable.setColumnCount(4)
        self.usersTable.setHorizontalHeaderLabels(["User ID", "Username", "Admin?", "Active?"])
        self.usersTable.horizontalHeader().setSectionResizeMode(L_Header_View.ResizeMode.Stretch)
        self.usersTable.setSelectionBehavior(L_Table_Widget.SelectionBehavior.SelectRows)
        self.usersTable.setEditTriggers(L_Table_Widget.EditTrigger.NoEditTriggers)
        self.usersTable.verticalHeader().setVisible(False)
        list_layout.addWidget(self.usersTable)
        main_layout.addWidget(list_group, 3)
        action_panel = L_Widget()
        action_layout = L_V_Box_Layout(action_panel)
        action_layout.setContentsMargins(0, 0, 0, 0)
        form_group = L_Group_Box("User Operations")
        form_layout = L_Form_Layout(form_group)
        self.userInput_chatId = L_Line_Edit()
        self.userInput_chatId.setPlaceholderText("Telegram Chat ID")
        self.userInput_userName = L_Line_Edit()
        self.userInput_userName.setPlaceholderText("Username")
        form_layout.addRow(L_Label("Chat ID:"), self.userInput_chatId)
        form_layout.addRow(L_Label("Name:"), self.userInput_userName)
        self.user_isAdminCheck = L_Check_Box("Admin Privileges")
        self.user_isActiveCheck = L_Check_Box("Account Active")
        self.user_isActiveCheck.setChecked(True)
        checkbox_layout = L_H_Box_Layout()
        checkbox_layout.addWidget(self.user_isAdminCheck)
        checkbox_layout.addWidget(self.user_isActiveCheck)
        form_layout.addRow(checkbox_layout)
        button_layout = L_H_Box_Layout()
        self.user_addButton = L_Push_Button("Add")
        self.user_addButton.setIcon(L_Icon.fromTheme("list-add"))
        self.user_updateButton = L_Push_Button("Update")
        self.user_deleteButton = L_Push_Button("Delete")
        self.user_deleteButton.setIcon(L_Icon.fromTheme("list-remove"))
        button_layout.addWidget(self.user_addButton)
        button_layout.addWidget(self.user_updateButton)
        button_layout.addWidget(self.user_deleteButton)
        form_layout.addRow(button_layout)
        action_layout.addStretch()
        main_layout.addWidget(action_panel, 1)

    def F_Apply_Stylesheet(self, p_app):
        stylesheet = """
            QMainWindow {
                background-color: #2c3e50;
            }
            QTabWidget::pane {
                border-top: 2px solid #34495e;
            }
            QTabBar::tab {
                background: #34495e;
                color: #ecf0f1;
                padding: 10px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #46627f;
                border: 1px solid #7f8c8d;
            }
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                background-color: #34495e;
                border: 1px solid #7f8c8d;
                gridline-color: #7f8c8d;
            }
            QHeaderView::section {
                background-color: #46627f;
                color: #ecf0f1;
                padding: 5px;
                border: 1px solid #7f8c8d;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QLineEdit, QDateEdit {
                background-color: #34495e;
                border: 1px solid #7f8c8d;
                padding: 5px;
                border-radius: 4px;
            }
            QLabel {
                padding: 5px;
            }
            QTextEdit {
                background-color: #34495e;
                border: 1px solid #7f8c8d;
                color: #ecf0f1;
            }
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
            #statusLabel {
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c; /* Red - Stopped */
            }
            #statusLabel[status="running"] {
                color: #2ecc71; /* Green - Running */
            }
            #statusLabel[status="waiting"] {
                color: #f39c12; /* Yellow - Waiting */
            }
        """
        p_app.setStyleSheet(stylesheet) 
        