from typing import List
from src.board.Column import Column


class Board:
    def __init__(self, title):
        self.title = title
        self.columnList = []
