from src.Task import Task


class Column:
    def __init__(self, title="Column name", WIPLimit=0):
        self.title = title
        self.WIPLimit = WIPLimit
        self.taskList = []
