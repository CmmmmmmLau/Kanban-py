from Column import Column
from Task import Task


class Board:
    def __init__(self, title):
        self.title = title
        self.columnList = []
def template():
    TODO = Column("TODO")
    task1 = Task("Task 1", "Description of task 1")
    TODO.taskList.append(task1)

    In_Progress = Column("In Progress")
    task2 = Task("Task 2", "Description of task 2")
    task3 = Task("Task 3", "Description of task 3")
    In_Progress.taskList.append(task3)
    In_Progress.taskList.append(task2)

    Done = Column("Done")

    board = Board("Template Board")
    board.columnList.append(TODO)
    board.columnList.append(In_Progress)
    board.columnList.append(Done)

    return board
