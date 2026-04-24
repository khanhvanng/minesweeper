import random
import pygame
import sys

direction = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1), (1, -1), (-1, 1)]

class Cell():
    '''
    Lớp đại diện cho một ô vuông trên bảng Dò Mìn.
    
    Attributes:
        isMine (bool): Trạng thái ô có chứa mìn hay không (True = có mìn).
        isRevealed (bool): Trạng thái ô đã được người chơi mở hay chưa.
        isFlagged (bool): Trạng thái ô đã bị cắm cờ nghi ngờ có mìn.
        neighbors (int): Số lượng mìn hiện diện trong 8 ô lân cận (từ 0 đến 8).
    '''
    def __init__(self):
        self.isMine = False
        self.isRevealed = False
        self.isFlagged = False
        self.neighbors = 0

class Board():
    '''
    Lớp đại diện cho bảng Dò mìn.

    Attributes:
        rows (int): Số hàng trong bảng chơi.
        cols (int): Số cột trong bảng chơi.
        num (int): Số lượng mìn được rải vào bảng chơi.
        grid (list): Mảng 2 chiều chứa các đối tượng Cell đại diện cho bàn cờ.
    '''
    def __init__(self, rows, cols, num):
        '''
        Khởi tạo bảng chơi với kích thước và số lượng mìn chỉ định.
        
        Args:
            rows (int): Số hàng của bảng.
            cols (int): Số cột của bảng.
            num (int): Tổng số mìn cần rải.
        '''
        self.rows = rows
        self.cols = cols
        self.num = num
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

    def place_mines(self, first_row, first_col):
        '''
        Rải mìn ngẫu nhiên lên bảng chơi. Tránh ô được chọn đầu tiên
        và 8 ô lân cận để đảm bảo người chơi có đủ dữ kiện để giải màn chơi.

        Args:
            first_row (int): Tọa độ hàng của ô được chọn đầu tiên.
            first_col (int): Tọa độ cột của ô được chọn đầu tiên.
        
        Returns:
            None. Gọi hàm calculate_neighbors sau khi rải xong.
        '''
        mines_placed = 0
        while mines_placed < self.num:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            if abs(r - first_row) <= 1 and abs(c - first_col) <= 1:
                continue

            if r == first_row and c == first_col:
                continue

            if self.grid[r][c].isMine:
                continue

            self.grid[r][c].isMine = True
            mines_placed += 1

        self.calculate_neighbors()

    def calculate_neighbors(self):
        '''
        Duyệt qua toàn bộ bảng chơi để đếm và gán số lượng mìn xung quanh 
        (từ 0-8) cho từng ô không chứa mìn.
        
        Returns:
            None. Cập nhật thuộc tính 'neighbors' cho các đối tượng Cell.
        '''      
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

    def reveal(self, r, c):
        '''
        Xử lý logic khi người chơi mở một ô. Sử dụng thuật toán đệ quy
        Flood Fill (DFS) để tự động mở lan truyền các ô an toàn lân cận 
        nếu ô hiện tại có số mìn xung quanh là 0.

        Args:
            r (int): Tọa độ hàng của ô cần mở.
            c (int): Tọa độ cột của ô cần mở.
            
        Returns:
            None. Cập nhật trạng thái 'isRevealed' của các ô hoặc in ra 
            "You lose" nếu trúng mìn.
        '''
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return
        
        cell = self.grid[r][c]

        if cell.isRevealed or cell.isFlagged:
            return
        
        cell.isRevealed = True

        if cell.isMine:
            print("You lose")
            return
        
        if cell.neighbors == 0:
            for dr, dc in direction:
                self.reveal(r + dr, c + dc)

