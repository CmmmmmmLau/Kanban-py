from PySide6.QtGui import QPalette, QTextCharFormat
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QCalendarWidget, QWidget, QHBoxLayout, QLabel, QCheckBox, QGridLayout


class DateCalendar(QCalendarWidget):
    StartDateChange = Signal()
    EndDateChange = Signal()

    def __init__(self):
        super().__init__()
        self.StartDate = None
        self.EndDate = None

        self.highlightFormat = QTextCharFormat()
        self.highlightFormat.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlightFormat.setForeground(self.palette().color(QPalette.HighlightedText))

        self.clicked.connect(self.DateIsClicked)
        print(super().dateTextFormat())

    def RangeSelected(self, format):
        if self.StartDate and self.EndDate:
            d0 = min(self.StartDate, self.EndDate)
            d1 = max(self.StartDate, self.EndDate)
            while d0 <= d1:
                self.setDateTextFormat(d0, format)
                d0 = d0.addDays(1)

    def DateIsClicked(self, date):
        self.RangeSelected(QTextCharFormat())
        if QApplication.instance().keyboardModifiers() & Qt.ShiftModifier and self.StartDate:
            self.EndDate = date
            self.EndDateChange.emit()
            self.RangeSelected(self.highlightFormat)
        else:
            self.StartDateChange.emit()
            self.StartDate = date
            self.EndDate = None


class DateCheckBox(QWidget):
    def __init__(self, text, date: list, index=0):
        super(DateCheckBox, self).__init__()

        self.date = date
        self.text = text
        self.index = index

        self.checkBox = QCheckBox()
        self.checkBox.clicked.connect(self.on_box_check)
        self.dateLabel = QLabel(self.text + " DD/MM/YYYY")
        self.dateLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.dateLabel.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.checkBox, 0, 0)
        layout.addWidget(self.dateLabel, 0, 1, -1, -1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def on_box_check(self):
        self.dateLabel.setEnabled(self.checkBox.isChecked())
        if self.checkBox.isChecked() is False:
            self.dateLabel.setText(self.text + " DD/MM/YYYY")
        else:
            self.dateLabel.setText(self.text + self.date[self.index])



if __name__ == "__main__":
    app = QApplication([])
    calendar = DateCalendar()
    calendar.show()
    app.exec()
