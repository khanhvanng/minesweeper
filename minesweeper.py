import random
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window

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
        lives (int): Số mạng sống hiện tại của người chơi.
        game_over (bool): Trạng thái kết thúc trò chơi.
        is_win (bool): Trạng thái người chơi đã chiến thắng hay chưa.
    '''
    def __init__(self, rows, cols, num, lives = 3):
        '''
        Khởi tạo bảng chơi với kích thước và số lượng mìn chỉ định.
        
        Args:
            rows (int): Số hàng của bảng.
            cols (int): Số cột của bảng.
            num (int): Tổng số mìn cần rải.
            lives (int): Số mạng sống khởi đầu (mặc định là 3).
        '''
        self.rows = rows
        self.cols = cols
        self.num = num
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

        self.lives = lives
        self.game_over = False
        self.is_win = False

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
        Quản lý trừ mạng nếu trúng mìn.

        Args:
            r (int): Tọa độ hàng của ô cần mở.
            c (int): Tọa độ cột của ô cần mở.
            
        Returns:
            None. Cập nhật trạng thái 'isRevealed' của các ô
            và trừ 'lives' nếu trúng mìn.
        '''
        if self.game_over:
            return
        
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return
        
        cell = self.grid[r][c]

        if cell.isRevealed or cell.isFlagged:
            return
        
        cell.isRevealed = True

        if cell.isMine:
            self.lives -= 1
            if self.lives < 0:
                self.game_over = True
                self.is_win = False
                self.reveal_all()
            return
        
        if cell.neighbors == 0:
            for dr, dc in direction:
                self.reveal(r + dr, c + dc)

    def reveal_safe_around(self, r, c):
        '''
        Hàm tự động lật mở tất cả các ô lân cận, nếu số cờ xung quanh
        hay số mìn đã mở bằng đúng neighbors của ô hiện tại.

        Args:
            r (int): Tọa độ hàng của ô được chọn.
            c (int): Tọa độ cột của ô được chọn. 
        '''
        if self.game_over:
            return
            
        cell = self.grid[r][c]
        
        if not cell.isRevealed or cell.neighbors == 0:
            return

        opened_mines = 0
        flag_count = 0
        for dr, dc in direction:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr][nc].isFlagged:
                    flag_count += 1
                elif self.grid[nr][nc].isMine and self.grid[nr][nc].isRevealed:
                    opened_mines += 1

        if (flag_count == cell.neighbors) or (flag_count + opened_mines == cell.neighbors):
            for dr, dc in direction:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbor_cell = self.grid[nr][nc]
                    if not neighbor_cell.isRevealed and not neighbor_cell.isFlagged:
                        self.reveal(nr, nc)

    def check_win(self):
        '''
        Kiểm tra điều kiện chiến thắng của trò chơi.
        Người chơi thắng khi tổng số ô đã mở bằng đúng tổng số ô an toàn trên bảng.
        
        Returns:
            None. Cập nhật trạng thái 'is_win' và 'game_over' thành True nếu thắng.
        '''
        if self.game_over:
            return
        
        revealed_count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].isRevealed and not self.grid[r][c].isMine:
                    revealed_count += 1
        
        target = self.rows * self.cols - self.num

        if revealed_count == target:
            self.game_over = True
            self.is_win = True
            self.reveal_all()

    def reveal_all(self):
        '''
        Lật mở toàn bộ các ô chứa mìn trên bàn cờ. 
        Được gọi khi trò chơi kết thúc (dù thắng hay thua).
        '''
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].isMine:
                    self.grid[r][c].isRevealed = True

class Constraint():
    def __init__(self, cells, mines):
        self.cells = set(cells)
        self.mines = mines

    def __eq__(self, other):
        return self.cells == other.cells and self.mines == other.mines

    def __hash__(self):
        return hash((frozenset(self.cells), self.mines))

    def is_empty(self):
        return len(self.cells) == 0
    
class MinesweeperAI():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
    
        self.knowledge = []
        self.safe = set()
        self.mines = set()
        self.processed = set()
    
    def add_knowledge(self, cell, number, board):
        r, c = cell

        self.safe.add(cell)

        unknown = set()
        remaining_mines = number

        for dr, dc in direction:
            nr, nc = r + dr, c + dc

            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbor = board.grid[nr][nc]
                
                if (nr, nc) in self.mines:
                    remaining_mines -= 1
                    
                elif not neighbor.isRevealed:
                    unknown.add((nr, nc))
        
        if len(unknown) > 0:
            new_constraint = Constraint(unknown, remaining_mines)

            if new_constraint not in self.knowledge:
                self.knowledge.append(new_constraint)
        
        self.infer()
    
    def infer(self):
        changed = True
        while changed:
            changed = False
        
            new_knowledge = []

            for c in self.knowledge:
                if c.mines == 0:
                    for cell in c.cells:
                        if cell not in self.safe:
                            self.safe.add(cell)
                            changed = True
                
                elif c.mines == len(c.cells):
                    for cell in c.cells:
                        if cell not in self.mines:
                            self.mines.add(cell)
                            changed = True

            for c in self.knowledge:
                new_cells = set()
                mines = c.mines

                for cell in c.cells:
                    if cell in self.mines:
                        mines -= 1
                    elif cell not in self.safe:
                        new_cells.add(cell)
                
                if len(new_cells) > 0 and 0 <= mines <= len(new_cells):
                    new_knowledge.append(Constraint(new_cells, mines))
            
            self.knowledge.extend(new_knowledge)
            self.knowledge = list(set(self.knowledge))

            new_constraints = []

            for c1 in self.knowledge:
                for c2 in self.knowledge:
                    if c1 == c2: continue
                    if c1.cells.issubset(c2.cells) and c1.mines <= c2.mines:
                        diff_cells = c2.cells - c1.cells
                        diff_mines = c2.mines - c1.mines
                        new_constraint = Constraint(diff_cells, diff_mines)

                        if (not new_constraint.is_empty() 
                            and new_constraint not in self.knowledge 
                            and new_constraint not in new_constraints):
                            new_constraints.append(new_constraint)
                            changed = True

            self.knowledge.extend(new_constraints)

            self.knowledge = [c for c in self.knowledge if not c.is_empty()]

            if not changed:
                if self.brute_force():
                    changed = True
                
    def get_hint(self, board):
        for r in range(self.rows):
            for c in range(self.cols):
                if board.grid[r][c].isFlagged and (r, c) in self.safe:
                    return ("wrong_flag", (r, c))
        
        for cell in self.safe:
            r, c = cell
            if not board.grid[r][c].isRevealed:
                return ("safe", (r, c))
            
        for cell in self.mines:
            r, c = cell
            if not board.grid[r][c].isFlagged and not board.grid[r][c].isRevealed:
                return ("mine", (r, c))
        
        return ("none", None)

    def brute_force(self):
        '''
        Thuật toán Vét cạn (Backtracking/Tank Solver).
        Gom các constraint giao nhau thành cụm, sinh các trường hợp đặt mìn,
        và lọc ra những ô luôn luôn là mìn hoặc luôn luôn an toàn.
        '''
        changed = False
        
        components = []
        unassigned = self.knowledge.copy()
        
        while unassigned:
            c = unassigned.pop(0)
            comp_cells = set(c.cells)
            comp_constraints = [c]
            
            added = True
            while added:
                added = False
                for other_c in unassigned[:]:
                    if comp_cells.intersection(other_c.cells):
                        comp_cells.update(other_c.cells)
                        comp_constraints.append(other_c)
                        unassigned.remove(other_c)
                        added = True
                        
            components.append((list(comp_cells), comp_constraints))
            
        for comp_cells, comp_constraints in components:
            if len(comp_cells) > 15:
                continue
                
            valid_assignments = []
            
            def backtrack(index, current_assignment):
                if index == len(comp_cells):
                    valid = True
                    for const in comp_constraints:
                        mines_in_const = sum(1 for i, cell in enumerate(comp_cells) 
                                             if cell in const.cells and current_assignment[i])
                        if mines_in_const != const.mines:
                            valid = False
                            break
                    
                    if valid:
                        valid_assignments.append(current_assignment.copy())
                    return
                
                current_assignment[index] = True
                backtrack(index + 1, current_assignment)
                
                current_assignment[index] = False
                backtrack(index + 1, current_assignment)
                
            backtrack(0, [False] * len(comp_cells))
            
            if valid_assignments:
                for i, cell in enumerate(comp_cells):
                    is_always_mine = all(assign[i] == True for assign in valid_assignments)
                    
                    is_always_safe = all(assign[i] == False for assign in valid_assignments)
                    
                    if is_always_mine and cell not in self.mines:
                        self.mines.add(cell)
                        changed = True
                    if is_always_safe and cell not in self.safe:
                        self.safe.add(cell)
                        changed = True
                        
        return changed
    
class CellUI(Button):
    '''
    Lớp giao diện đại diện cho một nút bấm (ô) trên màn hình.
    Kế thừa từ Button của thư viện Kivy.
    '''
    def __init__(self, logic_cell, r, c, app_ref, **kwargs):
        '''
        Khởi tạo nút bấm và liên kết nó với một đối tượng Cell logic.
        
        Args:
            logic_cell (Cell): Đối tượng chứa dữ liệu logic của ô này.
            r (int): Tọa độ hàng của ô trên lưới.
            c (int): Tọa độ cột của ô trên lưới.
            app_ref (MinesweeperApp): Tham chiếu đến ứng dụng gốc để gọi ngược lại.
        '''
        super().__init__(**kwargs)
        self.logic_cell = logic_cell
        self.r = r
        self.c = c
        self.app_ref = app_ref
        
        self.font_size = 24
        self.bold = True
        self.background_color = [0.8, 0.8, 0.8, 1]
    
    def on_touch_down(self, touch):
        '''
        Xử lý sự kiện khi người chơi click chuột phải (cắm/rút cờ).
        '''
        if self.collide_point(touch.x, touch.y):
            if 'button' in touch.profile and touch.button == 'right':
                if not self.logic_cell.isRevealed:
                    self.logic_cell.isFlagged = not self.logic_cell.isFlagged
                    self.update_display()
                return True 
                
        return super().on_touch_down(touch)

    def on_release(self):
        '''
        Xử lý sự kiện khi người chơi click chuột trái.
        Gửi yêu cầu mở ô về cho ứng dụng gốc nếu ô chưa bị cắm cờ.
        '''
        if self.logic_cell.isFlagged:
            return
            
        if not self.logic_cell.isRevealed:
            self.app_ref.handle_click(self.r, self.c)
            
        elif self.logic_cell.neighbors > 0:
            self.app_ref.handle_chord(self.r, self.c)

    def update_display(self):
        '''
        Đồng bộ giao diện của nút bấm dựa trên trạng thái hiện tại của logic_cell.
        Đổi màu nền đỏ nếu có mìn, hiện số nếu an toàn, hoặc hiện chữ 'F' nếu cắm cờ.
        '''
        if self.logic_cell.isRevealed:
            if self.logic_cell.isMine:
                self.background_color = [1, 0, 0, 1]
                self.text = "*"
            else:
                self.background_color = [1, 1, 1, 1] 
                self.text = str(self.logic_cell.neighbors) if self.logic_cell.neighbors > 0 else ""
        else:
            if self.logic_cell.isFlagged:
                self.background_color = [1, 1, 0, 1] 
                self.text = "F" 
                self.color = [0, 0, 0, 1]
            else:
                self.background_color = [0.8, 0.8, 0.8, 1]
                self.text = ""

class MinesweeperApp(App):
    '''
    Lớp ứng dụng cốt lõi (Controller). Quản lý vòng đời trò chơi, 
    khởi tạo giao diện và xử lý tương tác tổng thể.
    '''
    def build(self):
        '''
        Khởi tạo hệ thống giao diện và kết nối các phần tử UI với Logic.
        
        Returns:
            BoxLayout: Trả về khung bố cục gốc (chứa nhãn mạng sống và lưới game).
        '''
        self.game_rows = 8
        self.game_cols = 8
        self.num_mines = 10

        self.game_board = Board(self.game_rows, self.game_cols, self.num_mines, lives=3)
        self.is_first_click = True
        self.ui_grid = []
        self.ai = MinesweeperAI(self.game_rows, self.game_cols)
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=15)
        
        self.lives_label = Label(
            text=f"Mạng sống: {self.game_board.lives}", 
            font_size=24,
            bold=True
        )
        top_bar.add_widget(self.lives_label)

        hint_btn = Button(
            text="Gợi ý",
            font_size=20, 
            bold=True, 
            size_hint=(0.4, 1) 
        )
        hint_btn.bind(on_release=self.give_hint)
        top_bar.add_widget(hint_btn)
        
        main_layout.add_widget(top_bar)

        self.hint_message = Label(
            text="Trò chơi bắt đầu! AI đang theo dõi...", 
            font_size=18, 
            color=[1, 1, 0, 1], 
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(self.hint_message)

        root = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.85))
        self.board_layout = GridLayout(cols=self.game_cols, rows=self.game_rows, size_hint=(None, None))
        
        self.update_board_size()
        Window.bind(on_resize=self.update_board_size)
        
        for r in range(self.game_rows):
            ui_row = []
            for c in range(self.game_cols):
                logic = self.game_board.grid[r][c]
                btn = CellUI(logic_cell=logic, r=r, c=c, app_ref=self)
                self.board_layout.add_widget(btn)
                ui_row.append(btn)
            self.ui_grid.append(ui_row)
            
        root.add_widget(self.board_layout)
        main_layout.add_widget(root) 
        
        return main_layout

    def give_hint(self, instance):
        if self.game_board.game_over:
            return

        self.sync_ui_with_logic()

        for r in range(self.game_rows):
            for c in range(self.game_cols):
                cell = self.game_board.grid[r][c]
                
                if cell.isRevealed and not cell.isMine and (r, c) not in self.ai.processed:
                    self.ai.add_knowledge((r, c), cell.neighbors, self.game_board)
                    self.ai.processed.add((r, c))

            if len(self.ai.mines) > 0:
                for mine_coords in self.ai.mines:
                    memory_constraint = Constraint([mine_coords], 1)
                    if memory_constraint not in self.ai.knowledge:
                        self.ai.knowledge.append(memory_constraint)           
        
                self.ai.infer()

        action, coords = self.ai.get_hint(self.game_board)
        
        if action == "safe":
            r, c = coords
            self.hint_message.text = f"AI suy luận: Ô ({r},{c}) an toàn tuyệt đối. Hãy mở nó!"
            self.ui_grid[r][c].background_color = [0, 1, 1, 1] 
            self.ui_grid[r][c].color = [0, 0, 0, 1]
            
        elif action == "mine":
            r, c = coords
            self.hint_message.text = f"AI cảnh báo: Ô ({r},{c}) 100% là mìn. Hãy cắm cờ!"
            self.ui_grid[r][c].background_color = [1, 0.5, 0, 1] 
            self.ui_grid[r][c].text = "!"
            self.ui_grid[r][c].color = [0, 0, 0, 1]
            
        elif action == "wrong_flag":
            r, c = coords
            self.hint_message.text = f"AI phát hiện: Bạn cắm nhầm cờ ở ({r},{c}). Nó an toàn!"
            self.ui_grid[r][c].background_color = [1, 0, 1, 1] 
            
        else:
            self.hint_message.text = "AI chưa đủ dữ kiện để đưa ra quyết định chắc chắn!"

    def handle_chord(self, r, c):
        if self.game_board.game_over:
            return
            
        self.game_board.reveal_safe_around(r, c)
        
        self.game_board.check_win() 
        self.sync_ui_with_logic()
    
    def handle_click(self, r, c):
        '''
        Hàm trung gian nhận yêu cầu click từ CellUI và ra lệnh cho Board xử lý.
        Đảm bảo rải mìn an toàn ở click đầu tiên và kích hoạt kiểm tra Thắng/Thua.
        
        Args:
            r (int): Tọa độ hàng được click.
            c (int): Tọa độ cột được click.
        '''
        if self.game_board.game_over:
            return

        if self.is_first_click:
            self.game_board.place_mines(r, c)
            self.is_first_click = False

        self.game_board.reveal(r, c)
        
        for r in range(self.game_rows):
            for c in range(self.game_cols):
                cell = self.game_board.grid[r][c]

                if cell.isRevealed and not cell.isMine and (r, c) not in self.ai.safe:
                    self.ai.add_knowledge((r, c), cell.neighbors, self.game_board)

        self.game_board.check_win() 
        
        self.sync_ui_with_logic()

    def sync_ui_with_logic(self):
        '''
        Đồng bộ toàn bộ giao diện (View) để phản ánh trạng thái mới nhất của Bộ não (Model).
        Cập nhật Label thông báo chiến thắng/thua cuộc hoặc số mạng hiện tại, 
        và làm mới màu sắc của tất cả nút bấm.
        '''
        if self.game_board.game_over:
            if self.game_board.is_win:
                self.lives_label.text = "CHIẾN THẮNG!"
                self.lives_label.color = [0, 1, 0, 1]
            else:
                self.lives_label.text = "GAME OVER!"
                self.lives_label.color = [1, 0, 0, 1]
        else:
            self.lives_label.text = f"Mạng sống: {self.game_board.lives}"

        for r in range(self.game_rows):
            for c in range(self.game_cols):
                self.ui_grid[r][c].update_display()
                

    def update_board_size(self, *args):
        '''
        Tự động tính toán lại kích thước để ép lưới (Grid) hiển thị 
        dưới dạng hình vuông hoàn hảo dựa trên sự thay đổi màn hình thiết bị.
        '''
        available_height = Window.height * 0.8 
        
        shortest_edge = min(Window.width, available_height)
        square_size = shortest_edge * 0.9
        self.board_layout.size = (square_size, square_size)

if __name__ == '__main__':
    MinesweeperApp().run()
