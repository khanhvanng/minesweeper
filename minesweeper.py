import random

class Cell():
    def __init__(self):
        self.isMine = False
        self.isRevealed = False
        self.isFlagged = False
        self.neighbors = 0
    
class Board():
    def __init__(self, rows, cols,num):
        self.rows = rows
        self.cols = cols
        self.num = num
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

    def place_mines(self, first_row, first_col):
        mines_placed = 0
        while mines_placed < self.num:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
        
            if r == first_row and c == first_col:
                continue

            if self.grid[r][c].isMine:
                continue

            self.grid[r][c].isMine = True
            mines_placed += 1

        self.calculate_neighbors()

    def calculate_neighbors(self):
        direction = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1), (1, -1), (-1, 1)]
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].isMine:
                    continue
        
                count = 0
                for dr, dc in direction:
                    nr = dr + r
                    nc = dc + c
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if self.grid[nr][nc].isMine:
                            count += 1
                
                self.grid[r][c].neighbors = count
