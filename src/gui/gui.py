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
    QCalendarWidget,
    QDialog
)
from PySide6.QtGui import Qt, QDropEvent, QMouseEvent, QDrag, QCloseEvent
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

        self.task_detail = TaskDetail(self.task)
        self.task_detail.closeSignal.connect(lambda: self.titleLabel.setText(self.task.title))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.titleLabel)
        self.setLayout(layout)

    def mouseDoubleClickEvent(self, event) -> None:
        self.task_detail.show()
        super(TaskCard, self).mouseDoubleClickEvent(event)


class TaskList(QListWidget):
    def __init__(self):
        super(TaskList, self).__init__()

        self.setAcceptDrops(True)
        self.dragEnabled()
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

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
            event.setDropAction(Qt.DropAction.IgnoreAction)
        else:
            event.setDropAction(Qt.DropAction.MoveAction)
        super().dropEvent(event)


class SubBoard(QFrame):
    def __init__(self, column: Column):
        super(SubBoard, self).__init__()

        self.column = column

        self.init_ui(self.column)
        self.init_list()

    def init_ui(self, column: Column):
        # Button Widgets
        self.add_button = QPushButton("add")
        self.del_button = QPushButton("del")
        self.destroy_button = QPushButton("destroy")
        # Connect the signal
        self.add_button.clicked.connect(self.add_button_clicked)
        self.del_button.clicked.connect(self.del_button_clicked)
        self.destroy_button.clicked.connect(self.destory_button_clicked)

        # Column labe
        self.title_label = QLabel(column.title)

        # Task List
        self.task_list = TaskList()

        # Main layout
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.task_list)
        # Button layout
        layout.addLayout(button_layout)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.del_button)
        button_layout.addWidget(self.destroy_button)

        self.setLayout(layout)

    def init_list(self):
        for i in self.column.taskList:
            item = QListWidgetItem()
            itemWidget = TaskCard(i)
            item.setSizeHint(itemWidget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, itemWidget)

    def add_button_clicked(self):
        item = QListWidgetItem()
        itemWidget = TaskCard(Task())
        item.setSizeHint(itemWidget.sizeHint())
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, itemWidget)

    def del_button_clicked(self):
        selected_items = self.task_list.selectedItems()
        if selected_items:
            for item in selected_items:
                self.task_list.takeItem(self.task_list.row(item))

    def destory_button_clicked(self):
        for index in reversed(range(self.layout().count() - 1)):
            self.layout().takeAt(index).widget().deleteLater()

        self.deleteLater()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            widget_image = self.grab()
            mimedata = QMimeData()
            drag.setMimeData(mimedata)
            drag.setPixmap(widget_image)
            drag.setHotSpot(event.position().toPoint() - self.rect().topLeft())
            drag.exec()

        super().mouseMoveEvent(event)


class MainBoard(QWidget):
    def __init__(self, board: Board):
        super().__init__()

        self.board = board

        self.init_UI()
        self.init_column()

    def init_UI(self):
        # Button
        add_button = QPushButton("+")
        add_button.clicked.connect(self.add_column)

        open_file_button = QPushButton("open")
        save_file_button = QPushButton("save")
        close_project_button = QPushButton("close")

        # Layout
        main_layout = QVBoxLayout()

        self.board_layout = QHBoxLayout()
        self.board_layout.addWidget(add_button)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(open_file_button)
        toolbar_layout.addWidget(save_file_button)
        toolbar_layout.addWidget(close_project_button)

        main_layout.addLayout(self.board_layout)
        main_layout.addLayout(toolbar_layout)

        self.setLayout(main_layout)

    def init_column(self):
        for i in self.board.columnList:
            ins_column = Column(i.title)
            column_widget = SubBoard(ins_column)
            self.board_layout.insertWidget(self.board_layout.count() - 1, column_widget)

    def add_column(self):
        ins_column = Column()
        column_widget = SubBoard(ins_column)

        self.board_layout.insertWidget(self.board_layout.count() - 1, column_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainBoard(Board("Title"))
    window.show()

    sys.exit(app.exec())
