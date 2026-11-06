import pygame
import sys

pygame.init()
pygame.font.init()

# Janela e Grade
CELL_SIZE = 60
GRID_SIZE = 5
MARGIN_LEFT = 180
MARGIN_TOP = 140

WIDTH = MARGIN_LEFT + GRID_SIZE * CELL_SIZE + 40
HEIGHT = MARGIN_TOP + GRID_SIZE * CELL_SIZE + 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trab2 - Nonogram (Picross)")

COLOR_BG = (245, 247, 250)
COLOR_GRID_BG = (255, 255, 255)
COLOR_GRID_LINE = (200, 205, 215)
COLOR_FILLED = (44, 62, 80)
COLOR_CROSS = (231, 76, 60)
COLOR_TEXT = (50, 50, 50)
COLOR_HINT = (100, 110, 120)
COLOR_CURSOR = (52, 152, 219)
COLOR_WIN = (46, 204, 113)
COLOR_LOSE = (231, 76, 60)

font_title = pygame.font.SysFont("Arial", 24, bold=True)
font_sub = pygame.font.SysFont("Arial", 16)
font_hints = pygame.font.SysFont("Arial", 20, bold=True)
font_status = pygame.font.SysFont("Arial", 28, bold=True)

# matriz das Fases 
# 1: Preenchido, 0: Vazio
LEVELS = [
    {
        "name": "Fase 1: Coração",
        "solution": [
            [0, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0]
        ]
    },
    {
        "name": "Fase 2: Estrela",
        "solution": [
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1]
        ]
    }
]

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = 0  # 0: Vazio, 1: Preenchido, 2: Marcado com X

    def draw(self, surface, x, y, is_selected):
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, COLOR_GRID_BG, rect)
        
        if self.state == 1:
            pygame.draw.rect(surface, COLOR_FILLED, rect.inflate(-6, -6), border_radius=4)
        elif self.state == 2:
            pygame.draw.line(surface, COLOR_CROSS, (x + 12, y + 12), (x + CELL_SIZE - 12, y + CELL_SIZE - 12), 3)
            pygame.draw.line(surface, COLOR_CROSS, (x + CELL_SIZE - 12, y + 12), (x + 12, y + CELL_SIZE - 12), 3)

        pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)

        if is_selected:
            pygame.draw.rect(surface, COLOR_CURSOR, rect, 3)

#celulas e grades são classes
class Grid:
    def __init__(self, solution):
        self.solution = solution
        self.rows = len(solution)
        self.cols = len(solution[0])
        self.cells = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.row_hints = self._calc_row_hints()
        self.col_hints = self._calc_col_hints()

    def _calc_row_hints(self):
        hints = []
        for row in self.solution:
            h, count = [], 0
            for cell in row:
                if cell == 1:
                    count += 1
                elif count > 0:
                    h.append(count)
                    count = 0
            if count > 0:
                h.append(count)
            hints.append(h if h else [0])
        return hints

    def _calc_col_hints(self):
        hints = []
        for c in range(self.cols):
            h, count = [], 0
            for r in range(self.rows):
                if self.solution[r][c] == 1:
                    count += 1
                elif count > 0:
                    h.append(count)
                    count = 0
            if count > 0:
                h.append(count)
            hints.append(h if h else [0])
        return hints

    def check_victory(self):
        for r in range(self.rows):
            for c in range(self.cols):
                is_target = (self.solution[r][c] == 1)
                is_filled = (self.cells[r][c].state == 1)
                if is_target != is_filled:
                    return False
        return True

# Principal
class NonogramGame:
    def __init__(self):
        self.current_level = 0
        self.load_level(self.current_level)
        self.cursor_r = 0
        self.cursor_c = 0

    def load_level(self, idx):
        self.level_data = LEVELS[idx]
        self.grid = Grid(self.level_data["solution"])
        self.game_state = "PLAYING" 

    def reset_level(self):
        self.load_level(self.current_level)

    def next_level(self):
        self.current_level += 1
        if self.current_level < len(LEVELS):
            self.load_level(self.current_level)
        else:
            self.game_state = "GAME_FINISHED"

    def handle_click(self, r, c, button):
        if self.game_state != "PLAYING":
            return

        cell = self.grid.cells[r][c]
        target = self.grid.solution[r][c]

        if button == 1:  
            if cell.state == 1:
                return
            if target == 1:
                cell.state = 1
                if self.grid.check_victory():
                    self.game_state = "WIN"
            else:
                self.game_state = "GAMEOVER"

        elif button == 3:  
            if cell.state == 0:
                cell.state = 2
            elif cell.state == 2:
                cell.state = 0

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if MARGIN_LEFT <= mx < MARGIN_LEFT + GRID_SIZE * CELL_SIZE and                        MARGIN_TOP <= my < MARGIN_TOP + GRID_SIZE * CELL_SIZE:
                        c = (mx - MARGIN_LEFT) // CELL_SIZE
                        r = (my - MARGIN_TOP) // CELL_SIZE
                        self.handle_click(r, c, event.button)

                if event.type == pygame.KEYDOWN:
                    if self.game_state == "PLAYING":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.cursor_r = max(0, self.cursor_r - 1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.cursor_r = min(GRID_SIZE - 1, self.cursor_r + 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self.cursor_c = max(0, self.cursor_c - 1)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.cursor_c = min(GRID_SIZE - 1, self.cursor_c + 1)
                        elif event.key == pygame.K_SPACE:
                            self.handle_click(self.cursor_r, self.cursor_c, 1)
                        elif event.key == pygame.K_x:
                            self.handle_click(self.cursor_r, self.cursor_c, 3)

                    elif event.key == pygame.K_r:
                        if self.game_state in ("GAMEOVER", "GAME_FINISHED"):
                            self.current_level = 0
                            self.load_level(0)
                        elif self.game_state == "WIN":
                            self.next_level()

            screen.fill(COLOR_BG)

            txt_title = font_title.render(self.level_data["name"] if self.game_state != "GAME_FINISHED" else "Fim de Jogo", True, COLOR_TEXT)
            screen.blit(txt_title, (MARGIN_LEFT, 20))

            txt_instr = font_sub.render("Mouse: Esq = Pintar | Dir = Marcar X  |  Teclado: Setas + Espaço / X", True, COLOR_HINT)
            screen.blit(txt_instr, (30, 60))

            if self.game_state != "GAME_FINISHED":

                for r, hints in enumerate(self.grid.row_hints):
                    hint_str = " ".join(map(str, hints))
                    txt = font_hints.render(hint_str, True, COLOR_TEXT)
                    screen.blit(txt, (MARGIN_LEFT - txt.get_width() - 15, MARGIN_TOP + r * CELL_SIZE + (CELL_SIZE - txt.get_height()) // 2))

                for c, hints in enumerate(self.grid.col_hints):
                    for idx, val in enumerate(reversed(hints)):
                        txt = font_hints.render(str(val), True, COLOR_TEXT)
                        screen.blit(txt, (MARGIN_LEFT + c * CELL_SIZE + (CELL_SIZE - txt.get_width()) // 2, MARGIN_TOP - (idx + 1) * 25 - 5))

                # Desenhar Células da Grade
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        x = MARGIN_LEFT + c * CELL_SIZE
                        y = MARGIN_TOP + r * CELL_SIZE
                        is_sel = (r == self.cursor_r and c == self.cursor_c and self.game_state == "PLAYING")
                        self.grid.cells[r][c].draw(screen, x, y, is_sel)

            if self.game_state == "GAMEOVER":
                txt = font_status.render("VOCÊ ERROU! (Pressione R para Reiniciar)", True, COLOR_LOSE)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT - 50))

            elif self.game_state == "WIN":
                txt = font_status.render("ACERTOU! (Pressione R para Avançar)", True, COLOR_WIN)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT - 50))

            elif self.game_state == "JOGO FINALIZADO":
                txt = font_status.render("PARABÉNS! VOCÊ COMPLETOU O JOGO!", True, COLOR_WIN)
                txt_restart = font_sub.render("Pressione R para jogar novamente", True, COLOR_TEXT)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 20))
                screen.blit(txt_restart, (WIDTH // 2 - txt_restart.get_width() // 2, HEIGHT // 2 + 20))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = NonogramGame()
    game.run()
