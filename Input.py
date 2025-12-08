"""
This module contains six distinct GUI input pages, one for each scheduling algorithm.

A BaseInputPage class is used to handle the common UI elements and logic,
such as adding/removing processes and handling the continue/back buttons. Each
specific algorithm then gets its own simple subclass that configures the base class.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QLineEdit, QScrollArea
)

class BaseInputPage(QWidget):
    """
    A base class for all algorithm input pages. It provides a consistent layout
    and functionality for process input, which can be configured for priority
    and time quantum fields.
    """
    # --- Signals ---
    back_requested = Signal()
    # Emits a dictionary containing all the data needed to run the simulation.
    continue_to_output = Signal(dict)

    def __init__(self, algo_name, has_priority=False, has_time_quantum=False, parent=None):
        super().__init__(parent)
        self.setObjectName(f"{algo_name.replace(' ', '_')}InputPage")
        self.current_algorithm = algo_name
        self.process_rows = []

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)

        # --- Title ---
        title_label = QLabel(f"{algo_name} - Input")
        title_label.setObjectName("themed-label")
        title_label.setAlignment(Qt.AlignCenter)

        # --- Algorithm-specific options (e.g., Time Quantum) ---
        # This widget is only visible for the Round Robin algorithm.
        self.time_quantum_widget = QWidget()
        options_layout = QHBoxLayout(self.time_quantum_widget)
        time_quantum_label = QLabel("Time Quantum:")
        time_quantum_label.setObjectName("themed-label-small")
        self.time_quantum_input = QLineEdit("4")
        self.time_quantum_input.setFixedWidth(60)
        self.time_quantum_input.setObjectName("themed-input")
        options_layout.addStretch()
        options_layout.addWidget(time_quantum_label)
        options_layout.addWidget(self.time_quantum_input)
        options_layout.addStretch()
        self.time_quantum_widget.setVisible(has_time_quantum)

        # --- Process Table ---
        # A scroll area is used to handle a large number of processes gracefully.
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll-area")
        
        process_grid_widget = QWidget()
        self.process_grid_layout = QGridLayout(process_grid_widget)
        self.process_grid_layout.setSpacing(10)
        self.process_grid_layout.setColumnStretch(0, 2) # Give name column more space
        self.process_grid_layout.setColumnStretch(1, 1)
        self.process_grid_layout.setColumnStretch(2, 1)
        if has_priority:
            self.process_grid_layout.setColumnStretch(3, 1)

        # Create table headers.
        headers = ["Process Name", "Arrival Time", "Burst Time"]
        if has_priority:
            headers.append("Priority")

        for i, text in enumerate(headers):
            header = QLabel(text)
            header.setObjectName("table-header")
            self.process_grid_layout.addWidget(header, 0, i, Qt.AlignCenter)
        
        scroll_area.setWidget(process_grid_widget)

        # --- Table Control Buttons ---
        controls_layout = QHBoxLayout()
        add_button = QPushButton("Add Process")
        remove_button = QPushButton("Remove Process")
        add_button.setObjectName("table-control-button")
        remove_button.setObjectName("table-control-button")
        add_button.clicked.connect(lambda: self.add_process_row(has_priority))
        remove_button.clicked.connect(self.remove_process_row)
        controls_layout.addStretch()
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(remove_button)
        controls_layout.addStretch()

        # --- Error Label ---
        # This label is shown only when the user enters invalid data.
        self.error_label = QLabel("Invalid input. Please check all fields are correct integers.")
        self.error_label.setObjectName("error-label")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)

        # --- Navigation Buttons ---
        nav_layout = QHBoxLayout()
        back_button = QPushButton("< Back")
        continue_button = QPushButton("Continue to Output")
        back_button.setObjectName("BackButton")
        continue_button.setObjectName("ContinueButton")
        
        back_button.clicked.connect(self.back_requested.emit)
        continue_button.clicked.connect(self.on_continue)

        nav_layout.addWidget(back_button)
        nav_layout.addStretch()
        nav_layout.addWidget(continue_button)

        # --- Assemble Page Layout ---
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.time_quantum_widget)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.error_label)
        main_layout.addLayout(nav_layout)

        # Add some default rows for the user to start with.
        for i in range(4):
            self.add_process_row(has_priority)

    def add_process_row(self, has_priority):
        """Adds a new row of QLineEdit widgets to the process table."""
        row_index = len(self.process_rows)
        
        name_edit = QLineEdit(f"P{row_index + 1}")
        arrival_edit = QLineEdit("0")
        burst_edit = QLineEdit("1")
        
        row_widgets = {'name': name_edit, 'arrival': arrival_edit, 'burst': burst_edit}
        
        if has_priority:
            priority_edit = QLineEdit("0")
            priority_edit.setObjectName("themed-input")
            priority_edit.setAlignment(Qt.AlignCenter)
            row_widgets['priority'] = priority_edit

        for i, widget in enumerate(row_widgets.values()):
            widget.setObjectName("themed-input")
            widget.setAlignment(Qt.AlignCenter)
            self.process_grid_layout.addWidget(widget, row_index + 1, i)
        
        self.process_rows.append(row_widgets)

    def remove_process_row(self):
        """Removes the last row from the process table."""
        if not self.process_rows:
            return
        row_to_remove = self.process_rows.pop()
        for widget in row_to_remove.values():
            self.process_grid_layout.removeWidget(widget)
            widget.deleteLater()

    def on_continue(self):
        """Validates the input data and emits it if it's valid."""
        processes = []
        try:
            for row in self.process_rows:
                proc = {
                    'name': row['name'].text(),
                    'arrival_time': int(row['arrival'].text()),
                    'burst_time': int(row['burst'].text())
                }
                if 'priority' in row:
                    proc['priority'] = int(row['priority'].text())
                processes.append(proc)

            data_to_emit = {'algorithm': self.current_algorithm, 'processes': processes}
            
            if self.time_quantum_widget.isVisible():
                data_to_emit['time_quantum'] = int(self.time_quantum_input.text())
            
            self.error_label.setVisible(False)
            self.continue_to_output.emit(data_to_emit)
        except (ValueError, KeyError):
            # If any input is not a valid integer, show the error label.
            self.error_label.setVisible(True)

# --- 1. FCFS Input Page ---
class FCFS_InputPage(BaseInputPage):
    """A static input page for the FCFS algorithm."""
    def __init__(self, parent=None):
        super().__init__("First Come First Serve", has_priority=False, has_time_quantum=False, parent=parent)

# --- 2. SJF Input Page ---
class SJF_InputPage(BaseInputPage):
    """A static input page for the SJF algorithm."""
    def __init__(self, parent=None):
        super().__init__("Shortest Job First", has_priority=False, has_time_quantum=False, parent=parent)

# --- 3. SRTF Input Page ---
class SRTF_InputPage(BaseInputPage):
    """A static input page for the SRTF algorithm."""
    def __init__(self, parent=None):
        super().__init__("Shortest Remaining First", has_priority=False, has_time_quantum=False, parent=parent)

# --- 4. Priority (Non-Preemptive) Input Page ---
class Priority_InputPage(BaseInputPage):
    """A static input page for the non-preemptive Priority algorithm."""
    def __init__(self, parent=None):
        super().__init__("Priority", has_priority=True, has_time_quantum=False, parent=parent)

# --- 5. Priority (Preemptive) Input Page ---
class PriorityPreemptive_InputPage(BaseInputPage):
    """A static input page for the preemptive Priority algorithm."""
    def __init__(self, parent=None):
        super().__init__("Priority (Preemptive)", has_priority=True, has_time_quantum=False, parent=parent)

# --- 6. Round Robin Input Page ---
class RR_InputPage(BaseInputPage):
    """A static input page for the Round Robin algorithm."""
    def __init__(self, parent=None):
        super().__init__("Round Robin", has_priority=False, has_time_quantum=True, parent=parent)
