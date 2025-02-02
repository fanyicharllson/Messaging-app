# spinner_widget.py
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

class SpinnerWidget(QWidget):
    def __init__(self, parent=None,
                 line_count=12,
                 line_length=10,
                 line_width=3,
                 inner_radius=10,
                 color=QColor("#3498db"),  # Default blue color
                 update_interval=100):
        """
        A custom spinner widget.

        :param line_count: Number of lines (spokes) in the spinner.
        :param line_length: Length of each line.
        :param line_width: Width of each line.
        :param inner_radius: Distance from center to the beginning of the lines.
        :param color: Base color of the spinner.
        :param update_interval: Milliseconds between updates.
        """
        super().__init__(parent)
        self.line_count = line_count
        self.line_length = line_length
        self.line_width = line_width
        self.inner_radius = inner_radius
        self.base_color = color
        self.current_counter = 0

        # Timer to update the spinner rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(update_interval)

        # Ensure the widget is sized to contain the spinner
        diameter = (self.inner_radius + self.line_length) * 2
        self.setMinimumSize(diameter, diameter)
        self.setMaximumSize(diameter, diameter)

    def rotate(self):
        self.current_counter = (self.current_counter + 1) % self.line_count
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        width = self.width()
        height = self.height()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(width / 2, height / 2)

        step_angle = 360 / self.line_count
        for i in range(self.line_count):
            # Calculate alpha based on position relative to the current counter for a fading effect
            alpha = int(255 * ((i + self.current_counter) % self.line_count) / self.line_count)
            color = QColor(self.base_color)
            color.setAlpha(alpha)

            pen = QPen(color, self.line_width, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, self.inner_radius, 0, self.inner_radius + self.line_length)
            painter.rotate(step_angle)

        painter.end()

# If you want to test the spinner alone, you can add a __main__ section here.
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
    app = QApplication(sys.argv)
    test_window = QWidget()
    test_window.setWindowTitle("Spinner Test")
    test_window.setStyleSheet("background-color: #2c3e50;")
    layout = QVBoxLayout(test_window)
    layout.setAlignment(Qt.AlignCenter)

    spinner = SpinnerWidget(color=QColor("#ffffff"), line_count=12, line_length=12, line_width=4, inner_radius=10, update_interval=80)
    spinner.setFixedSize(100, 100)
    layout.addWidget(spinner)

    label = QLabel("Spinner Test")
    label.setStyleSheet("color: white; font-size: 18px; font-weight: 600; margin-top: 20px;")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    test_window.setFixedSize(300, 300)
    test_window.show()
    sys.exit(app.exec())
