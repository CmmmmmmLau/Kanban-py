from src.Task import Task


class Column:
    def __init__(self, title="Column name", WIPLimit=0):
        self.title = title
        self.WIPLimit = WIPLimit
        self.taskList = []

    def addTask(self, task: Task):
        self.taskList[task.id] = task

    def removeTask(self, target):
        del self.taskList[target]
