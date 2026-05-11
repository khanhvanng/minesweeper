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
from kivy.clock import Clock
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.image import Image 
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

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
                
                if (nr, nc) in self.mines or (neighbor.isMine and neighbor.isRevealed):
                    remaining_mines -= 1
                    
                elif not neighbor.isRevealed:
                    unknown.add((nr, nc))
        
        if len(unknown) > 0:
            new_constraint = Constraint(unknown, remaining_mines)

            if new_constraint not in self.knowledge:
                self.knowledge.append(new_constraint)
    
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
        
        if self.brute_force():
            self.infer() 
            return self.get_hint(board)
        
        return ("none", None)

    def brute_force(self):
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
                       
                        if len(comp_cells.union(other_c.cells)) <= 15:
                            comp_cells.update(other_c.cells)
                            comp_constraints.append(other_c)
                            unassigned.remove(other_c)
                            added = True
                            
            components.append((list(comp_cells), comp_constraints))
            
        for comp_cells, comp_constraints in components:
            valid_assignments = []
            
            cell_to_constraints = {i: [] for i in range(len(comp_cells))}
            for const in comp_constraints:
                for i, cell in enumerate(comp_cells):
                    if cell in const.cells:
                        cell_to_constraints[i].append(const)
            
            const_unassigned_count = {const: sum(1 for cell in comp_cells if cell in const.cells) for const in comp_constraints}
            const_mine_counts = {const: 0 for const in comp_constraints}

            def backtrack(index, current_assignment):
                if index == len(comp_cells):
                    valid_assignments.append(current_assignment.copy())
                    return
                
                can_be_safe = True
                for const in cell_to_constraints[index]:
                    if const_mine_counts[const] + (const_unassigned_count[const] - 1) < const.mines:
                        can_be_safe = False
                        break
                
                if can_be_safe:
                    for const in cell_to_constraints[index]:
                        const_unassigned_count[const] -= 1
                    
                    current_assignment[index] = False
                    backtrack(index + 1, current_assignment)
                    
                    for const in cell_to_constraints[index]:
                        const_unassigned_count[const] += 1
                
                can_be_mine = True
                for const in cell_to_constraints[index]:
                    if const_mine_counts[const] + 1 > const.mines:
                        can_be_mine = False
                        break
                
                if can_be_mine:
                    for const in cell_to_constraints[index]:
                        const_unassigned_count[const] -= 1
                        const_mine_counts[const] += 1
                        
                    current_assignment[index] = True
                    backtrack(index + 1, current_assignment)
                    
                    for const in cell_to_constraints[index]:
                        const_unassigned_count[const] += 1
                        const_mine_counts[const] -= 1
            
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
        self.font_name = 'font/Board.ttf'

        self.background_color = [0, 0, 0, 0]
        self.background_normal = '' 
        self.background_down = ''

        with self.canvas.before:
            self.bg_color = Color(get_color_from_hex("#FFB64A"))
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])

        with self.canvas.after:
            self.icon_color = Color(1, 1, 1, 0)
            self.icon_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        padding = min(self.width, self.height) * 0.15
        self.icon_rect.pos = (self.x + padding, self.y + padding)
        self.icon_rect.size = (self.width - 2*padding, self.height - 2*padding)

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
        self.text = ""
        self.icon_color.rgba = [1, 1, 1, 0] 
        
        if self.logic_cell.isRevealed:
            if self.logic_cell.isMine:
                self.bg_color.rgba = [1, 0.4, 0.4, 1]  

                self.icon_color.rgba = [1, 1, 1, 1] 
                self.icon_rect.source = 'image/bone.png' 
            else:
                self.bg_color.rgba = [1, 1, 1, 0.8] 
                self.text = str(self.logic_cell.neighbors) if self.logic_cell.neighbors > 0 else ""
                self.color = [0.2, 0.2, 0.2, 1] 
        else:
            if self.logic_cell.isFlagged:
                self.bg_color.rgba = [1, 0.8, 0.4, 1]
    
                self.icon_color.rgba = [1, 1, 1, 1] 
                self.icon_rect.source = 'image/fish.png'  
            else:
                self.bg_color.rgba = get_color_from_hex('#FFB64A') 
                self.text = ""

class RoundedSpinnerOption(SpinnerOption):
    '''
    Lớp này dùng để bo góc cho các lựa chọn NẰM BÊN TRONG danh sách xổ xuống.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.background_color = [0, 0, 0, 0]
        self.background_normal = ''
        self.background_down = ''
        
        self.font_name = 'font/hint.ttf' 
        self.color = [1, 1, 1, 1] 
        
        with self.canvas.before:
            self.bg_color = Color(*get_color_from_hex("#DDB476"),) 
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10]) 
            
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = (self.x + 2, self.y + 2)
        self.bg_rect.size = (self.width - 4, self.height - 4)

class RoundedSpinner(Spinner):
    '''
    Lớp này dùng để bo góc cho CÁI NÚT SPINNER CHÍNH hiển thị trên màn hình.
    '''
    def __init__(self, **kwargs):
        self.custom_color = kwargs.pop('custom_color', get_color_from_hex("#C9903BFF"))
        super().__init__(**kwargs)
        
        self.background_color = [0, 0, 0, 0]
        self.background_normal = ''
        self.background_down = ''
        
        self.option_cls = RoundedSpinnerOption 
        
        with self.canvas.before:
            self.bg_color = Color(*self.custom_color)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class RoundedButton(Button):
    '''
    Lớp nút bấm tùy chỉnh để có viền bo góc.
    Hỗ trợ truyền màu sắc tùy ý qua tham số `custom_color`.
    '''
    def __init__(self, **kwargs):
        self.custom_color = kwargs.pop('custom_color', [1, 0.6, 0.8, 1])
        super().__init__(**kwargs)
        
        self.background_color = [0, 0, 0, 0] 
        self.background_normal = ''
        self.background_down = ''
        
        with self.canvas.before:
            self.bg_color = Color(*self.custom_color)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

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
        self.sm = ScreenManager()
        
        self.start_screen = Screen(name='start')
        start_layout = FloatLayout()
        
        bg_start = Image(source='image/background.jpg', fit_mode='cover')
        start_layout.add_widget(bg_start)
        
        title = Label(
            text="Meowsweeper", 
            font_size=100, bold=True, 
            color=get_color_from_hex("#C9903B"),
            font_name='font/head.ttf',
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )
        start_layout.add_widget(title)
        
        start_btn = RoundedButton(
            text="Bắt đầu", 
            font_size=30, bold=True, 
            font_name='font/hint.ttf',
            size_hint=(0.4, 0.15), 
            pos_hint={'center_x': 0.5, 'center_y': 0.4}, 
            custom_color=get_color_from_hex("#C9903B"),
            color=[1, 1, 1, 1]
        )
        start_btn.bind(on_release=self.go_to_game)
        start_layout.add_widget(start_btn)
        
        self.start_screen.add_widget(start_layout)
        self.sm.add_widget(self.start_screen)

        self.game_screen = Screen(name='game')
        
        self.game_rows = 6
        self.game_cols = 12
        self.num_mines = 10
        self.time_elapsed = 0
        self.timer_event = None
        self.is_popup_open = False 

        self.game_board = Board(self.game_rows, self.game_cols, self.num_mines, lives=3)
        self.is_first_click = True
        self.ui_grid = []
        self.ai = MinesweeperAI(self.game_rows, self.game_cols)

        
        root_layer = FloatLayout()
        bg_game = Image(source='image/background.jpg', fit_mode='cover')
        root_layer.add_widget(bg_game)

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        self.menu_spinner = RoundedSpinner(
            text='Cài đặt',
            font_size=25,
            font_name="font/Hint.ttf",
            values=('Dễ', 'Vừa', 'Khó', 'Chơi lại'),
            size_hint=(0.25, 1), 
            background_color=get_color_from_hex("#E0B067FF"),
            bold=True, 
            background_normal=''
        )
        self.menu_spinner.bind(text=self.on_menu_select)
        top_bar.add_widget(self.menu_spinner)

        self.hints_left = 3

        self.hint_btn = RoundedButton(
            font_size=25,
            text=f"Gợi ý ({self.hints_left})", 
            size_hint=(0.2, 1), 
            custom_color=get_color_from_hex("#C9903B"),
            bold=True, 
            font_name='font/hint.ttf'
        )
        self.hint_btn.bind(on_release=self.give_hint)
        top_bar.add_widget(self.hint_btn)

        self.timer_label = Label(text="000", size_hint=(0.2, 1), font_size=30, bold=True, color=[0,0,0,1])
        top_bar.add_widget(self.timer_label)

        self.lives_layout = BoxLayout(orientation='horizontal', size_hint=(0.35, 1))
        self.update_lives_ui()
        top_bar.add_widget(self.lives_layout)

        main_layout.add_widget(top_bar)

        self.hint_message = Label(text="Sẵn sàng! Chúc bạn may mắn", font_size=18, color=[0, 0, 0, 1], size_hint=(1, 0.05), bold=True)
        main_layout.add_widget(self.hint_message)

        board_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.85))
        self.board_layout = GridLayout(cols=self.game_cols, rows=self.game_rows, size_hint=(None, None), spacing=2)
        
        self.create_grid_ui() 
        board_anchor.add_widget(self.board_layout)
        main_layout.add_widget(board_anchor)
        
        root_layer.add_widget(main_layout)
        self.game_screen.add_widget(root_layer)
        self.sm.add_widget(self.game_screen)
        
        Window.bind(on_resize=self.update_board_size)
        
        self.sync_ui_with_logic()

        return self.sm

    def go_to_game(self, instance):
        '''Hàm để chuyển từ màn hình Start sang màn hình Game'''
        self.sm.current = 'game'

    def create_grid_ui(self):
        self.board_layout.clear_widgets()
        self.ui_grid = []
        
        self.board_layout.rows = self.game_rows
        self.board_layout.cols = self.game_cols

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

    def update_lives_ui(self):
        self.lives_layout.clear_widgets()
        for _ in range(self.game_board.lives):
            heart = Image(source='image/heart.png', allow_stretch=True) 
            self.lives_layout.add_widget(heart)

    def on_menu_select(self, spinner, text):
        if text == 'Dễ':
            self.reset_game(6, 12, 10)
        elif text == 'Vừa':
            self.reset_game(10, 21, 35)
        elif text == 'Khó':
            self.reset_game(13, 28, 75)
        elif text == 'Chơi lại':
            self.reset_game(self.game_rows, self.game_cols, self.num_mines)
        
        spinner.text = 'Cài đặt'

    def reset_game(self, rows, cols, mines):
        self.game_rows = rows
        self.game_cols = cols
        self.num_mines = mines
        
        self.game_board = Board(self.game_rows, self.game_cols, self.num_mines, lives=3)
        self.ai = MinesweeperAI(self.game_rows, self.game_cols)
        self.is_first_click = True

        self.hints_left = 3
        self.hint_btn.text = f"Gợi ý ({self.hints_left})"
        
        self.create_grid_ui()

        self.update_lives_ui()
        self.hint_message.text = "Game mới đã sẵn sàng!"
        self.hint_message.color = [0, 0, 0, 1]
        
        self.time_elapsed = 0
        self.timer_label.text = "000"
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        self.is_popup_open = False

        self.sync_ui_with_logic()

    def give_hint(self, instance):
        if self.game_board.game_over:
            return

        if self.hints_left <= 0:
            self.hint_message.text = "Hết lượt gợi ý rồi! Tự lực cánh sinh đi nha!"
            self.hint_message.color = [1, 0, 0, 1]
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
        
        if action == "none":
            self.hint_message.text = "AI bó tay! Vẫn giữ nguyên lượt gợi ý cho bạn."
            self.hint_message.font_name = "font/body.ttf"
            self.hint_message.color = [0, 0, 0, 1]
            return 

        self.hints_left -= 1
        self.hint_btn.text = f"Gợi ý ({self.hints_left})"
        
        if action == "safe":
            r, c = coords
            self.hint_message.text = f"Ô ({r},{c}) không có cá. Bạn có thể mở ô."
            self.ui_grid[r][c].bg_color.rgba = get_color_from_hex("#77DD77")
            self.hint_message.font_name = "font/body.ttf"
            self.ui_grid[r][c].color = [0, 0, 0, 1]
            
        elif action == "mine":
            r, c = coords
            self.hint_message.text = f"Ô ({r},{c}) là cá. Hãy đánh dấu vị trí."
            self.ui_grid[r][c].bg_color.rgba = [1, 0.6, 0.2, 1]
            self.ui_grid[r][c].text = "!"
            self.hint_message.font_name = "font/body.ttf"
            self.ui_grid[r][c].color = [0, 0, 0, 1]
            
        elif action == "wrong_flag":
            r, c = coords
            self.hint_message.text = f"Ô ({r},{c}) không có cá. Bạn đánh dấu nhầm rồi."
            self.ui_grid[r][c].bg_color.rgba = get_color_from_hex("#94FBFF")
            self.hint_message.font_name = "font/body.ttf"

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
            if not self.timer_event:
                self.timer_event = Clock.schedule_interval(self.update_timer, 1)

        self.game_board.reveal(r, c)

        self.game_board.check_win() 
        
        self.sync_ui_with_logic()

    def update_timer(self, dt):
        if self.game_board.game_over:
            self.timer_event.cancel()
            return
            
        self.time_elapsed += 1
        self.timer_label.text = f"{self.time_elapsed:03d}"

    def sync_ui_with_logic(self):
        '''
        Đồng bộ toàn bộ giao diện (View) để phản ánh trạng thái mới nhất của Bộ não (Model).
        Cập nhật Label thông báo chiến thắng/thua cuộc hoặc số mạng hiện tại, 
        và làm mới màu sắc của tất cả nút bấm.
        '''
        self.update_lives_ui()

        for r in range(self.game_rows):
            for c in range(self.game_cols):
                self.ui_grid[r][c].update_display()
                
        if self.game_board.game_over:
            self.show_endgame_popup(self.game_board.is_win)  

    def update_board_size(self, *args):
        '''
        Tự động tính toán lại kích thước để ép lưới (Grid) hiển thị 
        dưới dạng hình vuông hoàn hảo dựa trên sự thay đổi màn hình thiết bị.
        '''
        available_width = Window.width * 0.95
        available_height = Window.height * 0.75 
        
        spacing_size = 2 
        total_spacing_x = spacing_size * (self.game_cols - 1)
        total_spacing_y = spacing_size * (self.game_rows - 1)
        
        max_cell_width = (available_width - total_spacing_x) / self.game_cols
        max_cell_height = (available_height - total_spacing_y) / self.game_rows
        
        perfect_cell_size = min(max_cell_width, max_cell_height)
        
        board_width = (perfect_cell_size * self.game_cols) + total_spacing_x
        board_height = (perfect_cell_size * self.game_rows) + total_spacing_y
        
        self.board_layout.size = (board_width, board_height)

    def show_endgame_popup(self, is_win):
        '''Tạo và hiển thị cửa sổ nổi kết thúc game: Nền trắng trong suốt, giới hạn kích thước'''
        if self.is_popup_open:
            return
        self.is_popup_open = True
        
        p_width = min(Window.width * 0.7, 500)
        p_height = min(Window.height * 0.45, 400)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        msg = "Bạn đã bảo vệ được số cá!" if is_win else f"   Cá của bạn đã bị\nchú mèo khác ăn hết..."
        color = [0.2, 0.7, 0.2, 1] if is_win else [0.9, 0.2, 0.2, 1]
        
        lbl = Label(
            text=msg, 
            font_size=30, bold=True, color=color,
            font_name='font/hint.ttf' 
        )
        content.add_widget(lbl)
        
        if is_win:
            finish_time = f"Thời gian: {self.time_elapsed} giây"
            lbl_time = Label(
                text=finish_time, 
                font_size=22, 
                color=[0.4, 0.4, 0.4, 1], 
                font_name='font/hint.ttf'
            )
            content.add_widget(lbl_time)

        btn = RoundedButton(
            text="Chơi lại", 
            font_size=24, bold=True, 
            font_name='font/hint.ttf',
            size_hint=(1, 0.6), 
            custom_color=get_color_from_hex("#C9903B")
        )
        btn.bind(on_release=self.restart_from_popup)
        content.add_widget(btn)
        
        self.endgame_popup = Popup(
            title="Thông báo",
            title_color=[0, 0, 0, 1], 
            title_font='font/hint.ttf',
            title_size='18sp',
            title_align='center',
            separator_color=get_color_from_hex("#C9903B"), 
            
            background='', 
            background_color=[1, 1, 1, 0.85], 
            
            content=content,
            size_hint=(None, None), 
            size=(p_width, p_height), 
            auto_dismiss=False
        ) 
        
        self.endgame_popup.open()

    def restart_from_popup(self, instance):
        '''Xử lý khi người chơi bấm nút Chơi lại trên Popup'''
        self.endgame_popup.dismiss() 
        self.reset_game(self.game_rows, self.game_cols, self.num_mines) 

if __name__ == '__main__':
    MinesweeperApp().run()
