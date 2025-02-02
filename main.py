import qtawesome as qta
from PySide6.QtWidgets import QApplication, QPushButton

app = QApplication([])

button = QPushButton("Send")
button.setIcon(qta.icon('fa.send'))  # Font Awesome's "send" icon
button.show()

app.exec()
