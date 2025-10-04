import pygame
import numpy as np
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
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height, self)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 60)
        self.small_font = pygame.font.SysFont("Arial", 20)
        
        # Game state management
        self.game_state = "menu"  # "menu", "playing", "game_over", "series_over"
        self.winning_score = 5
        self.winner = None
        self.match_options = [3, 5, 7]  # Best of 3, 5, or 7
        self.selected_match = 1  # Index for match_options (default: 5)
        
        # Series tracking
        self.series_length = 5  # Will be set when game starts
        self.player_series_wins = 0
        self.ai_series_wins = 0
        self.games_played = 0
        self.series_winner = None
        
        # Initialize sound system
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.sounds_enabled = True
            print("Sound system initialized successfully")
            self.generate_sounds()
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            self.sounds_enabled = False

    def handle_input(self, events):
        keys = pygame.key.get_pressed()
        
        if self.game_state == "menu":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_match = (self.selected_match - 1) % len(self.match_options)
                        self.play_sound("click")
                    elif event.key == pygame.K_DOWN:
                        self.selected_match = (self.selected_match + 1) % len(self.match_options)
                        self.play_sound("click")
                    elif event.key == pygame.K_RETURN:
                        self.play_sound("click")
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"
        
        elif self.game_state == "playing":
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)
                
        elif self.game_state == "game_over":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_next_game()  # Continue to next game in series
                    elif event.key == pygame.K_r:
                        self.game_state = "menu"  # Return to menu for new series
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"
        
        elif self.game_state == "series_over":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.game_state = "menu"  # Return to menu for new series
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"
        
        return None
    
    def start_game(self):
        """Start a new series with selected match type"""
        self.winning_score = 5  # Individual game winning score
        self.series_length = self.match_options[self.selected_match]
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        # Reset series tracking
        self.player_series_wins = 0
        self.ai_series_wins = 0
        self.games_played = 0
        self.series_winner = None
        self.game_state = "playing"
        self.ball.reset()


    def update(self):
        if self.game_state == "playing":
            self.ball.move()
            self.ball.check_collision(self.player, self.ai)

            if self.ball.x <= 0:
                self.ai_score += 1
                self.play_sound("score")
                self.ball.reset()
                self.check_win_condition()
            elif self.ball.x >= self.width:
                self.player_score += 1
                self.play_sound("score")
                self.ball.reset()
                self.check_win_condition()

            self.ai.auto_track(self.ball, self.height)
    
    def check_win_condition(self):
        """Check if either player has won the game"""
        if self.player_score >= self.winning_score:
            self.winner = "Player"
            self.record_series_score("Player")
            self.game_state = "game_over"
        elif self.ai_score >= self.winning_score:
            self.winner = "AI"
            self.record_series_score("AI")
            self.game_state = "game_over"
    
    def record_series_score(self, game_winner):
        """Record the winner of the current game and check for series completion"""
        self.games_played += 1
        
        if game_winner == "Player":
            self.player_series_wins += 1
        elif game_winner == "AI":
            self.ai_series_wins += 1
        
        # Check if series is complete (need to win majority of games)
        games_to_win = (self.series_length + 1) // 2  # e.g., 2 for best of 3, 3 for best of 5
        
        if self.player_series_wins >= games_to_win:
            self.series_winner = "Player"
            self.game_state = "series_over"
        elif self.ai_series_wins >= games_to_win:
            self.series_winner = "AI"
            self.game_state = "series_over"
    
    def start_next_game(self):
        """Start the next game in the current series"""
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        self.game_state = "playing"
        self.ball.reset()

    def render(self, screen):
        if self.game_state == "menu":
            self.render_menu(screen)
            
        elif self.game_state == "playing":
            # Draw paddles and ball
            pygame.draw.rect(screen, WHITE, self.player.rect())
            pygame.draw.rect(screen, WHITE, self.ai.rect())
            pygame.draw.ellipse(screen, WHITE, self.ball.rect())
            pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

            # Draw current game score
            player_text = self.font.render(str(self.player_score), True, WHITE)
            ai_text = self.font.render(str(self.ai_score), True, WHITE)
            screen.blit(player_text, (self.width//4, 20))
            screen.blit(ai_text, (self.width * 3//4, 20))
            
            # Draw series score
            series_text = self.small_font.render(f"Series: P{self.player_series_wins} - {self.ai_series_wins}A | Game {self.games_played + 1}/{self.series_length}", True, WHITE)
            series_rect = series_text.get_rect(center=(self.width//2, 60))
            screen.blit(series_text, series_rect)
        
        elif self.game_state == "game_over":
            self.render_game_over(screen)
        
        elif self.game_state == "series_over":
            self.render_series_over(screen)
    
    def render_game_over(self, screen):
        """Render the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Winner announcement
        winner_color = GREEN if self.winner == "Player" else RED
        winner_text = self.big_font.render(f"{self.winner} Wins Game!", True, winner_color)
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 100))
        screen.blit(winner_text, winner_rect)
        
        # Game score
        score_text = self.font.render(f"Game Score: {self.player_score} - {self.ai_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.width//2, self.height//2 - 60))
        screen.blit(score_text, score_rect)
        
        # Series progress
        series_text = self.font.render(f"Series Score: Player {self.player_series_wins} - {self.ai_series_wins} AI", True, WHITE)
        series_rect = series_text.get_rect(center=(self.width//2, self.height//2 - 20))
        screen.blit(series_text, series_rect)
        
        # Game progress
        progress_text = self.small_font.render(f"Game {self.games_played} of {self.series_length} (Best of {self.series_length})", True, WHITE)
        progress_rect = progress_text.get_rect(center=(self.width//2, self.height//2 + 10))
        screen.blit(progress_text, progress_rect)
        
        # Instructions
        if self.series_winner is None:  # Series not over yet
            next_text = self.small_font.render("Press SPACE for next game, 'R' for new series, or 'ESC' to quit", True, WHITE)
        else:
            next_text = self.small_font.render("Press 'R' for new series or 'ESC' to quit", True, WHITE)
        next_rect = next_text.get_rect(center=(self.width//2, self.height//2 + 50))
        screen.blit(next_text, next_rect)
    
    def render_series_over(self, screen):
        """Render the series completion screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Series winner announcement
        winner_color = GREEN if self.series_winner == "Player" else RED
        winner_text = self.big_font.render(f"{self.series_winner} Wins Series!", True, winner_color)
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 80))
        screen.blit(winner_text, winner_rect)
        
        # Final series score
        series_text = self.font.render(f"Final Series Score: Player {self.player_series_wins} - {self.ai_series_wins} AI", True, WHITE)
        series_rect = series_text.get_rect(center=(self.width//2, self.height//2 - 20))
        screen.blit(series_text, series_rect)
        
        # Series type
        series_type_text = self.small_font.render(f"Best of {self.series_length} Series Complete", True, WHITE)
        series_type_rect = series_type_text.get_rect(center=(self.width//2, self.height//2 + 10))
        screen.blit(series_type_text, series_type_rect)
        
        # Instructions
        restart_text = self.small_font.render("Press 'R' to start new series or 'ESC' to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 50))
        screen.blit(restart_text, restart_rect)
    
    def generate_sounds(self):
        """Generate simple sound effects using numpy"""
        try:
            import pygame.sndarray
            sample_rate = 22050
            
            print("Generating sound effects...")
            
            # Generate paddle hit sound (short beep at 800Hz)
            duration = 0.15
            frequency = 800
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            paddle_wave = np.sin(frequency * 2 * np.pi * t) * 0.5
            # Add slight decay
            envelope = np.exp(-t * 8)
            paddle_wave *= envelope
            # Create stereo sound and ensure C-contiguous
            paddle_sound = np.column_stack((paddle_wave, paddle_wave))
            paddle_sound = np.ascontiguousarray((paddle_sound * 32767).astype(np.int16))
            self.paddle_sound = pygame.sndarray.make_sound(paddle_sound)
            print("Paddle sound generated")
            
            # Generate wall bounce sound (lower pitch at 300Hz)
            frequency = 300
            t_wall = np.linspace(0, duration, int(sample_rate * duration), False)
            wall_wave = np.sin(frequency * 2 * np.pi * t_wall) * 0.4
            wall_wave *= np.exp(-t_wall * 8)
            wall_sound = np.column_stack((wall_wave, wall_wave))
            wall_sound = np.ascontiguousarray((wall_sound * 32767).astype(np.int16))
            self.wall_sound = pygame.sndarray.make_sound(wall_sound)
            print("Wall bounce sound generated")
            
            # Generate score sound (ascending chord)
            duration = 0.5
            t_score = np.linspace(0, duration, int(sample_rate * duration), False)
            # Create a chord with multiple frequencies
            freq1, freq2 = 440, 554  # A and C# notes
            score_wave = (np.sin(freq1 * 2 * np.pi * t_score) + 
                         np.sin(freq2 * 2 * np.pi * t_score)) * 0.3
            # Add envelope for smooth fade
            envelope = np.exp(-t_score * 3)
            score_wave *= envelope
            score_sound = np.column_stack((score_wave, score_wave))
            score_sound = np.ascontiguousarray((score_sound * 32767).astype(np.int16))
            self.score_sound = pygame.sndarray.make_sound(score_sound)
            print("Score sound generated")
            
            # Generate menu navigation sound (short click)
            duration = 0.08
            frequency = 1200
            t_click = np.linspace(0, duration, int(sample_rate * duration), False)
            click_wave = np.sin(frequency * 2 * np.pi * t_click) * 0.3
            click_wave *= np.exp(-t_click * 15)  # Quick decay
            click_sound = np.column_stack((click_wave, click_wave))
            click_sound = np.ascontiguousarray((click_sound * 32767).astype(np.int16))
            self.click_sound = pygame.sndarray.make_sound(click_sound)
            print("Click sound generated")
            
            print("All sounds generated successfully!")
            
            # Set volume levels
            self.paddle_sound.set_volume(0.7)
            self.wall_sound.set_volume(0.5)
            self.score_sound.set_volume(0.8)
            self.click_sound.set_volume(0.6)
            
        except Exception as e:
            print(f"Could not generate sounds: {e}")
            import traceback
            traceback.print_exc()
            self.sounds_enabled = False
    
    def play_sound(self, sound_type):
        """Play a sound effect"""
        if not self.sounds_enabled:
            print(f"Sounds disabled, cannot play {sound_type}")
            return
            
        try:
            print(f"Playing {sound_type} sound")
            if sound_type == "paddle" and hasattr(self, 'paddle_sound'):
                self.paddle_sound.play()
            elif sound_type == "wall" and hasattr(self, 'wall_sound'):
                self.wall_sound.play()
            elif sound_type == "score" and hasattr(self, 'score_sound'):
                self.score_sound.play()
            elif sound_type == "click" and hasattr(self, 'click_sound'):
                self.click_sound.play()
            else:
                print(f"Sound {sound_type} not found or not loaded")
        except Exception as e:
            print(f"Error playing sound {sound_type}: {e}")
            import traceback
            traceback.print_exc()
    
    def render_menu(self, screen):
        """Render the match selection menu"""
        # Title
        title_text = self.big_font.render("PING PONG", True, WHITE)
        title_rect = title_text.get_rect(center=(self.width//2, self.height//2 - 120))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font.render("Choose Match Type:", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(self.width//2, self.height//2 - 60))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Match options
        for i, option in enumerate(self.match_options):
            color = GREEN if i == self.selected_match else WHITE
            option_text = self.font.render(f"Best of {option}", True, color)
            option_rect = option_text.get_rect(center=(self.width//2, self.height//2 - 10 + i * 40))
            screen.blit(option_text, option_rect)
            
            # Draw selection indicator
            if i == self.selected_match:
                pygame.draw.rect(screen, GREEN, option_rect.inflate(20, 10), 2)
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to select",
            "Press ENTER to start game", 
            "Use W/S to move paddle",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, WHITE)
            inst_rect = inst_text.get_rect(center=(self.width//2, self.height//2 + 80 + i * 25))
            screen.blit(inst_text, inst_rect)
