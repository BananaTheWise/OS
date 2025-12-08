"""
Module for the Algorithm Display Page.

This file contains the UI for the second main screen of the application,
where the user can cycle through the available scheduling algorithms.
"""

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)

class AlgorithmDisplayPage(QWidget):
    """
    A page that displays the name of the currently selected algorithm and provides
    navigation controls to cycle through them or proceed to the input stage.
    """
    # --- Signals ---
    # Emitted when the user clicks the back button.
    back_requested = Signal()
    # Emitted when the algorithm is changed, to keep other parts of the app in sync.
    algorithm_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AlgoDisplayPage")

        # --- Algorithm Data ---
        # The master list of algorithms. The names must match the keys in Main.py.
        self.algorithms = [
            "First Come First Serve", 
            "Shortest Job First", 
            "Shortest Remaining First", 
            "Priority", 
            "Priority (Preemptive)", 
            "Round Robin"
        ]
        self.current_algo_index = 0

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)

        # --- UI Widgets ---
        # The large button that takes the user to the input page for the selected algorithm.
        self.output_button = QPushButton("Input Stage")
        self.output_button.setObjectName("OutputButton")
        self.output_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Horizontal layout for the navigation controls (<, Name, >).
        nav_layout = QHBoxLayout()

        self.left_button = QPushButton("<")
        self.left_button.setObjectName("NavButton")
        self.left_button.clicked.connect(self.previous_algorithm)

        self.algo_name_label = QLabel(self.algorithms[self.current_algo_index])
        self.algo_name_label.setObjectName("AlgoNameDisplay")
        self.algo_name_label.setAlignment(Qt.AlignCenter)

        self.right_button = QPushButton(">")
        self.right_button.setObjectName("NavButton")
        self.right_button.clicked.connect(self.next_algorithm)

        # Assemble the navigation layout.
        nav_layout.addWidget(self.left_button, 1)  # Stretch factor 1
        nav_layout.addWidget(self.algo_name_label, 6) # Stretch factor 6 (takes up more space)
        nav_layout.addWidget(self.right_button, 1) # Stretch factor 1

        # The main back button to return to the color selection page.
        self.back_button = QPushButton("< Back to Color Selection")
        self.back_button.setObjectName("BackButton")
        self.back_button.clicked.connect(self.back_requested.emit)

        # --- Assemble Page Layout ---
        # The output button gets a higher stretch factor to make it larger.
        main_layout.addWidget(self.output_button, 3) 
        main_layout.addLayout(nav_layout, 1)
        main_layout.addWidget(self.back_button)

        # --- Event Filtering ---
        # Install an event filter on the main buttons. This allows the parent widget (this page)
        # to intercept key presses, ensuring arrow keys always change algorithms.
        self.output_button.installEventFilter(self)
        self.left_button.installEventFilter(self)
        self.right_button.installEventFilter(self)
        self.back_button.installEventFilter(self)

    def set_initial_algorithm(self, algo_name):
        """Sets the algorithm display when entering the page."""
        if algo_name in self.algorithms:
            self.current_algo_index = self.algorithms.index(algo_name)
            self.update_display()

    def next_algorithm(self):
        """Cycles to the next algorithm in the list."""
        self.current_algo_index = (self.current_algo_index + 1) % len(self.algorithms)
        self.update_display()

    def previous_algorithm(self):
        """Cycles to the previous algorithm in the list."""
        self.current_algo_index = (self.current_algo_index - 1 + len(self.algorithms)) % len(self.algorithms)
        self.update_display()

    def update_display(self):
        """Updates the UI to reflect the currently selected algorithm."""
        algo_name = self.algorithms[self.current_algo_index]
        self.algo_name_label.setText(algo_name)
        self.algorithm_changed.emit(algo_name)

    def eventFilter(self, watched, event):
        """
        Handles key presses for the watched objects (the buttons).
        This ensures arrow keys work for navigation regardless of which button has focus.
        """
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Left:
                self.previous_algorithm()
                return True  # True means the event is handled and should not be processed further.
            elif event.key() == Qt.Key_Right:
                self.next_algorithm()
                return True  # True means the event is handled.
        
        # For all other events, let the default handler process them.
        return super().eventFilter(watched, event)
