import threading

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout, QSizePolicy, \
    QButtonGroup

from path_finding.algos import aStar, bfs
from path_finding.utils import Graph


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(350, 90, 1220, 900)
        self.setFixedSize(1220, 900)
        self.setStyleSheet("QMainWindow{background: rgb(43, 43, 43)}"
                           "QWidget{color: white; background: rgb(43, 43, 43)}"
                           "QPushButton{border: 1px solid white}"
                           "QPushButton:hover{background: rgb(90, 90, 90)}"
                           "QLabel{font: 15px Impact}"
                           "QGraphicsView{border: 1px solid white}")

        self.central_widget = MainWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.setCentralWidget(self.central_widget)


def solve(func, start, goal, diagonals=False, early_exit=True):
    return func(start, goal, diagonals, early_exit)


class MainWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setFixedSize(1220, 900)
        self.grid = QHBoxLayout(self)
        self.setLayout(self.grid)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignBottom)

        self.algorithm_group = QButtonGroup(self)

        self.run_button = QPushButton("run", self)
        self.run_button.clicked.connect(self.run)
        self.run_button.setMinimumHeight(40)
        self.run_button.setMaximumWidth(300)
        self.run_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.clear_walls_button = QPushButton("clear walls", self)
        self.clear_walls_button.clicked.connect(self.clear_walls)
        self.clear_walls_button.setMinimumHeight(40)
        self.clear_walls_button.setMaximumWidth(300)
        self.clear_walls_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.diagonals_check = QCheckBox("Diagonals", self)
        self.diagonals_check.stateChanged.connect(self.run)

        self.show_grid = QCheckBox("Toggle grid", self)
        self.show_grid.stateChanged.connect(self.update)

        self.show_astar = QCheckBox("A Star", self)
        self.show_astar.setChecked(True)
        self.show_astar.stateChanged.connect(self.run)

        self.show_dijkstra = QCheckBox("Dijkstra", self)
        self.show_dijkstra.stateChanged.connect(self.run)

        self.show_bfs = QCheckBox("BFS", self)
        self.show_bfs.stateChanged.connect(self.run)

        self.algorithm_group.addButton(self.show_astar)
        self.algorithm_group.addButton(self.show_dijkstra)
        self.algorithm_group.addButton(self.show_bfs)

        self.grid.addWidget(self.show_grid)
        self.grid.addWidget(self.diagonals_check)
        self.grid.addWidget(self.clear_walls_button)
        self.grid.addWidget(self.run_button)
        self.grid.addWidget(self.show_astar)
        self.grid.addWidget(self.show_dijkstra)
        self.grid.addWidget(self.show_bfs)

        self.offset = 10
        self.size = 20

        self.setMouseTracking(True)

        self.w, self.h = 60, 40

        self.s, self.g = (1, 1), (40, 32)
        self.graph = Graph(self.w, self.h)

        self.path_ASTAR = []
        self.path_DIJKSTRA = []
        self.path_BFS = []

        self.selected = None
        self.t1 = None
        self.running = False
        self.diagonals = True
        self.visited_nodes = dict()

    def paintEvent(self, PaintEvent):

        qp = QPainter(self)

        #  Draw cell the mouse is hovering
        if self.selected:
            qp.fillRect(self.offset + self.selected[0] * self.size,
                        self.offset + self.selected[1] * self.size,
                        self.size, self.size, QColor(140, 140, 140))

        #  Fill all cells white marked as wall
        for item in self.graph.walls:
            qp.fillRect(self.offset + item[0] * self.size,
                        self.offset + item[1] * self.size,
                        self.size, self.size, Qt.white)

        #  Draw Grid / Boundary
        qp.setPen(QColor(100, 100, 100))
        if self.show_grid.isChecked():
            for y in range(self.h):
                for x in range(self.w):
                    qp.drawRect(self.offset + x * self.size, self.offset + y * self.size, self.size, self.size)
        else:
            qp.drawRect(self.offset, self.offset, self.width() - 2 * self.offset, self.height() - 100)

        # AStar-Path
        if self.show_astar.isChecked():
            qp.setPen(QPen(QColor("#FADF27"), 2))
            for i in range(len(self.path_ASTAR) - 1):
                qp.drawLine(self.offset + self.path_ASTAR[i][0] * self.size + self.size // 2,
                            self.offset + self.path_ASTAR[i][1] * self.size + self.size // 2,
                            self.offset + self.path_ASTAR[i + 1][0] * self.size + self.size // 2,
                            self.offset + self.path_ASTAR[i + 1][1] * self.size + self.size // 2)

        # Dijkstra-Path
        if self.show_dijkstra.isChecked():
            qp.setPen(QPen(QColor("#8528FA"), 2))
            for i in range(len(self.path_DIJKSTRA) - 1):
                qp.drawLine(self.offset + self.path_DIJKSTRA[i][0] * self.size + self.size // 2,
                            self.offset + self.path_DIJKSTRA[i][1] * self.size + self.size // 2,
                            self.offset + self.path_DIJKSTRA[i + 1][0] * self.size + self.size // 2,
                            self.offset + self.path_DIJKSTRA[i + 1][1] * self.size + self.size // 2)

        # BFS-Path
        if self.show_bfs.isChecked():
            qp.setPen(QPen(QColor("#F79802"), 2))
            for i in range(len(self.path_BFS) - 1):
                qp.drawLine(self.offset + self.path_BFS[i][0] * self.size + self.size // 2,
                            self.offset + self.path_BFS[i][1] * self.size + self.size // 2,
                            self.offset + self.path_BFS[i + 1][0] * self.size + self.size // 2,
                            self.offset + self.path_BFS[i + 1][1] * self.size + self.size // 2)

        #  Highlight all visited cells to see what cells have been used by the algorithm (AStar)
        if len(self.visited_nodes) > 0:
            for key in self.visited_nodes.keys():
                x, y = key
                qp.fillRect(self.offset + x * self.size,
                            self.offset + y * self.size,
                            self.size, self.size, QColor(120, 120, 120, 80))

        qp.setPen(QPen(QColor(255, 255, 255), 1))

        #  START
        qp.fillRect(self.offset + self.s[0] * self.size,
                    self.offset + self.s[1] * self.size,
                    self.size, self.size, QColor("#19ED02"))

        #  GOAL
        qp.fillRect(self.offset + self.g[0] * self.size,
                    self.offset + self.g[1] * self.size,
                    self.size, self.size, QColor("#E0110D"))

    def mousePressEvent(self, QMouseEvent):
        x, y = (QMouseEvent.pos().x() - self.offset) // self.size, \
               (QMouseEvent.pos().y() - self.offset) // self.size
        if 0 <= x < self.w and 0 <= y < self.h:
            if QMouseEvent.buttons() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.ShiftModifier:
                if not self.g == (x, y):
                    self.s = x, y
                    self.reset_data()
                    self.run()
            elif QMouseEvent.buttons() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.ControlModifier:
                if not self.s == (x, y):
                    self.g = x, y
                    self.reset_data()
                    self.run()
            elif QMouseEvent.buttons() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.NoModifier:
                if not self.s == (x, y) and not self.g == (x, y):
                    if (x, y) not in self.graph.walls:
                        self.graph.walls.append((x, y))
                    else:
                        self.graph.walls.remove((x, y))
                    self.reset_data()
            elif QMouseEvent.buttons() == Qt.RightButton and QMouseEvent.modifiers() == Qt.NoModifier:
                if not self.s == (x, y) and not self.g == (x, y):
                    if (x, y) in self.graph.walls:
                        self.graph.walls.remove((x, y))
                        self.reset_data()
            self.update()

    def mouseMoveEvent(self, QMouseEvent):
        x, y = (QMouseEvent.pos().x() - self.offset) // self.size, \
               (QMouseEvent.pos().y() - self.offset) // self.size
        if 0 <= x < self.w and 0 <= y < self.h:
            self.selected = x, y
            if QMouseEvent.buttons() == Qt.LeftButton:
                if not self.s == (x, y) and not self.g == (x, y):
                    if (x, y) not in self.graph.walls:
                        self.graph.walls.append((x, y))
            elif QMouseEvent.buttons() == Qt.RightButton:
                if not self.s == (x, y) and not self.g == (x, y):
                    if (x, y) in self.graph.walls:
                        self.graph.walls.remove((x, y))
            self.update()

    def run(self):
        self.running = True
        self.reset_data()

        if self.show_astar.isChecked():
            t1 = threading.Thread(target=aStar, args=(self.graph, self.s, self.g,
                                                      self.diagonals_check.isChecked(), self))
            t1.start()

        if self.show_dijkstra.isChecked():
            t2 = threading.Thread(target=aStar, args=(self.graph, self.s, self.g,
                                                      self.diagonals_check.isChecked(), self, True))
            t2.start()

        if self.show_bfs.isChecked():
            t3 = threading.Thread(target=bfs, args=(self.graph, self.s, self.g,
                                                    self.diagonals_check.isChecked(), self))
            t3.start()

        self.update()

    def clear_walls(self):
        self.graph.walls = []
        self.reset_data()
        self.update()

    def reset_data(self):
        """Resets the paths and visited cells"""
        self.path_ASTAR = []
        self.path_DIJKSTRA = []
        self.path_BFS = []
        self.visited_nodes = dict()
