from graphviz import Digraph

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QScrollBar, QWidget


class GraphViewer(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._y = 0
        self._width = 1
        self._height = 1

        self.dot = Digraph(format='svg', strict=True)
        self._declared_count = 1
        self._declared = dict()
        self._renderer = QSvgRenderer(self.dot.pipe(), self)

        self.scrollbar = QScrollBar(self.parent())
        self.scrollbar.setRange(0, 0)
        self.parent().wheelEvent = self.wheelEvent

    def wheelEvent(self, event):
        if event.x() > self.getScrollWidth():
            return
        if event.y() > self._height:
            return
        self.scrollbar.wheelEvent(event)

    def add(self, data):
        # is variable
        if data in self._declared.keys():
            return self._declared[data]
        if data.is_variable:
            name = data.name
            self._declared[data] = name
            self.dot.node(name)
            if data.toward is not None:
                toward = self.add(data.toward)
                self.dot.edge(toward, name)
            return name
        # is constant
        if data.is_constant:
            name = data.symbol
            self._declared[data] = name
            self.dot.node(name)
            return name
        # is operator
        if data.is_operator:
            name = '[%d] %s' % (self._declared_count, data.name)
            self._declared_count += 1
            self._declared[data] = name
            self.dot.node(name)
            args = [data.sub, data.obj, data.step]
            if data.args is not None:
                args += data.args
            args = [arg for arg in args if arg is not None]
            for arg in args:
                arg = self.add(arg)
                self.dot.edge(arg, name)
            return name

    def paintEvent(self, event):
        self._width = self.width()
        self._height = self.height()
        self.scrollbar.setGeometry(self.getScrollWidth(), 0, 20, self._height)
        self.resize(self._renderer.defaultSize())
        painter = QPainter(self)
        painter.restore()
        drawRect = QRectF(self.rect())

        if self.scrollbar.maximum() == 0:
            draw_y = 0
        else:
            draw_y = drawRect.height() - self._height
            draw_y *= self.scrollbar.value() / self.scrollbar.maximum()

        drawRect.setY(-draw_y)
        drawRect.setHeight(drawRect.y() + drawRect.height())
        self._renderer.render(painter, drawRect)

    def flush(self):
        self._renderer = QSvgRenderer(self.dot.pipe())
        max_h = self._renderer.defaultSize().height() / self._height
        if max_h <= 1:
            max_h = 0
        max_h = int(self.delta() * max_h)
        self.scrollbar.setMaximum(max_h)

    def clear(self):
        self._declared_count = 1
        self._declared = dict()
        self.dot.clear()

    def getScrollWidth(self):
        return self._width - 20

    def delta(self):
        return 3.14
