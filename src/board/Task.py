import time


class Task:
    totalTask = 1

    def __init__(self, title="Task's title", describe="description", priority=1,
                 startDate="", endDate=""):
        self.title = title
        self.describe = describe
        self.priority = priority
        self.Date = [startDate, endDate]
        self.history = []
        self.id = Task.totalTask
        Task.totalTask += 1
        print(self.id)