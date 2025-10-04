import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 60)
        self.small_font = pygame.font.SysFont("Arial", 20)
        
        # Game state management
        self.game_state = "playing"  # "playing" or "game_over"
        self.winning_score = 5
        self.winner = None

    def handle_input(self, events):
        keys = pygame.key.get_pressed()
        
        if self.game_state == "playing":
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)
        elif self.game_state == "game_over":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"
        
        return None
    
    def restart_game(self):
        """Reset the game to initial state"""
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        self.game_state = "playing"
        self.ball.reset()

    def update(self):
        if self.game_state == "playing":
            self.ball.move()
            self.ball.check_collision(self.player, self.ai)

            if self.ball.x <= 0:
                self.ai_score += 1
                self.ball.reset()
                self.check_win_condition()
            elif self.ball.x >= self.width:
                self.player_score += 1
                self.ball.reset()
                self.check_win_condition()

            self.ai.auto_track(self.ball, self.height)
    
    def check_win_condition(self):
        """Check if either player has won the game"""
        if self.player_score >= self.winning_score:
            self.winner = "Player"
            self.game_state = "game_over"
        elif self.ai_score >= self.winning_score:
            self.winner = "AI"
            self.game_state = "game_over"

    def render(self, screen):
        if self.game_state == "playing":
            # Draw paddles and ball
            pygame.draw.rect(screen, WHITE, self.player.rect())
            pygame.draw.rect(screen, WHITE, self.ai.rect())
            pygame.draw.ellipse(screen, WHITE, self.ball.rect())
            pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

            # Draw score
            player_text = self.font.render(str(self.player_score), True, WHITE)
            ai_text = self.font.render(str(self.ai_score), True, WHITE)
            screen.blit(player_text, (self.width//4, 20))
            screen.blit(ai_text, (self.width * 3//4, 20))
        
        elif self.game_state == "game_over":
            self.render_game_over(screen)
    
    def render_game_over(self, screen):
        """Render the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Winner announcement
        winner_color = GREEN if self.winner == "Player" else RED
        winner_text = self.big_font.render(f"{self.winner} Wins!", True, winner_color)
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 80))
        screen.blit(winner_text, winner_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {self.player_score} - {self.ai_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.width//2, self.height//2 - 20))
        screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.small_font.render("Press 'R' to play again or 'ESC' to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 40))
        screen.blit(restart_text, restart_rect)
