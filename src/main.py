import sys, os

from PySide6.QtWidgets import QApplication, QMessageBox, QMainWindow, QHBoxLayout, QWidget
from gui import MainBoard, Board
from db import buildXML, parserXML

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        if os.path.exists("project.xml"):
            board = parserXML("project.xml")
            boardWindow = MainBoard(board)
            layout.addWidget(boardWindow)
        else:
            reply = QMessageBox.question(self, "", "Project file not found. Load template?", QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                board = parserXML("template.xml")
                boardWindow = MainBoard(board)
                layout.addWidget(boardWindow)
            else:
                boardWindow = MainBoard(Board("New Project"))
                layout.addWidget(boardWindow)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.adjustSize()

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("Fusion")
    window = MainWindow()
    screen_size = QApplication.primaryScreen().availableSize()
    window.resize(screen_size.width() / 3, screen_size.height() / 2)
    window.show()
    app.exec()
