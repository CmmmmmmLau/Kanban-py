import random
import sys

from PySide6.QtCore import QMimeData, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QTextEdit,
    QListWidget,
    QFrame,
    QListWidgetItem,
    QVBoxLayout,
    QAbstractItemView,
    QPushButton,
    QHBoxLayout,
    QApplication,
    QGridLayout,
    QLineEdit,
    QSpinBox,
    QMessageBox
)
from PySide6.QtGui import Qt, QDropEvent, QMouseEvent, QDrag, QCloseEvent, QDragEnterEvent
from src.board.Task import Task
from src.board.Column import Column
from src.board.Board import Board
from src.gui.utils import DateCheckBox, DateCalendar


class TaskDetail(QWidget):
    closeSignal = Signal()

    def __init__(self, task: Task):
        super(TaskDetail, self).__init__()

        self.task = task

        self.init_UI()
        self.InitHistoryItem(self.task.history)

    def init_UI(self):
        # Description
        descriptionLabel = QLabel("Description:")
        self.descriptionEdit = QTextEdit()
        self.descriptionEdit.setPlainText(self.task.describe)
        self.descriptionEdit.textChanged.connect(self.OnContentChange)

        # Movement History
        MovementHistoryLabel = QLabel("Movement History:")
        self.MovementHistoryList = QListWidget()

        # LHS Widget
        self.titleLabel = QLineEdit(self.task.title)
        self.titleLabel.textChanged.connect(self.OnTitleChange)
        checkStart = DateCheckBox("Start Date:", self.task.Date, 0)
        checkEnd = DateCheckBox("End Date:", self.task.Date, 1)
        self.calender = DateCalendar()
        self.calender.StartDateChange.connect(self.OnStartDateChange)
        self.calender.EndDateChange.connect(self.OnEndDateChange)

        # Layout
        LHS_layout = QGridLayout()
        LHS_layout.addWidget(self.titleLabel, 0, 0)
        LHS_layout.addWidget(checkStart, 1, 0)
        LHS_layout.addWidget(checkEnd, 1, 1)
        LHS_layout.addWidget(self.calender, 2, 0, -1, -1)

        RHS_layout = QVBoxLayout()
        RHS_layout.addWidget(descriptionLabel)
        RHS_layout.addWidget(self.descriptionEdit)
        RHS_layout.addWidget(MovementHistoryLabel)
        RHS_layout.addWidget(self.MovementHistoryList)

        main_layout = QHBoxLayout()
        main_layout.addLayout(LHS_layout)
        main_layout.addLayout(RHS_layout)

        self.setLayout(main_layout)

    def InitHistoryItem(self, hisList: list):
        for i in hisList:
            his_item = QListWidgetItem(i)
            self.MovementHistoryList.addItem(his_item)

    def OnContentChange(self):
        self.task.describe = self.descriptionEdit.toPlainText()

    def OnTitleChange(self):
        self.task.title = self.titleLabel.text()

    def OnStartDateChange(self):
        self.task.Date[0] = str(self.calender.selectedDate().day()) + "/" \
                            + str(self.calender.selectedDate().month()) + "/" \
                            + str(self.calender.selectedDate().year())

    def OnEndDateChange(self):
        self.task.Date[1] = str(self.calender.selectedDate().day()) + "/" \
                            + str(self.calender.selectedDate().month()) + "/" \
                            + str(self.calender.selectedDate().year())

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closeSignal.emit()
        super().closeEvent(event)


class TaskCard(QWidget):

    def __init__(self, task: Task):
        super().__init__()

        self.task = task

        self.titleLabel = QLabel(task.title)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.taskDetail = TaskDetail(self.task)
        self.taskDetail.closeSignal.connect(lambda: self.titleLabel.setText(self.task.title))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.titleLabel)
        self.setLayout(layout)

    def mouseDoubleClickEvent(self, event) -> None:
        self.taskDetail.show()
        super(TaskCard, self).mouseDoubleClickEvent(event)


class TaskList(QListWidget):
    def __init__(self, taskList: list):
        super(TaskList, self).__init__()
        self.taskList = taskList

        self.setAcceptDrops(True)
        self.dragEnabled()
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.initList(self.taskList)

        self.taskList = self.buildTaskList()

    def initList(self, list: list):
        for i in list:
            item = QListWidgetItem()
            itemWidget = TaskCard(i)
            item.setSizeHint(itemWidget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, itemWidget)

    def dropEvent(self, event: QDropEvent) -> None:
        source: TaskList = event.source()
        item: QListWidgetItem = source.currentItem()
        itemWidget: TaskCard = source.itemWidget(item)
        _task = itemWidget.task
        if _task is None:
            _task = Task()
        if source != self:
            item = source.takeItem(source.currentRow())
            self.addItem(item)
            self.setItemWidget(item, TaskCard(_task))
            event.setDropAction(Qt.DropAction.TargetMoveAction)
        else:
            event.setDropAction(Qt.DropAction.MoveAction)

        super().dropEvent(event)

    def buildTaskList(self):
        list = []
        for i in range(self.count()):
            task: TaskCard = self.itemWidget(self.item(i))
            if task:
                list.append(task.task)

        return list


class SubBoard(QFrame):
    DestroySignal = Signal()

    # columnIndex = 0

    def __init__(self, column: Column):
        super(SubBoard, self).__init__()

        self.column = column
        # self.index = SubBoard.columnIndex
        # SubBoard.columnIndex += 1

        self.init_ui(self.column)

    def init_ui(self, column: Column):
        # Button Widgets
        self.addButton = QPushButton("add")
        self.delButton = QPushButton("del")
        self.destroyButton = QPushButton("destroy")
        # Connect the signal
        self.addButton.clicked.connect(self.AddButtonClicked)
        self.delButton.clicked.connect(self.DelButtonClicked)
        self.destroyButton.clicked.connect(self.DestroyButtonClicked)

        # Column label
        self.titleLabel = QLineEdit(column.title)
        self.titleLabel.textChanged.connect(self.ColumnTitleChanged)
        self.wip = QSpinBox()
        self.wip.setFixedSize(50, 30)
        self.wip.textChanged.connect(self.WIPChanged)

        # Task List
        self.taskList = TaskList(column.taskList)

        # Main layout
        layout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        labelLayout = QHBoxLayout()
        layout.addLayout(labelLayout)
        layout.addWidget(self.taskList)
        layout.addLayout(buttonLayout)
        # Label Layout
        labelLayout.addWidget(self.titleLabel)
        labelLayout.addWidget(self.wip)
        # Button layout
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.delButton)
        buttonLayout.addWidget(self.destroyButton)

        self.setLayout(layout)

    def AddButtonClicked(self):
        if int(self.column.WIPLimit) == 0 or self.taskList.count() < int(self.column.WIPLimit):
            item = QListWidgetItem()
            task = Task()
            itemWidget = TaskCard(task)
            item.setSizeHint(itemWidget.sizeHint())
            self.column.taskList.append(task)
            self.taskList.addItem(item)
            self.taskList.setItemWidget(item, itemWidget)
            self.column.taskList = self.taskList.buildTaskList()

        else:
            dialog = QMessageBox()
            dialog.setWindowTitle("Task add fail!")
            dialog.setText("Maximum Reached!")
            dialog.exec()

    def DelButtonClicked(self):
        selectedItems = self.taskList.selectedItems()
        if selectedItems:
            for item in selectedItems:
                self.taskList.takeItem(self.taskList.row(item))
            self.column.taskList = self.taskList.buildTaskList()

    def DestroyButtonClicked(self):
        # for index in reversed(range(self.layout().count() - 1)):
        #     self.layout().takeAt(index).widget().deleteLater()
        self.column = None
        self.deleteLater()
        self.DestroySignal.emit()

    def WIPChanged(self):
        self.column.WIPLimit = self.wip.text()

    def ColumnTitleChanged(self):
        self.column.title = self.titleLabel.text()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            widgetImage = self.grab()
            mimeData = QMimeData()
            drag.setMimeData(mimeData)
            drag.setPixmap(widgetImage)
            drag.setHotSpot(event.position().toPoint() - self.rect().topLeft())
            drag.exec()

        super().mouseMoveEvent(event)


class MainBoard(QWidget):
    def __init__(self, board: Board):
        super().__init__()

        self.board = board

        self.setAcceptDrops(True)

        self.InitUI()
        self.InitColumn()

    def InitUI(self):
        # Button
        add_button = QPushButton("+")
        add_button.clicked.connect(self.add_column)

        open_file_button = QPushButton("open")
        save_file_button = QPushButton("save")
        close_project_button = QPushButton("close")

        # Layout
        main_layout = QVBoxLayout()

        self.boardLayout = QHBoxLayout()
        self.boardLayout.addWidget(add_button)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(open_file_button)
        toolbar_layout.addWidget(save_file_button)
        toolbar_layout.addWidget(close_project_button)

        main_layout.addLayout(self.boardLayout)
        main_layout.addLayout(toolbar_layout)

        self.setLayout(main_layout)

    def InitColumn(self):
        for i in self.board.columnList:
            insColumn = Column(i.title)
            columnWidget = SubBoard(insColumn)
            columnWidget.DestroySignal.connect(self.ColumnDel)
            self.boardLayout.insertWidget(self.boardLayout.count() - 1, columnWidget)

    def add_column(self):
        insColumn = Column()
        columnWidget = SubBoard(insColumn)
        columnWidget.DestroySignal.connect(self.ColumnDel)
        self.board.columnList.append(insColumn)
        self.boardLayout.insertWidget(self.boardLayout.count() - 1, columnWidget)

    def ColumnDel(self):
        allWidget = self.findChildren(SubBoard)
        index = 0
        for i in allWidget:
            if self.sender() == i:
                self.board.columnList.pop(index)
                board: SubBoard = i
                print("Found!")
                print(board.titleLabel.text())
                print()
            index += 1

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if isinstance(event.source(), SubBoard):
            event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        pos = event.position().toPoint()

        widget: SubBoard = event.source()

        subLayout = self.layout().itemAt(0)
        widgetIndex = -1
        for i in range(subLayout.count()):
            if subLayout.itemAt(i).geometry().contains(pos):
                widgetIndex = i

        if widgetIndex >= 0:
            index = min(widgetIndex, subLayout.count() - 1)
            subLayout.insertWidget(index, widget)

        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainBoard(Board("Title"))
    window.show()

    sys.exit(app.exec())
