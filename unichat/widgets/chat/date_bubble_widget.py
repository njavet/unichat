# external imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QFrame
)


class DateBubbleWidget(QWidget):
    """
    A bubble that displays the date in a chat history

    """

    def __init__(self, timestamp: str):
        """
        timestamp is of the format: %d.%m.%y (e.g. 28.04.24)
        """
        super().__init__()
        self.frame = QFrame()
        self.label = QLabel(timestamp)
        self.init_ui()

    def init_ui(self):
        """
        sets up the date bubble layout
        """
        layout = QGridLayout()
        self.frame.setObjectName('DateBubble')
        self.label.setObjectName('DateLabel')
        self.frame.setFrameStyle(QFrame.StyledPanel)
        self.frame.setLineWidth(0)
        self.label.setAlignment(Qt.AlignCenter)

        frame_layout = QGridLayout()
        frame_layout.addWidget(self.label)
        self.frame.setLayout(frame_layout)
        layout.addWidget(self.frame, 0, 0, alignment=Qt.AlignCenter)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
