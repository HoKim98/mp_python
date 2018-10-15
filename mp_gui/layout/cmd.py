from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QPushButton, QLineEdit, QTextEdit, QWidget

from mp_gui import common


class CommandLine(QWidget):
    def __init__(self, parent, func_cmd):
        super().__init__(parent)
        self.func_cmd = func_cmd

        self.log = QTextEdit('', self)
        self.log.setAlignment(Qt.AlignTop)
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.log.setFont(common.font)

        self.cmd = QLineEdit('y = x * 3', self)
        self.cmd.setAlignment(Qt.AlignTop)
        self.cmd.setFont(common.font)

        self.btn = QPushButton('push', self)
        self.btn.mouseReleaseEvent = self.execute

    def execute(self, *args):
        msg = self.cmd.text()
        if len(msg) > 0:
            self.cmd.setText('')
            self.log.append(msg)
            self.func_cmd(msg)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            # enter event
            if event.key() in [Qt.Key_Enter, 16777220]:
                self.execute()

    def paintEvent(self, event):
        log_rect = QRectF(self.rect())
        log_rect.setHeight(self.getLogHeight())

        cmd_rect = QRectF(self.rect())
        cmd_rect.setY(self.getLogHeight())
        cmd_rect.setWidth(cmd_rect.width() - self.getButtonWidth())
        cmd_rect.setHeight(self.getCommandHeight())

        btn_rect = QRectF(cmd_rect)
        btn_rect.setX(btn_rect.width())
        btn_rect.setWidth(self.getButtonWidth())

        self.log.setGeometry(*log_rect.getRect())
        self.cmd.setGeometry(*cmd_rect.getRect())
        self.btn.setGeometry(*btn_rect.getRect())

    def getFixedHeight(self):
        return 130

    def getLogHeight(self):
        return self.getFixedHeight() - self.getCommandHeight()

    def getCommandHeight(self):
        return 30

    def getButtonWidth(self):
        return 80
