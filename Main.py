import sys
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QRadioButton, QStackedWidget, QGridLayout,
    QSizePolicy
)

# Import all page and algorithm classes
from Choose import AlgorithmDisplayPage
from Input import (
    FCFS_InputPage, SJF_InputPage, SRTF_InputPage,
    Priority_InputPage, PriorityPreemptive_InputPage, RR_InputPage
)
from Output import (
    FCFS_OutputPage, SJF_OutputPage, SRTF_OutputPage,
    Priority_OutputPage, PriorityPreemptive_OutputPage, RR_OutputPage
)
import Algorithm_Phase1 as sched

# --- App Stylesheet ---
STYLESHEET = """
    #MainWindow, #ColorPage, #AlgoDisplayPage, 
    #FCFS_InputPage, #SJF_InputPage, #SRTF_InputPage, 
    #Priority_InputPage, #PriorityPreemptive_InputPage, #RR_InputPage,
    #FCFS_OutputPage, #SJF_OutputPage, #SRTF_OutputPage,
    #Priority_OutputPage, #PriorityPreemptive_OutputPage, #RR_OutputPage {
        background-color: #212121;
        color: white;
    }
    #TitleBar { background-color: #171717; }
    #TitleBar QPushButton { background-color: #171717; color: white; border: none; font-size: 14px; padding: 8px; }
    #TitleBar QPushButton:hover { background-color: #333333; }

    #ContinueButton { background-color: #3c3c3c; color: %(color)s; font-size: 22px; font-weight: bold; border: 2px solid transparent; padding: 20px; border-radius: 5px; }
    #ContinueButton:hover { background-color: #4f4f4f; }
    #ContinueButton:focus { border: 2px solid %(color)s; }

    QRadioButton { font-size: 18px; padding: 20px; spacing: 15px; }
    QRadioButton::indicator { width: 24px; height: 24px; border: 2px solid #777; border-radius: 13px; background-color: #333; }
    QRadioButton::indicator:hover { border: 2px solid #999; }
    QRadioButton::indicator:checked { border: 2px solid %(color)s; background-color: %(color)s; }
    
    .themed-label { font-size: 28px; color: %(color)s; padding-bottom: 20px; }
    #BackButton { background-color: #3c3c3c; color: %(color)s; font-size: 14px; border: none; padding: 12px; border-radius: 3px; }
    #BackButton:hover { background-color: #4f4f4f; }

    #OutputButton { background-color: #2a2a2a; border: 2px solid %(color)s; border-radius: 5px; color: %(color)s; font-size: 18px; font-weight: bold; text-align: center; }
    #OutputButton:focus { border: 2px solid white; }

    #AlgoNameDisplay { background-color: #171717; border: 2px solid %(color)s; border-radius: 5px; color: %(color)s; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; }
    #NavButton { background-color: #3c3c3c; color: %(color)s; font-size: 24px; font-weight: bold; border: 2px solid #3c3c3c; padding: 15px 30px; border-radius: 5px; }
    #NavButton:hover { background-color: #4f4f4f; border: 2px solid %(color)s; }
    #NavButton:focus { border: 2px solid %(color)s; outline: none; }

    /* Input Page Styles */
    #table-header { color: %(color)s; font-size: 16px; font-weight: bold; }
    #themed-input { background-color: #333; color: white; border: 1px solid #555; border-radius: 3px; padding: 8px; font-size: 14px; }
    #themed-input:focus { border: 1px solid %(color)s; }
    #table-control-button { background-color: #555; color: %(color)s; padding: 8px 16px; border: none; border-radius: 3px; }
    #table-control-button:hover { background-color: #666; }
    #scroll-area { border: none; }
    #themed-label-small { font-size: 16px; color: %(color)s; }
    #error-label { color: #E53935; font-size: 14px; font-weight: bold; }

    /* Output Page Styles */
    #results-table { border: 1px solid #444; gridline-color: #444; color: white; }
    #results-table QHeaderView::section { background-color: #333; padding: 10px; border: 1px solid #444; color: %(color)s; }
    #gantt-chart { font-size: 14px; font-weight: bold; color: %(color)s; }
    #metrics-label { font-size: 16px; font-weight: bold; color: %(color)s; }
"""

class ColorChooserPage(QWidget):
    color_changed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ColorPage")
        self.radio_buttons = []
        self.focusable_widgets = []
        layout = QVBoxLayout(self)
        layout.setSpacing(40)
        layout.setContentsMargins(50, 50, 50, 50)
        self.continue_button = QPushButton("choose a color ❤️")
        self.continue_button.setObjectName("ContinueButton")
        self.focusable_widgets.append(self.continue_button)
        radio_grid = QGridLayout()
        radio_grid.setSpacing(15)
        colors = {'Red': '#E53935', 'Blue': '#1E88E5', 'Green': '#43A047', 'Yellow': '#FDD835', 'Purple': '#8E24AA', 'Orange': '#FB8C00', 'Pink': '#EC407A', 'White': '#FFFFFF'}
        positions = [(i, j) for i in range(2) for j in range(4)]
        for i in range(4): radio_grid.setColumnStretch(i, 1)
        for i in range(2): radio_grid.setRowStretch(i, 1)
        for pos, (name, code) in zip(positions, colors.items()):
            radio = QRadioButton(name)
            radio.setProperty("color_code", code)
            radio.toggled.connect(self.on_color_select)
            radio.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            radio.setStyleSheet(f"color: {code};")
            radio_grid.addWidget(radio, pos[0], pos[1])
            self.radio_buttons.append(radio)
            self.focusable_widgets.append(radio)
        layout.addWidget(self.continue_button, 1)
        layout.addLayout(radio_grid, 3)
        self.radio_buttons[-1].setChecked(True)
    def on_color_select(self):
        sender_radio = self.sender()
        if sender_radio and sender_radio.isChecked(): self.color_changed.emit(sender_radio.property("color_code"))
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() not in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter]: super().keyPressEvent(event); return
        try: current_index = self.focusable_widgets.index(self.focusWidget())
        except (ValueError, AttributeError): current_index = 0
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if hasattr(self.focusable_widgets[current_index], 'click'): self.focusable_widgets[current_index].click()
            elif hasattr(self.focusable_widgets[current_index], 'setChecked'): self.focusable_widgets[current_index].setChecked(True)
            return
        num_cols = 4
        if current_index == 0: next_index = 1 if event.key() == Qt.Key_Down else current_index
        else:
            row, col = (current_index - 1) // num_cols, (current_index - 1) % num_cols
            if event.key() == Qt.Key_Right: next_index = row * num_cols + (col + 1) % num_cols + 1
            elif event.key() == Qt.Key_Left: next_index = row * num_cols + (col - 1 + num_cols) % num_cols + 1
            elif event.key() == Qt.Key_Down: next_index = current_index + num_cols if row == 0 else current_index
            elif event.key() == Qt.Key_Up: next_index = current_index - num_cols if row == 1 else 0
        if 0 <= next_index < len(self.focusable_widgets): self.focusable_widgets[next_index].setFocus()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("OS Algorithm Selector")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.theme_color = "#FFFFFF"
        self.old_pos = self.pos()
        title_bar = QWidget(self)
        title_bar.setObjectName("TitleBar")
        title_bar.mousePressEvent = self.title_bar_press
        title_bar.mouseMoveEvent = self.move_window
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.addStretch()
        minimize_button, close_button = QPushButton("—"), QPushButton("X")
        minimize_button.setFocusPolicy(Qt.NoFocus); close_button.setFocusPolicy(Qt.NoFocus)
        title_bar_layout.addWidget(minimize_button); title_bar_layout.addWidget(close_button)
        self.setMenuWidget(title_bar)
        close_button.clicked.connect(self.close); minimize_button.clicked.connect(self.showMinimized)

        self.stack = QStackedWidget()
        self.color_page = ColorChooserPage()
        self.display_page = AlgorithmDisplayPage()

        self.input_pages = {
            "First Come First Serve": FCFS_InputPage(), "Shortest Job First": SJF_InputPage(),
            "Shortest Remaining First": SRTF_InputPage(), "Priority": Priority_InputPage(),
            "Priority (Preemptive)": PriorityPreemptive_InputPage(), "Round Robin": RR_InputPage()
        }
        self.output_pages = {
            "First Come First Serve": FCFS_OutputPage(), "Shortest Job First": SJF_OutputPage(),
            "Shortest Remaining First": SRTF_OutputPage(), "Priority": Priority_OutputPage(),
            "Priority (Preemptive)": PriorityPreemptive_OutputPage(), "Round Robin": RR_OutputPage()
        }
        self.algo_functions = {
            "First Come First Serve": sched.FCFS,
            "Shortest Job First": sched.SJF,
            "Shortest Remaining First": sched.SRT,
            "Priority": sched.Priority_NP,
            "Priority (Preemptive)": sched.Priority_P,
            "Round Robin": sched.Round_Robin
        }

        self.stack.addWidget(self.color_page)
        self.stack.addWidget(self.display_page)
        for page in self.input_pages.values(): self.stack.addWidget(page)
        for page in self.output_pages.values(): self.stack.addWidget(page)

        self.setCentralWidget(self.stack)

        # Connect signals
        self.color_page.color_changed.connect(self.update_theme_color)
        self.color_page.continue_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.display_page))
        self.display_page.back_requested.connect(lambda: self.stack.setCurrentWidget(self.color_page))
        self.display_page.output_button.clicked.connect(self.open_input_page)

        for name, page in self.input_pages.items():
            page.back_requested.connect(lambda: self.stack.setCurrentWidget(self.display_page))
            page.continue_to_output.connect(self.handle_output_request)
            self.output_pages[name].back_requested.connect(lambda p=page: self.stack.setCurrentWidget(p))

        self.update_theme_color(self.theme_color)
        self.showMaximized()
        self.color_page.continue_button.setFocus()

    def open_input_page(self):
        current_algo_name = self.display_page.algorithms[self.display_page.current_algo_index]
        if current_algo_name in self.input_pages:
            self.stack.setCurrentWidget(self.input_pages[current_algo_name])

    def handle_output_request(self, data):
        algo_name = data['algorithm']
        processes = data['processes']

        algo_func = self.algo_functions.get(algo_name)
        if not algo_func: return

        adapted_processes = []
        for p in processes:
            proc = { "PID": p['name'], "arrival": p['arrival_time'], "burst": p['burst_time'] }
            if 'priority' in p: proc['priority'] = p['priority']
            adapted_processes.append(proc)

        if algo_name == "Round Robin":
            results = algo_func(adapted_processes, data['time_quantum'])
        else:
            results = algo_func(adapted_processes)

        output_page = self.output_pages.get(algo_name)
        if output_page:
            output_page.display_results(results)
            self.stack.setCurrentWidget(output_page)

    def update_theme_color(self, color):
        self.theme_color = color
        self.setStyleSheet(STYLESHEET.replace("%(color)s", self.theme_color))

    def title_bar_press(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPosition().toPoint()
    def move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
