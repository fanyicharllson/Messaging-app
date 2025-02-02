# loading_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from welcome_view.spinner_widget import SpinnerWidget

class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading ChatHub...")
        self.setStyleSheet("background-color: #2c3e50;")
        self.setFixedSize(900, 600)

        layout = QVBoxLayout(self)
        # Only horizontally center the widgets; vertical alignment will be at the top.
        layout.setAlignment(Qt.AlignHCenter)
        layout.setContentsMargins(0, 50, 0, 0)
        layout.setSpacing(20)

        # Create and configure the spinner widget with increased size parameters
        self.spinner = SpinnerWidget(
            color=QColor("#ffffff"),  # White spinner
            line_count=12,
            line_length=20,    # Increased line length for a larger spinner
            line_width=6,      # Increased line width
            inner_radius=20,   # Increased inner radius
            update_interval=80
        )
        self.spinner.setFixedSize(150, 150)  # Increase the overall spinner size
        layout.addWidget(self.spinner, alignment=Qt.AlignHCenter | Qt.AlignTop)

        # Add a modern loading text directly below the spinner
        self.loading_text = QLabel("Just a sec, we’re loading up the magic...")
        self.loading_text.setStyleSheet("color: white; font-size: 24px; font-weight: 700;")
        self.loading_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_text, alignment=Qt.AlignHCenter | Qt.AlignTop)

        # Add a stretch at the bottom to push the spinner and text to the top
        layout.addStretch()
