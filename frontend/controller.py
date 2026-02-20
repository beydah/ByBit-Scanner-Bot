# ----- HEADER --------------------------------------------------

# File: controller.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import sys as L_SYS
import time as L_Time
from datetime import datetime as L_Date

from PyQt6.QtWidgets import QApplication as L_Application, QMainWindow as L_Main_Window, QTableWidgetItem as L_Table_Widget_Item, QMessageBox as L_Message_Box
from PyQt6.QtCore import QThread as L_Thread, pyqtSignal as L_Signal, QTimer as L_Timer

from frontend.view import C_Ui_Main_Window as V_Main
from backend.market import scanner_engine as S_Scanner
from backend.trade.signal_queue import Signal_Que as S_Signal_Que
from backend.core import config as M_Bybit
from backend.notification import user_repository as M_Telegram
from backend.logger import log_service as M_Log

# ----- CLASS --------------------------------------------------

class C_Scanner_Status_Thread(L_Thread):
    # DESC: Thread that continuously monitors the scanner status
    status_updated = L_Signal(dict)
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                status_info = S_Scanner.F_Get_Status_Scanner()
                self.status_updated.emit(status_info)
                L_Time.sleep(1)  # Update every second
            except Exception as e:
                print(f"Status thread error: {e}")
                L_Time.sleep(5)
    
    def stop(self): self.running = False

class C_Main_Window(L_Main_Window):
    def __init__(self):
        super().__init__()
        self.ui = V_Main()
        self.ui.F_Setup_Ui(self)
        self.scanner_stats = {
            'total_symbols': 0,
            'scanned_symbols': 0,
            'remaining_symbols': 0,
            'found_signals': 0,
            'current_symbol': '-',
            'progress_percent': 0
        }
        
        self._last_status = None  # Store the last status
        self.status_thread = C_Scanner_Status_Thread()
        self.status_thread.status_updated.connect(self.update_scanner_status_detailed)
        self.status_thread.start()
        self.setup_timers()
        self.connect_signals()
        self.load_initial_data()

    def setup_timers(self):
        # DESC: Set up timers for periodic updates
        self.scanner_timer = L_Timer()
        self.scanner_timer.timeout.connect(self.update_scanner_progress)
        self.scanner_timer.start(2000)
        self.signal_timer = L_Timer()
        self.signal_timer.timeout.connect(self.process_signal_queue)
        self.signal_timer.start(1000)

    def connect_signals(self):
        # DESC: Connects signals like button clicks to their respective functions (slots).
        self.ui.startButton.clicked.connect(self.start_scanner)
        self.ui.stopButton.clicked.connect(self.stop_scanner)
        self.ui.saveSettingsButton.clicked.connect(self.save_settings)
        self.ui.fetchLogsButton.clicked.connect(self.load_logs)
        self.ui.user_addButton.clicked.connect(self._user_add)
        self.ui.user_updateButton.clicked.connect(self._user_update)
        self.ui.user_deleteButton.clicked.connect(self._user_delete)
        self.ui.usersTable.itemSelectionChanged.connect(self._user_selection_changed)
        
    def load_initial_data(self):
        # DESC: Loads data when the application first starts.
        self.load_settings()
        self.load_users()
        self.load_logs()
        self.update_scanner_status()

    def add_activity_log(self, message): pass

    def update_scanner_progress(self):
        # DESC: Updates the scanner's progress status
        try:
            if hasattr(S_Scanner, 'symbols') and S_Scanner.symbols:
                total = len(S_Scanner.symbols)
                if hasattr(S_Scanner, 'current_index'):
                    scanned = S_Scanner.current_index
                    remaining = total - scanned
                    progress = int((scanned / total) * 100) if total > 0 else 0
                    self.scanner_stats.update({
                        'total_symbols': total,
                        'scanned_symbols': scanned,
                        'remaining_symbols': remaining,
                        'progress_percent': progress
                    })
                    
                    self.update_scanner_stats_display()
        except Exception as e: print(f"Progress update error: {e}")

    def update_scanner_stats_display(self):
        # DESC: Displays scanner statistics in the interface
        self.ui.totalSymbolsLabel.setText(f"Total Symbols: {self.scanner_stats['total_symbols']}")
        self.ui.scannedSymbolsLabel.setText(f"Scanned Symbols: {self.scanner_stats['scanned_symbols']}")
        self.ui.remainingSymbolsLabel.setText(f"Remaining Symbols: {self.scanner_stats['remaining_symbols']}")
        self.ui.foundSignalsLabel.setText(f"Found Signals: {self.scanner_stats['found_signals']}")
        self.ui.currentSymbolLabel.setText(f"Current Symbol: {self.scanner_stats['current_symbol']}")
        self.ui.scanProgressLabel.setText(f"Progress: %{self.scanner_stats['progress_percent']}")
        self.ui.scanProgressBar.setValue(self.scanner_stats['progress_percent'])

    def update_scanner_status_detailed(self, status_info):
        """Updates the detailed status of the scanner"""
        status = status_info.get("status", "stopped").upper()
        self.ui.scannerStatusLabel.setText(status)
        if status == "RUNNING":
            self.ui.scannerStatusLabel.setProperty("status", "running")
            if self._last_status == "WAITING": self.ui.activityTable.setRowCount(0)

        elif status == "WAITING": self.ui.scannerStatusLabel.setProperty("status", "waiting")
        else: self.ui.scannerStatusLabel.setProperty("status", "stopped")
        self.ui.scannerStatusLabel.style().polish(self.ui.scannerStatusLabel)
        if status in ["RUNNING", "WAITING"]:
            self.scanner_stats.update({
                'total_symbols': status_info.get('total_symbols', 0),
                'scanned_symbols': status_info.get('scanned_symbols', 0),
                'remaining_symbols': status_info.get('total_symbols', 0) - status_info.get('scanned_symbols', 0),
                'found_signals': status_info.get('found_signals', 0),
                'current_symbol': status_info.get('current_symbol', '-'),
                'progress_percent': int((status_info.get('scanned_symbols', 0) / max(status_info.get('total_symbols', 1), 1)) * 100)
            })
            
            current_price = status_info.get('current_price', '-')
            zigzag_level = status_info.get('last_zigzag_level', '-')
            fibo_level = status_info.get('last_fibo_level', '-')
            if status == "RUNNING" and current_price != "-":
                activity_msg = f"Scanning: {status_info.get('current_symbol', '-')} | Period: {status_info.get('current_period', '-')} | Price: {current_price}"
                if zigzag_level != "-": activity_msg += f" | ZigZag: {zigzag_level}"
                if fibo_level != "-": activity_msg += f" | Fibo: {fibo_level}"
            
            last_signal_time = status_info.get('last_signal_time')
            if last_signal_time and last_signal_time != self.scanner_stats.get('last_signal_time'):
                self.scanner_stats['last_signal_time'] = last_signal_time
            
            self.update_scanner_stats_display()
        self._last_status = status

    def start_scanner(self):
        S_Scanner.F_Start_Scanner()
        self.update_scanner_status()

    def stop_scanner(self):
        S_Scanner.F_Stop_Scanner()
        self.update_scanner_status()
        self.scanner_stats.update({
            'scanned_symbols': 0,
            'remaining_symbols': 0,
            'current_symbol': '-',
            'progress_percent': 0
        })

        self.update_scanner_stats_display()

    def update_scanner_status(self):
        status_info = S_Scanner.F_Get_Status_Scanner()
        status = status_info.get("status", "stopped").upper()
        self.ui.scannerStatusLabel.setText(status)
        self.ui.scannerStatusLabel.setProperty("status", "running" if status == "RUNNING" else "stopped")
        self.ui.scannerStatusLabel.style().polish(self.ui.scannerStatusLabel)
        print(f"Scanner status updated: {status}")

    def add_signal_to_table(self, signal_data):
        # DESC: Adds a new signal to the table when found
        stop_loss = signal_data.get('stop_loss', 0)
        take_profit = signal_data.get('take_profit', 0)
        if stop_loss == 0 or stop_loss == '0' or take_profit == 0 or take_profit == '0': return
        row_position = self.ui.signalsTable.rowCount()
        self.ui.signalsTable.insertRow(row_position)
        self.ui.signalsTable.setItem(row_position, 0, L_Table_Widget_Item(str(signal_data.get('time', ''))))
        self.ui.signalsTable.setItem(row_position, 1, L_Table_Widget_Item(str(signal_data.get('symbol', ''))))
        self.ui.signalsTable.setItem(row_position, 2, L_Table_Widget_Item(str(signal_data.get('period', ''))))
        self.ui.signalsTable.setItem(row_position, 3, L_Table_Widget_Item(str(signal_data.get('direction', ''))))
        self.ui.signalsTable.setItem(row_position, 4, L_Table_Widget_Item(str(signal_data.get('price', ''))))
        if self.ui.signalsTable.rowCount() > 100: self.ui.signalsTable.removeRow(0)
        self.scanner_stats['found_signals'] += 1
        self.update_scanner_stats_display()

    def load_settings(self):
        # DESC: Loads settings and period list
        settings = M_Bybit.F_Get_Settings()
        periods = M_Bybit.F_Get_Period()
        period_keys = list(periods.keys())
        self.ui.settings_inputs["period_1"].clear()
        self.ui.settings_inputs["period_2"].clear()
        self.ui.settings_inputs["period_1"].addItems(period_keys)
        self.ui.settings_inputs["period_2"].addItems(period_keys)
        if settings.get("period_1") in period_keys: self.ui.settings_inputs["period_1"].setCurrentText(settings.get("period_1"))
        if settings.get("period_2") in period_keys: self.ui.settings_inputs["period_2"].setCurrentText(settings.get("period_2"))
        for key, widget in self.ui.settings_inputs.items():
            if key not in ["period_1", "period_2"]: widget.setText(str(settings.get(key, "")))
        
        print("Settings loaded into the interface.")

    def save_settings(self):
        # DESC: Saves the settings
        settings_to_save = {}
        settings_to_save["p_period_1"] = self.ui.settings_inputs["period_1"].currentText()
        settings_to_save["p_period_2"] = self.ui.settings_inputs["period_2"].currentText()
        for key, widget in self.ui.settings_inputs.items():
            if key not in ["period_1", "period_2"]:
                value = widget.text()
                if key in ["min_leverage", "min_volume", "zigzag_period", "wait_time"]:
                    try: value = int(value)
                    except ValueError:
                        L_Message_Box.warning(self, "Invalid Value", f"Please enter a numeric value for {key.replace('_', ' ').title()}.")
                        return

                settings_to_save[f"p_{key}"] = value
        
        if M_Bybit.F_Update_Settings(**settings_to_save): L_Message_Box.information(self, "Success", "Settings saved successfully.")
        else: L_Message_Box.critical(self, "Error", "An error occurred while saving settings.")

    def load_logs(self):
        self._delete_old_logs(days=5)
        log_type_str = self.ui.logTypeCombo.text()
        log_types = [t.strip() for t in log_type_str.split(',') if t.strip()]
        date = self.ui.logDateEdit.date().toString("yyyy-MM-dd")
        self.ui.logsTable.setRowCount(0)
        all_logs = M_Log.F_Get_Log(date)
        display_logs = []
        for log_type, logs in all_logs.items():
            if log_type in log_types:
                for log_time, log_data in logs.items(): 
                    display_logs.append([log_time, log_data.get('title', ''), log_data.get('description', '')])
        
        for row_data in sorted(display_logs, key=lambda x: x[0]):
            row_position = self.ui.logsTable.rowCount()
            self.ui.logsTable.insertRow(row_position)
            for col, data in enumerate(row_data): self.ui.logsTable.setItem(row_position, col, L_Table_Widget_Item(str(data)))
        
        print(f"Loaded {log_types} type logs for date: {date}")

    def _delete_old_logs(self, days=5):
        """Deletes logs older than the specified number of days."""
        import os
        from datetime import datetime, timedelta
        log_dir = os.path.join(os.path.dirname(__file__), '../e_database')
        now = datetime.now()
        for fname in os.listdir(log_dir):
            if fname.startswith('f_log') and fname.endswith('.json'):
                fpath = os.path.join(log_dir, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if (now - mtime).days > days: os.remove(fpath)
                except Exception as e: print(f"Could not delete log file: {fpath} - {e}")

    def load_users(self):
        """Loads users from the model and populates the table."""
        self.ui.usersTable.setRowCount(0)
        users = M_Telegram.F_Get_All_Users()
        if not users:
            self._user_clear_inputs()
            self._user_update_button_states()
            return

        self.ui.usersTable.setRowCount(len(users))
        for row, (user_id, user_data) in enumerate(users.items()):
            self.ui.usersTable.setItem(row, 0, L_Table_Widget_Item(str(user_id)))
            self.ui.usersTable.setItem(row, 1, L_Table_Widget_Item(user_data.get("user_name", "")))
            self.ui.usersTable.setItem(row, 2, L_Table_Widget_Item("Evet" if user_data.get("user_type") else "Hayır"))
            self.ui.usersTable.setItem(row, 3, L_Table_Widget_Item("Evet" if user_data.get("user_active") else "Hayır"))
        
        self._user_clear_inputs()
        self._user_update_button_states()
        print("Users loaded into the interface.")

    def _user_selection_changed(self):
        """Handles actions when a user is selected from the table."""
        selected_items = self.ui.usersTable.selectedItems()
        if not selected_items:
            self._user_clear_inputs()
            return

        selected_row = self.ui.usersTable.currentRow()
        chat_id = self.ui.usersTable.item(selected_row, 0).text()
        user_name = self.ui.usersTable.item(selected_row, 1).text()
        is_admin_text = self.ui.usersTable.item(selected_row, 2).text()
        is_active_text = self.ui.usersTable.item(selected_row, 3).text()
        self.ui.userInput_chatId.setText(chat_id)
        self.ui.userInput_userName.setText(user_name)
        self.ui.user_isAdminCheck.setChecked(is_admin_text == "Yes")
        self.ui.user_isActiveCheck.setChecked(is_active_text == "Yes")
        self._user_update_button_states()

    def _user_add(self):
        """Adds a new user."""
        chat_id = self.ui.userInput_chatId.text().strip()
        user_name = self.ui.userInput_userName.text().strip()
        is_admin = self.ui.user_isAdminCheck.isChecked()
        is_active = self.ui.user_isActiveCheck.isChecked()
        if not chat_id or not user_name:
            L_Message_Box.warning(self, "Missing Information", "Chat ID and Name fields cannot be empty.")
            return

        if not chat_id.isdigit():
            L_Message_Box.warning(self, "Invalid ID", "Chat ID must contain only numbers.")
            return

        if M_Telegram.F_Add_User(chat_id, user_name, p_user_type=is_admin, p_user_active=is_active):
            L_Message_Box.information(self, "Success", f"User '{user_name}' has been added.")
            self.load_users()

        else: L_Message_Box.critical(self, "Error", "Failed to add user. This Chat ID might already exist.")

    def _user_update(self):
        """Updates the information of the selected user."""
        selected_items = self.ui.usersTable.selectedItems()
        if not selected_items:
            L_Message_Box.warning(self, "No User Selected", "Please select a user to update.")
            return
            
        chat_id = self.ui.usersTable.item(self.ui.usersTable.currentRow(), 0).text()
        user_name = self.ui.userInput_userName.text().strip()
        is_admin = self.ui.user_isAdminCheck.isChecked()
        is_active = self.ui.user_isActiveCheck.isChecked()
        if not user_name:
            L_Message_Box.warning(self, "Missing Information", "Name field cannot be empty.")
            return

        if M_Telegram.F_Update_User(chat_id, p_user_name=user_name, p_user_type=is_admin, p_user_active=is_active):
            L_Message_Box.information(self, "Success", "User information has been updated.")
            self.load_users()
            
        else: L_Message_Box.critical(self, "Hata", "Kullanıcı güncellenemedi.")

    def _user_delete(self):
        """Deletes the selected user."""
        selected_items = self.ui.usersTable.selectedItems()
        if not selected_items:
            L_Message_Box.warning(self, "No User Selected", "Please select a user to delete.")
            return

        selected_row = self.ui.usersTable.currentRow()
        chat_id = self.ui.usersTable.item(selected_row, 0).text()
        user_name = self.ui.usersTable.item(selected_row, 1).text()
        reply = L_Message_Box.question(self, 'Delete Confirmation',
                                     f"Are you sure you want to delete user '{user_name}' ({chat_id})?",
                                     L_Message_Box.StandardButton.Yes | L_Message_Box.StandardButton.No,
                                     L_Message_Box.StandardButton.No)

        if reply == L_Message_Box.StandardButton.Yes:
            if M_Telegram.F_Del_User(chat_id):
                L_Message_Box.information(self, "Success", "User has been deleted.")
                self.load_users()
            
            else: L_Message_Box.critical(self, "Error", "Failed to delete user.")

    def _user_clear_inputs(self):
        """Clears all user input fields."""
        self.ui.userInput_chatId.clear()
        self.ui.userInput_userName.clear()
        self.ui.user_isAdminCheck.setChecked(False)
        self.ui.user_isActiveCheck.setChecked(True)
        self.ui.usersTable.clearSelection()

    def _user_update_button_states(self):
        """Updates the state of buttons based on user selection."""
        has_selection = bool(self.ui.usersTable.selectedItems())
        self.ui.user_updateButton.setEnabled(has_selection)
        self.ui.user_deleteButton.setEnabled(has_selection)
        self.ui.userInput_chatId.setReadOnly(has_selection)

    def process_signal_queue(self):
        if not hasattr(self, 'activity_id_counter'): self.activity_id_counter = 1
        max_rows = max(100, self.scanner_stats.get('total_symbols', 50))
        while not S_Signal_Que.empty():
            signal_data = S_Signal_Que.get()
            row_position = self.ui.activityTable.rowCount()
            self.ui.activityTable.insertRow(row_position)
            self.ui.activityTable.setItem(row_position, 0, L_Table_Widget_Item(str(signal_data.get('symbol', '-'))))
            self.ui.activityTable.setItem(row_position, 1, L_Table_Widget_Item(str(signal_data.get('volume', '-'))))
            self.ui.activityTable.setItem(row_position, 2, L_Table_Widget_Item(str(signal_data.get('period', '-'))))
            self.ui.activityTable.setItem(row_position, 3, L_Table_Widget_Item(str(signal_data.get('price', '-'))))
            self.ui.activityTable.setItem(row_position, 4, L_Table_Widget_Item(str(signal_data.get('pattern', '-'))))
            self.ui.activityTable.setItem(row_position, 5, L_Table_Widget_Item(str(signal_data.get('fib_0_0', '-'))))
            self.ui.activityTable.setItem(row_position, 6, L_Table_Widget_Item(str(signal_data.get('fib_0_01', '-'))))
            self.ui.activityTable.setItem(row_position, 7, L_Table_Widget_Item(str(signal_data.get('fib_0_236', '-'))))
            self.ui.activityTable.setItem(row_position, 8, L_Table_Widget_Item(str(signal_data.get('fib_0_382', '-'))))
            self.ui.activityTable.setItem(row_position, 9, L_Table_Widget_Item(str(signal_data.get('fib_1_0', '-'))))
            while self.ui.activityTable.rowCount() > max_rows: self.ui.activityTable.removeRow(0)
            if signal_data.get('direction') in ('LONG', 'SHORT'): self.add_signal_to_table(signal_data)

    def closeEvent(self, event):
        """Stops all threads when the application is closed"""
        self.status_thread.stop()
        self.status_thread.wait()
        event.accept()

# ----- START --------------------------------------------------

if __name__ == '__main__':
    app = L_Application(L_SYS.argv)
    window = C_Main_Window()
    window.show()
    L_SYS.exit(app.exec()) 
    