import tkinter as tk
import random
import pygame

# === Pause/Unpause ===
is_paused = False
pause_menu = None

# === CONFIGURATION ===
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_WIDTH = COLUMNS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
DELAY = 500

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

COLORS = {
    'I': 'cyan', 'J': 'blue', 'L': 'orange', 'O': 'yellow',
    'S': 'green', 'T': 'purple', 'Z': 'red'
}

# === TKINTER ROOT SETUP ===
root = tk.Tk()
root.title("Tetris 2P")
root.attributes("-fullscreen", True)
root.bind("<F11>", lambda e: root.attributes("-fullscreen", False))

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# === UI LAYOUT ===
grid_y = 230
label_y = grid_y - 30
p1_grid_x = 780
p1_right_sidebar_x = p1_grid_x - 150
p1_left_sidebar_x = p1_grid_x + GRID_WIDTH + 50

main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

# --- PLAYER 1 ---
tk.Label(main_frame, text="Player 1:", fg="white", bg="black", font=("Arial", 14)).place(x=p1_grid_x, y=label_y)

p1_canvas = tk.Canvas(main_frame, width=GRID_WIDTH, height=GRID_HEIGHT, bg="black")
p1_canvas.place(x=p1_grid_x, y=grid_y)

p1_left_canvas = tk.Canvas(main_frame, width=100, height=500, bg="black")
p1_left_canvas.place(x=p1_left_sidebar_x, y=grid_y + 30)
tk.Label(main_frame, text="Next Block", fg="white", bg="black", font=("Arial", 14)).place(x=p1_left_sidebar_x, y=grid_y)

# Right Sidebar Elements
p1_right_sidebar_x = p1_grid_x - 150

# Hold
tk.Label(main_frame, text="Hold", fg="white", bg="black", font=("Arial", 14)).place(x=p1_right_sidebar_x, y=grid_y)
p1_right_canvas = tk.Canvas(main_frame, width=100, height=100, bg="black")
p1_right_canvas.place(x=p1_right_sidebar_x, y=grid_y + 30)

# Score
tk.Label(main_frame, text="Score", fg="white", bg="black", font=("Arial", 14)).place(x=p1_right_sidebar_x, y=grid_y + 140)
p1_score_canvas = tk.Canvas(main_frame, width=100, height=50, bg="black")
p1_score_canvas.place(x=p1_right_sidebar_x, y=grid_y + 170)

# Cleared Lines
tk.Label(main_frame, text="Cleared Lines", fg="white", bg="black", font=("Arial", 14)).place(x=p1_right_sidebar_x, y=grid_y + 230)
p1_lines_canvas = tk.Canvas(main_frame, width=100, height=50, bg="black")
p1_lines_canvas.place(x=p1_right_sidebar_x, y=grid_y + 260)

game_over_label = tk.Label(main_frame, text="Game Over", fg="white", bg="black", font=("Arial", 24))
game_over_label.place(x=p1_grid_x + GRID_WIDTH // 2, y=grid_y + GRID_HEIGHT // 2)
game_over_label.place_forget()  # Hide it initially

# === TETRIS LOGIC FOR PLAYER 1 ===
class TetrisGame:
    def __init__(self):
        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.queue = [self.random_piece() for _ in range(5)]
        self.hold_piece_data = None
        self.can_hold = True
        self.score = 0
        self.cleared_lines = 0
        self.is_game_over = False
        self.new_piece()
        self.draw()
        root.bind("<Key>", self.key_press)
        root.after(DELAY, self.update)
        root.bind("<Escape>", lambda e: self.toggle_pause())

    def random_piece(self):
        shape = random.choice(list(SHAPES))
        return {'shape': shape, 'matrix': SHAPES[shape], 'color': COLORS[shape]}

    def new_piece(self):
        current = self.queue.pop(0)
        self.piece = current['matrix']
        self.shape = current['shape']
        self.color = current['color']
        self.queue.append(self.random_piece())
        self.x = COLUMNS // 2 - len(self.piece[0]) // 2
        self.y = 0
        self.can_hold = True
        if self.collision(self.x, self.y, self.piece):
            self.game_over()

    def draw_cell(self, canvas, x, y, color, outline="gray"):
        x0, y0 = x * CELL_SIZE, y * CELL_SIZE
        x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=outline)

    def draw_preview_cell(self, canvas, x, y, size, color):
        x0, y0 = x * size, y * size
        x1, y1 = x0 + size, y0 + size
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='gray')

    def draw(self):
        p1_canvas.delete("all")
        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.board[y][x]:
                    self.draw_cell(p1_canvas, x, y, self.board[y][x])
        if not self.is_game_over:
            gx, gy = self.get_ghost_position()
            for i, row in enumerate(self.piece):
                for j, val in enumerate(row):
                    if val:
                        self.draw_cell(p1_canvas, gx + j, gy + i, "", outline='white')
            for i, row in enumerate(self.piece):
                for j, val in enumerate(row):
                    if val:
                        self.draw_cell(p1_canvas, self.x + j, self.y + i, self.color)
        self.draw_preview()
        self.draw_hold()
        self.draw_score()
        self.draw_cleared_lines()

    def draw_score(self):
        p1_score_canvas.delete("all")
        p1_score_canvas.create_text(50, 25, text=str(self.score), 
                                  fill="white", font=("Arial", 24))

    def draw_cleared_lines(self):
        p1_lines_canvas.delete("all")
        p1_lines_canvas.create_text(50, 25, text=str(self.cleared_lines), 
                                   fill="white", font=("Arial", 24))

    def draw_preview(self):
        p1_left_canvas.delete("all")
        size = 20
        for idx, piece in enumerate(self.queue):
            matrix, color = piece['matrix'], piece['color']
            for i, row in enumerate(matrix):
                for j, val in enumerate(row):
                    if val:
                        self.draw_preview_cell(p1_left_canvas, j + 1, i + idx * 5 + 1, size, color)

    def draw_hold(self):
        p1_right_canvas.delete("all")
        if not self.hold_piece_data:
            return
        matrix = self.hold_piece_data['matrix']
        color = self.hold_piece_data['color']
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                if val:
                    self.draw_preview_cell(p1_right_canvas, j + 1, i + 1, 20, color)

    def collision(self, x, y, piece):
        for i, row in enumerate(piece):
            for j, val in enumerate(row):
                if val:
                    px, py = x + j, y + i
                    if px < 0 or px >= COLUMNS or py >= ROWS:
                        return True
                    if py >= 0 and self.board[py][px]:
                        return True
        return False

    def get_ghost_position(self):
        gy = self.y
        while not self.collision(self.x, gy + 1, self.piece):
            gy += 1
        return self.x, gy

    def move(self, dx, dy):
        if not self.collision(self.x + dx, self.y + dy, self.piece):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self):
        rotated = list(zip(*self.piece[::-1]))
        if not self.collision(self.x, self.y, rotated):
            self.piece = rotated

    def lock_piece(self):
        for i, row in enumerate(self.piece):
            for j, val in enumerate(row):
                if val:
                    px, py = self.x + j, self.y + i
                    if py >= 0:
                        self.board[py][px] = self.color

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(new_board)
        self.cleared_lines += cleared
        self.score += cleared * 100
        for _ in range(cleared):
            new_board.insert(0, [None for _ in range(COLUMNS)])
        self.board = new_board

    def update(self):
        if self.is_game_over or is_paused:
            return
        if not self.move(0, 1):
            self.lock_piece()
            self.clear_lines()
            self.new_piece()
        self.draw()
        root.after(DELAY, self.update)

    def hold(self):
        if not self.can_hold:
            return
        self.can_hold = False
        current = {'shape': self.shape, 'matrix': self.piece, 'color': self.color}
        if not self.hold_piece_data:
            self.hold_piece_data = current
            self.new_piece()
        else:
            temp = self.hold_piece_data
            self.hold_piece_data = current
            self.piece = temp['matrix']
            self.shape = temp['shape']
            self.color = temp['color']
            self.x = COLUMNS // 2 - len(self.piece[0]) // 2
            self.y = 0

    def game_over(self):
        self.is_game_over = True
        p1_canvas.create_text(GRID_WIDTH // 2, GRID_HEIGHT // 2, text="GAME OVER", fill="white", font=("Arial", 24))
        game_over_label.update_idletasks()
        center_x = p1_grid_x + GRID_WIDTH // 2 - game_over_label.winfo_reqwidth() // 2
        center_y = grid_y + GRID_HEIGHT // 2 - game_over_label.winfo_reqheight() // 2
        game_over_label.place(x=center_x, y=center_y)
        root.unbind("<Key>")

    def key_press(self, e):
        if self.is_game_over:
            return
        if e.keysym == 'Left': self.move(-1, 0)
        elif e.keysym == 'Right': self.move(1, 0)
        elif e.keysym == 'Down': self.move(0, 1)
        elif e.keysym == 'Up': self.rotate()
        elif e.keysym == 'space':
            self.x, self.y = self.get_ghost_position()
            self.lock_piece()
            self.clear_lines()
            self.new_piece()
        elif e.keysym.lower() == 'c': self.hold()
        self.draw()

    def toggle_pause(self):
        global is_paused, pause_menu
        is_paused = not is_paused
        if is_paused:
            pause_menu = tk.Frame(main_frame, bg='gray20', width=400, height=300)
            pause_menu.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(pause_menu, text="Paused", font=("Arial", 24), fg="white", bg="gray20").pack(pady=20)
            tk.Button(pause_menu, text="Resume", font=("Arial", 16), command=self.toggle_pause).pack(pady=10)
            tk.Button(pause_menu, text="Help", font=("Arial", 16), command=self.show_help).pack(pady=10)
            tk.Button(pause_menu, text="Quit", font=("Arial", 16), command=root.destroy).pack(pady=10)
        else:
            if pause_menu:
                pause_menu.destroy()
            self.update()

    def show_help(self):
        help_win = tk.Toplevel(root)
        help_win.title("Help")
        help_win.geometry("400x300")
        tk.Label(help_win, text="Controls:\n← → ↓: Move\n↑: Rotate\nSpace: Hard Drop\nC: Hold\nEsc: Pause", justify="left").pack(padx=20, pady=20)

TetrisGame()
root.mainloop()
