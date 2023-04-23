import sys
import time

from PySide6.QtCore import QMimeData, Signal, QDate
from PySide6.QtGui import Qt, QDropEvent, QMouseEvent, QDrag, QCloseEvent, QDragEnterEvent
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

from Board import Board
from Column import Column
from Task import Task
from db import buildXML
from utils import DateCheckBox, DateCalendar


class TaskDetail(QWidget):
    closeSignal = Signal()

    def __init__(self, task: Task):
        super(TaskDetail, self).__init__()
        self.setWindowTitle("Task Detail")
        self.setMinimumSize(700, 500)

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
        self.checkStart = DateCheckBox("Start Date:", self.task.date, 0, self.task.dateCheckStatus[0])
        self.checkStart.OnCheck.connect(self.OnChecked)
        self.checkEnd = DateCheckBox("End Date:", self.task.date, 1, self.task.dateCheckStatus[1])
        self.checkStart.OnCheck.connect(self.OnChecked)
        self.calender = DateCalendar()
        self.setDate()
        self.calender.RangeSelected(self.calender.highlightFormat)
        self.calender.StartDateChange.connect(self.OnStartDateChange)
        self.calender.EndDateChange.connect(self.OnEndDateChange)

        # Layout
        LHSLayout = QGridLayout()
        LHSLayout.addWidget(self.titleLabel, 0, 0)
        LHSLayout.addWidget(self.checkStart, 1, 0)
        LHSLayout.addWidget(self.checkEnd, 1, 1)
        LHSLayout.addWidget(self.calender, 2, 0, -1, -1)

        RHSLayout = QVBoxLayout()
        RHSLayout.addWidget(descriptionLabel)
        RHSLayout.addWidget(self.descriptionEdit)
        RHSLayout.addWidget(MovementHistoryLabel)
        RHSLayout.addWidget(self.MovementHistoryList)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(LHSLayout)
        mainLayout.addLayout(RHSLayout)

        self.setLayout(mainLayout)

    def InitHistoryItem(self, hisList: list):
        for i in hisList:
            his_item = QListWidgetItem(i)
            self.MovementHistoryList.addItem(his_item)

    def OnContentChange(self):
        self.task.describe = self.descriptionEdit.toPlainText()

    def OnTitleChange(self):
        self.task.title = self.titleLabel.text()

    def OnStartDateChange(self):
        self.task.date[0] = str(self.calender.selectedDate().day()) + "/" \
                            + str(self.calender.selectedDate().month()) + "/" \
                            + str(self.calender.selectedDate().year())

        if self.checkStart.isChecked():
            self.checkStart.OnBoxCheck()

    def OnChecked(self):
        self.task.dateCheckStatus[0] = int(self.checkStart.isChecked())
        self.task.dateCheckStatus[1] = int(self.checkEnd.isChecked())

    def OnEndDateChange(self):
        self.task.date[1] = str(self.calender.selectedDate().day()) + "/" \
                            + str(self.calender.selectedDate().month()) + "/" \
                            + str(self.calender.selectedDate().year())

        if self.checkEnd.isChecked():
            self.checkEnd.OnBoxCheck()

    def setDate(self):
        date: str = self.task.date[0]
        if date:
            day, month, year = date.split("/")
            self.calender.StartDate = QDate(int(year), int(month), int(day))

        date: str = self.task.date[1]
        if date:
            day, month, year = date.split("/")
            self.calender.EndDate = QDate(int(year), int(month), int(day))

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
    def __init__(self, column: Column):
        super(TaskList, self).__init__()
        self.column = column

        self.setAcceptDrops(True)
        self.dragEnabled()
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.initList(self.column.taskList)

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
            parentBoard: SubBoard = self.parentWidget()
            _task.history.append(
                "Moved to " + parentBoard.titleLabel.text() + " on " + time.asctime(time.localtime(time.time())))
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
        self.taskList = TaskList(self.column)

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
            task.history.append("Created on " + time.asctime(time.localtime(time.time())))
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
        addButton = QPushButton("+")
        addButton.clicked.connect(self.add_column)

        # openFileButton = QPushButton("Open")
        # openFileButton.clicked.connect(self.OnOpenButtonClicked)
        saveFileButton = QPushButton("Save")
        saveFileButton.clicked.connect(self.OnSaveButtonClicked)
        # closeProjectButton = QPushButton("Close")
        # closeProjectButton.clicked.connect(self.OnCloseButtonClicked)

        # Title
        self.projectTitle = QLineEdit()
        self.projectTitle.textChanged.connect(self.OnTitleChange)
        self.projectTitle.setText(self.board.title)
        self.projectTitle.setFixedSize(200, 25)
        # Layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.projectTitle)

        self.boardLayout = QHBoxLayout()
        self.boardLayout.addWidget(addButton)

        toolbarLayout = QHBoxLayout()
        # toolbarLayout.addWidget(openFileButton)
        toolbarLayout.addWidget(saveFileButton)
        # toolbarLayout.addWidget(closeProjectButton)

        mainLayout.addLayout(self.boardLayout)
        mainLayout.addLayout(toolbarLayout)

        self.setLayout(mainLayout)

    def InitColumn(self):
        for i in self.board.columnList:
            insColumn = i
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
            index += 1

    def OnSaveButtonClicked(self):
        allBoard = self.findChildren(SubBoard)
        for i in allBoard:
            subBoard: SubBoard = i
            subBoard.column.taskList = subBoard.taskList.buildTaskList()
        buildXML(self.board)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if isinstance(event.source(), SubBoard):
            event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        pos = event.position().toPoint()

        widget: SubBoard = event.source()

        subLayout = self.layout().itemAt(1)
        widgetIndex = -1
        for i in range(subLayout.count()):
            if subLayout.itemAt(i).geometry().contains(pos):
                widgetIndex = i

        if widgetIndex >= 0:
            index = min(widgetIndex, subLayout.count() - 1)
            subLayout.insertWidget(index, widget)

        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()

    def OnTitleChange(self):
        self.board.title = self.projectTitle.text()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainBoard(Board("Title"))
    window.show()

    sys.exit(app.exec())
