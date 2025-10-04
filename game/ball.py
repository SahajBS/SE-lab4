import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height, game_engine=None):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        self.game_engine = game_engine

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Bounce off top and bottom walls with position correction
        if self.y <= 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y)
            if self.game_engine:
                self.game_engine.play_sound("wall")
        elif self.y + self.height >= self.screen_height:
            self.y = self.screen_height - self.height
            self.velocity_y = -abs(self.velocity_y)
            if self.game_engine:
                self.game_engine.play_sound("wall")

    def check_collision(self, player, ai):
        ball_rect = self.rect()
        
        # Check collision with player paddle (left side)
        if (self.velocity_x < 0 and 
            ball_rect.colliderect(player.rect()) and 
            self.x > player.x + player.width // 2):
            self.velocity_x = abs(self.velocity_x)  # Ensure ball moves right
            # Position correction to prevent tunneling
            self.x = player.x + player.width
            # Add variation based on where ball hits paddle
            hit_pos = (self.y + self.height // 2 - player.y) / player.height
            self.velocity_y += (hit_pos - 0.5) * 3
            if self.game_engine:
                self.game_engine.play_sound("paddle")
            
        # Check collision with AI paddle (right side)  
        elif (self.velocity_x > 0 and 
              ball_rect.colliderect(ai.rect()) and 
              self.x < ai.x + ai.width // 2):
            self.velocity_x = -abs(self.velocity_x)  # Ensure ball moves left
            # Position correction to prevent tunneling
            self.x = ai.x - self.width
            # Add variation based on where ball hits paddle
            hit_pos = (self.y + self.height // 2 - ai.y) / ai.height
            self.velocity_y += (hit_pos - 0.5) * 3
            if self.game_engine:
                self.game_engine.play_sound("paddle")
            
        # Clamp velocity_y to reasonable bounds to prevent crazy bounces
        self.velocity_y = max(-8, min(8, self.velocity_y))

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.velocity_x *= -1
        self.velocity_y = random.choice([-3, 3])

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
