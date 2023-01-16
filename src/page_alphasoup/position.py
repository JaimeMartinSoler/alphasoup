
class Position:

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self):
        return f"[{self.row}][{self.col}]"

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        return False

    def __hash__(self):
        return hash((self.row, self.col))

    def is_in(self, positions):
        for p in positions:
            if self == p:
                return True
        return False
