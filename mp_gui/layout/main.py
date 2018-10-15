import sys
from PyQt5.QtWidgets import QApplication, QWidget

from mp.core import error

from mp_gui.layout.cmd import CommandLine
from mp_gui.layout.graph import GraphViewer
from mp_gui.core.interpreter import GuiInterpreter


class MpGui(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.graph = GraphViewer(self)
        self.cmdline = CommandLine(self, self.execute)

        self.interpreter = GuiInterpreter()

    def execute(self, msg: str):
        try:
            data_array = list(self.interpreter.code_to_data(msg))
            for data in data_array:
                self.interpreter.plan.push(data)
            ios = self.interpreter.get_ios().copy()
            self.interpreter.plan.execute()
            self.graph.clear()

            for var in self.interpreter.get_vars().values():
                self.graph.add(var)
            self.graph.flush()

            for name, is_save in ios.items():
                if is_save:
                    value = self.interpreter.plan.attr[name]
                    value = 'None' if value is None else str(value.get_value())
                    self.cmdline.log.append('%s = %s' % (name, value))

        except error.BaseError as e:
            self.cmdline.log.append(str(e))

    def paintEvent(self, event):
        rect = self.rect()
        self.graph.setGeometry(0, 0, rect.width(), rect.height() - self.cmdline.getFixedHeight())
        self.cmdline.setGeometry(0, rect.height() - self.cmdline.getFixedHeight(),
                                 rect.width(), self.cmdline.getFixedHeight())

    def loop(self):
        sys.exit(self.app.exec_())


class MpGuiLinker:

    # object is unique
    _self = None

    def __new__(cls):
        # if already inited
        if cls._self is not None:
            return cls._self
        # init
        app = QApplication(sys.argv)

        cls._self = MpGui(app)
        cls._self.resize(800, 600)
        cls._self.move(300, 300)
        cls._self.setMinimumHeight(200)
        cls._self.setWindowTitle('MpCAD')
        cls._self.show()

        return cls._self
