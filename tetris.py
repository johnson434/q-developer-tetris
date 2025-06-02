#!/usr/bin/env python3
import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_Y = (SCREEN_HEIGHT - GRID_HEIGHT * BLOCK_SIZE) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.blocks_broken = 0
        self.stage = 1
        self.stage_goal = 1  # Only need 1 block per stage
        self.fall_speed = 1.0  # seconds per grid cell (slower)
        self.last_fall_time = time.time()

    def new_piece(self):
        # Choose a random shape
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = SHAPE_COLORS[shape_idx]
        
        # Start position
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {'shape': shape, 'x': x, 'y': y, 'color': color}

    def valid_position(self, piece=None, x_offset=0, y_offset=0):
        if piece is None:
            piece = self.current_piece
            
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = piece['x'] + x + x_offset
                    pos_y = piece['y'] + y + y_offset
                    
                    # Check if out of bounds
                    if pos_x < 0 or pos_x >= GRID_WIDTH or pos_y >= GRID_HEIGHT:
                        return False
                    
                    # Check if collides with existing blocks
                    if pos_y >= 0 and self.grid[pos_y][pos_x]:
                        return False
        return True

    def merge_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = self.current_piece['x'] + x
                    pos_y = self.current_piece['y'] + y
                    
                    # Only merge if within grid
                    if 0 <= pos_y < GRID_HEIGHT and 0 <= pos_x < GRID_WIDTH:
                        self.grid[pos_y][pos_x] = self.current_piece['color']
        
        # Check for completed lines
        self.check_lines()
        
        # Create new piece
        self.current_piece = self.new_piece()
        
        # Check if game over
        if not self.valid_position():
            self.game_over = True

    def rotate_piece(self):
        # Create a rotated version of the current piece
        shape = self.current_piece['shape']
        rotated = [[shape[y][x] for y in range(len(shape)-1, -1, -1)] for x in range(len(shape[0]))]
        
        old_shape = self.current_piece['shape']
        self.current_piece['shape'] = rotated
        
        # If rotation is not valid, revert
        if not self.valid_position():
            self.current_piece['shape'] = old_shape

    def check_lines(self):
        lines_to_clear = []
        
        # Find completed lines
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # Update score and blocks broken
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            # Count just 1 block broken regardless of how many lines cleared
            self.blocks_broken = 1
            self.score += len(lines_to_clear) * 100
            
            # Remove completed lines
            for line in lines_to_clear:
                del self.grid[line]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            # Check if stage is completed
            if self.blocks_broken >= self.stage_goal:
                if self.stage < 10:
                    self.stage += 1
                    self.stage_goal = 1  # Only need 1 block per stage
                    self.blocks_broken = 0
                    self.fall_speed = 1.0  # Keep the same slow speed

    def draw_grid(self):
        # Draw background
        self.screen.fill(BLACK)
        
        # Draw grid border
        pygame.draw.rect(self.screen, WHITE, 
                         (GRID_X - 2, GRID_Y - 2, 
                          GRID_WIDTH * BLOCK_SIZE + 4, 
                          GRID_HEIGHT * BLOCK_SIZE + 4), 2)
        
        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_x = GRID_X + x * BLOCK_SIZE
                cell_y = GRID_Y + y * BLOCK_SIZE
                
                # Draw cell
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], 
                                    (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, WHITE, 
                                    (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)
                else:
                    pygame.draw.rect(self.screen, DARK_GRAY, 
                                    (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw current piece
        if not self.game_over and not self.paused:
            for y, row in enumerate(self.current_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        cell_x = GRID_X + (self.current_piece['x'] + x) * BLOCK_SIZE
                        cell_y = GRID_Y + (self.current_piece['y'] + y) * BLOCK_SIZE
                        
                        pygame.draw.rect(self.screen, self.current_piece['color'], 
                                        (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, WHITE, 
                                        (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw score and level info
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (20, 50))
        
        stage_text = self.font.render(f"Stage: {self.stage}/10", True, WHITE)
        self.screen.blit(stage_text, (20, 80))
        
        progress_text = self.font.render(f"Blocks: {self.blocks_broken}/{self.stage_goal}", True, WHITE)
        self.screen.blit(progress_text, (20, 110))
        
        # Draw game over or paused message
        if self.game_over:
            if self.stage == 10 and self.blocks_broken >= self.stage_goal:
                # Congratulations message
                congrats_text = self.big_font.render("CONGRATULATIONS!", True, YELLOW)
                win_text = self.font.render("You completed all 10 stages!", True, WHITE)
                restart_text = self.font.render("Press R to play again", True, WHITE)
                
                self.screen.blit(congrats_text, 
                                (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 - 60))
                self.screen.blit(win_text, 
                                (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2))
                self.screen.blit(restart_text, 
                                (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 + 40))
            else:
                # Game over message
                game_over_text = self.big_font.render("GAME OVER", True, RED)
                restart_text = self.font.render("Press R to restart", True, WHITE)
                
                self.screen.blit(game_over_text, 
                                (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 - 30))
                self.screen.blit(restart_text, 
                                (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 + 30))
        elif self.paused:
            paused_text = self.big_font.render("PAUSED", True, YELLOW)
            self.screen.blit(paused_text, 
                            (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 15))

    def run(self):
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
                        self.reset_game()
                    
                    if self.game_over:
                        continue
                    
                    if event.key == pygame.K_p:
                        # Pause/unpause game
                        self.paused = not self.paused
                    
                    if self.paused:
                        continue
                    
                    if event.key == pygame.K_LEFT:
                        # Move left
                        if self.valid_position(x_offset=-1):
                            self.current_piece['x'] -= 1
                    
                    elif event.key == pygame.K_RIGHT:
                        # Move right
                        if self.valid_position(x_offset=1):
                            self.current_piece['x'] += 1
                    
                    elif event.key == pygame.K_DOWN:
                        # Move down
                        if self.valid_position(y_offset=1):
                            self.current_piece['y'] += 1
                        else:
                            self.merge_piece()
                    
                    elif event.key == pygame.K_UP:
                        # Rotate piece
                        self.rotate_piece()
                    
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while self.valid_position(y_offset=1):
                            self.current_piece['y'] += 1
                        self.merge_piece()
            
            # Game logic
            if not self.game_over and not self.paused:
                # Auto-fall
                current_time = time.time()
                if current_time - self.last_fall_time > self.fall_speed:
                    if self.valid_position(y_offset=1):
                        self.current_piece['y'] += 1
                    else:
                        self.merge_piece()
                    self.last_fall_time = current_time
                
                # Check if stage completed
                if self.blocks_broken >= self.stage_goal:
                    if self.stage == 10:
                        self.game_over = True
                    else:
                        self.stage += 1
                        self.stage_goal = 1  # Only need 1 block per stage
                        self.blocks_broken = 0
                        self.fall_speed = 1.0  # Keep the same slow speed
            
            # Draw everything
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Tetris()
    game.run()
