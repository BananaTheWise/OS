"""
This module contains six distinct GUI output pages, one for each scheduling algorithm.

A BaseOutputPage class handles the common UI structure for displaying results,
including a process details table, a Gantt chart representation, and performance metrics.
Each specific algorithm has its own subclass.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)

class BaseOutputPage(QWidget):
    """
    A base class for all algorithm output pages. It provides a consistent
    layout for displaying scheduling results.
    """
    # --- Signals ---
    back_requested = Signal()

    def __init__(self, algo_name, parent=None):
        super().__init__(parent)
        self.setObjectName(f"{algo_name.replace(' ', '_')}OutputPage")

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)

        # --- Title ---
        title_label = QLabel(f"{algo_name} - Output")
        title_label.setObjectName("themed-label")
        title_label.setAlignment(Qt.AlignCenter)

        # --- Results Table ---
        # This table displays the detailed metrics for each process.
        self.results_table = QTableWidget()
        self.results_table.setObjectName("results-table")
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Process", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True) # Makes table easier to read

        # --- Gantt Chart ---
        # This section visualizes the execution timeline of the processes.
        gantt_layout = QVBoxLayout()
        gantt_title = QLabel("Gantt Chart")
        gantt_title.setObjectName("table-header")
        self.gantt_chart_label = QLabel("Gantt chart will be displayed here.")
        self.gantt_chart_label.setObjectName("gantt-chart")
        self.gantt_chart_label.setWordWrap(True)
        gantt_layout.addWidget(gantt_title)
        gantt_layout.addWidget(self.gantt_chart_label)
        gantt_layout.addStretch()

        # --- Metrics ---
        # Displays the calculated average waiting and turnaround times.
        metrics_layout = QHBoxLayout()
        self.avg_waiting_label = QLabel("Avg. Waiting Time: N/A")
        self.avg_turnaround_label = QLabel("Avg. Turnaround Time: N/A")
        self.avg_waiting_label.setObjectName("metrics-label")
        self.avg_turnaround_label.setObjectName("metrics-label")
        metrics_layout.addStretch()
        metrics_layout.addWidget(self.avg_waiting_label)
        metrics_layout.addStretch()
        metrics_layout.addWidget(self.avg_turnaround_label)
        metrics_layout.addStretch()

        # --- Navigation ---
        self.back_button = QPushButton("< Back to Input")
        self.back_button.setObjectName("BackButton")
        self.back_button.clicked.connect(self.back_requested.emit)

        # --- Assemble Page Layout ---
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.results_table, 2) # Give table more stretch
        main_layout.addLayout(gantt_layout, 1)
        main_layout.addLayout(metrics_layout)
        main_layout.addWidget(self.back_button)

    def display_results(self, data):
        """Populates the UI widgets with the results from the scheduling algorithm."""
        # --- Populate Table ---
        table_data = data.get('table', [])
        self.results_table.setRowCount(len(table_data))
        for row_idx, row_data in enumerate(table_data):
            # The order of keys must match the header labels.
            headers = ['name', 'arrival_time', 'burst_time', 'completion_time', 'turnaround_time', 'waiting_time']
            for col_idx, header in enumerate(headers):
                item_value = row_data.get(header, '')
                item = QTableWidgetItem(str(item_value))
                item.setTextAlignment(Qt.AlignCenter)
                self.results_table.setItem(row_idx, col_idx, item)

        # --- Populate Gantt Chart ---
        gantt_data = data.get('gantt_chart', [])
        gantt_string = " | ".join([f"{p_name} ({start}-{end})" for p_name, start, end in gantt_data])
        self.gantt_chart_label.setText(gantt_string if gantt_string else "No processes were scheduled.")

        # --- Populate Metrics ---
        metrics = data.get('metrics', {})
        avg_wt = metrics.get('average_waiting_time', 0)
        avg_tat = metrics.get('average_turnaround_time', 0)
        self.avg_waiting_label.setText(f"Average Waiting Time: {avg_wt:.2f}")
        self.avg_turnaround_label.setText(f"Average Turnaround Time: {avg_tat:.2f}")

# --- 1. FCFS Output Page ---
class FCFS_OutputPage(BaseOutputPage):
    """A static output page for the FCFS algorithm."""
    def __init__(self, parent=None):
        super().__init__("First Come First Serve", parent=parent)

# --- 2. SJF Output Page ---
class SJF_OutputPage(BaseOutputPage):
    """A static output page for the SJF algorithm."""
    def __init__(self, parent=None):
        super().__init__("Shortest Job First", parent=parent)

# --- 3. SRTF Output Page ---
class SRTF_OutputPage(BaseOutputPage):
    """A static output page for the SRTF algorithm."""
    def __init__(self, parent=None):
        super().__init__("Shortest Remaining First", parent=parent)

# --- 4. Priority Output Page ---
class Priority_OutputPage(BaseOutputPage):
    """A static output page for the non-preemptive Priority algorithm."""
    def __init__(self, parent=None):
        super().__init__("Priority", parent=parent)

# --- 5. Priority (Preemptive) Output Page ---
class PriorityPreemptive_OutputPage(BaseOutputPage):
    """A static output page for the preemptive Priority algorithm."""
    def __init__(self, parent=None):
        super().__init__("Priority (Preemptive)", parent=parent)

# --- 6. Round Robin Output Page ---
class RR_OutputPage(BaseOutputPage):
    """A static output page for the Round Robin algorithm."""
    def __init__(self, parent=None):
        super().__init__("Round Robin", parent=parent)
