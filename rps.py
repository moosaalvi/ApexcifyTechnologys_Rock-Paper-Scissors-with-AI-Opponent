import pygame
import random
import sys
from collections import Counter

# --- 1. CONFIGURATION & INITIALIZATION ---
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rock Paper and Scissors with AI opponent")
CLOCK = pygame.time.Clock()

# Colors (Same)
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GRAY = (200, 200, 200)
DARK_BLUE = (30, 30, 60)
YELLOW = (255, 255, 0)
GREEN_LITE = (50, 200, 50)
RED_LITE = (200, 50, 50)
ORANGE = (255, 180, 0)
BUTTON_COLOR = (100, 100, 200)
MUTE_BUTTON_COLOR = (255, 100, 100)

# Fonts - FINAL ADJUSTMENT
FONT_XL = pygame.font.Font(None, 85) 
FONT_LG = pygame.font.Font(None, 55)   # Reduced from 60/65 -> FINAL MESSAGE FIX
FONT_MD = pygame.font.Font(None, 35)   # Reduced from 40/45 -> BUTTON TEXT FIX
FONT_SM = pygame.font.Font(None, 30)   # Reduced from 35

# Game Constants (Same)
CHOICES = ['rock', 'paper', 'scissors']
WINNING_RULES = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
MAX_ROUNDS_OPTIONS = [3, 5, 7, 10]

# --- 2. ASSETS LOADING (Same) ---
ASSET_MAP = {}
SOUNDS = {}

def load_assets():
    global ASSET_MAP, SOUNDS
    try:
        IMAGE_SIZE = (150, 150)
        for choice in CHOICES:
            img = pygame.image.load(f'assets/{choice}.png').convert_alpha()
            ASSET_MAP[choice] = pygame.transform.scale(img, IMAGE_SIZE)
        
        pygame.mixer.init() 
        SOUNDS['win'] = pygame.mixer.Sound('assets/win.wav')
        SOUNDS['loss'] = pygame.mixer.Sound('assets/loss.wav')
        SOUNDS['tie'] = pygame.mixer.Sound('assets/tie.wav')
        print("Assets loaded successfully.")
    
    except pygame.error as e:
        print(f"CRITICAL ERROR: Failed to load assets. Details: {e}")
        DUMMY_SURFACE = pygame.Surface((150, 150))
        DUMMY_SURFACE.fill(GRAY)
        for choice in CHOICES: ASSET_MAP[choice] = DUMMY_SURFACE
        SOUNDS['win'] = lambda: None
        SOUNDS['loss'] = lambda: None
        SOUNDS['tie'] = lambda: None

# --- 3. UI ELEMENT CLASS (Uses new FONT_MD and FONT_SM) ---
class Button:
    def __init__(self, x, y, width, height, text, action=None, base_color=BUTTON_COLOR, font=FONT_MD):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.base_color = base_color
        self.hover_color = tuple(min(255, c + 50) for c in base_color)
        self.click_color = (255, 200, 200) 
        self.is_clicked = False
        self.font = font

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.is_clicked:
            color_to_draw = self.click_color
            self.is_clicked = False 
        elif self.rect.collidepoint(mouse_pos):
            color_to_draw = self.hover_color
        else:
            color_to_draw = self.base_color
        
        shadow_offset = 4
        pygame.draw.rect(surface, BLACK, self.rect.move(shadow_offset, shadow_offset), border_radius=15)
        
        pygame.draw.rect(surface, color_to_draw, self.rect, border_radius=15)
        
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_clicked = True
                if self.action:
                    self.action()
                    return True
        return False

# --- 4. GAME CLASS ---
class PygameRPS:
    def __init__(self):
        self.user_score = 0
        self.computer_score = 0
        self.rounds_played = 0
        self.max_rounds = 5
        self.user_choice = None
        self.computer_choice = None
        self.winner_choice = None
        self.result_message = "WELCOME TO THE ARENA!"
        self.result_color = YELLOW
        self.play_buttons = self._create_play_buttons()
        self.menu_buttons = []
        self.game_state = 'MENU' 
        self.last_round_end_time = 0
        self.user_history = []
        self.is_muted = False
        self.mute_button = self._create_mute_button()
        
        self.ai_counter_bias = 0.70
        self.ai_win_streak = 0
        self.last_winner = 0

        if pygame.mixer.get_init():
             pygame.mixer.unpause()

    # --- Button Creation (Using new FONT_MD) ---
    def _create_play_buttons(self):
        x_rock = SCREEN_WIDTH // 2 - 270
        x_paper = SCREEN_WIDTH // 2 - 80
        x_scissors = SCREEN_WIDTH // 2 + 110
        button_y = SCREEN_HEIGHT - 120
        button_w = 150 
        button_h = 70
        
        buttons = [
            Button(x_rock, button_y, button_w, button_h, 'ROCK', lambda: self.play_round('rock'), (255, 100, 100), FONT_MD),
            Button(x_paper, button_y, button_w, button_h, 'PAPER', lambda: self.play_round('paper'), (100, 100, 255), FONT_MD),
            Button(x_scissors, button_y, button_w, button_h, 'SCISSORS', lambda: self.play_round('scissors'), (100, 255, 100), FONT_MD)
        ]
        return buttons
    
    def _create_mute_button(self):
        # Mute button uses FONT_SM
        MUTE_BTN_WIDTH = 180
        MUTE_BTN_X = SCREEN_WIDTH - MUTE_BTN_WIDTH - 20 
        return Button(MUTE_BTN_X, 20, MUTE_BTN_WIDTH, 40, 'MUTE', self.toggle_mute, MUTE_BUTTON_COLOR, FONT_SM)

    # --- State Management (No Change) ---
    def start_game(self, rounds):
        self.max_rounds = rounds
        self.reset_game(set_state='PLAYING')

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if pygame.mixer.get_init():
            if self.is_muted:
                pygame.mixer.pause()
                self.mute_button.text = "UNMUTE (Muted)"
            else:
                pygame.mixer.unpause()
                self.mute_button.text = "MUTE"
        
    def reset_game(self, set_state='MENU'):
        self.user_score = 0
        self.computer_score = 0
        self.rounds_played = 0
        self.user_choice = None
        self.computer_choice = None
        self.winner_choice = None
        self.result_message = "WELCOME TO THE ARENA!"
        self.result_color = YELLOW
        self.game_state = set_state
        self.last_round_end_time = 0
        self.user_history = []
        
        self.ai_counter_bias = 0.70
        self.ai_win_streak = 0
        self.last_winner = 0

        if not self.is_muted and pygame.mixer.get_init():
            pygame.mixer.unpause()

    def _get_final_result(self):
        if self.user_score > self.computer_score:
            return "FINAL VICTOR: PLAYER! 🏆"
        elif self.computer_score > self.user_score:
            return "FINAL VICTOR: COMPUTER! 🤖"
        else:
            return "SERIES DRAW! 🤝"

    # --- Advanced AI Logic (No Change) ---
    def get_smart_computer_choice(self):
        if len(self.user_history) < 3:
            return random.choice(CHOICES)
        
        # Pattern Recognition 
        if len(self.user_history) >= 2:
            last_two = tuple(self.user_history[-2:])
            if last_two == ('paper', 'rock'): return 'paper'
            if last_two == ('scissors', 'paper'): return 'scissors'
            if last_two == ('rock', 'scissors'): return 'rock'
            
        # Most Common Counter (Dynamic Bias)
        counts = Counter(self.user_history)
        most_common_move = counts.most_common(1)[0][0]

        counter_move_map = {v: k for k, v in WINNING_RULES.items()}
        counter_move = counter_move_map[most_common_move]
        
        if random.random() < self.ai_counter_bias:
            return counter_move
        else:
            return random.choice(CHOICES)

    # --- Game Logic (Dynamic Bias Update Added) ---
    def determine_winner(self, user_choice, computer_choice):
        self.rounds_played += 1
        self.user_history.append(user_choice)
        
        if user_choice == computer_choice:
            winner_code = 0
            message, color = "IT'S A TIE! 🤝", ORANGE
            self.winner_choice = None
            if not self.is_muted and SOUNDS['tie'] is not None and not callable(SOUNDS['tie']): 
                SOUNDS['tie'].play()
        
        elif WINNING_RULES.get(user_choice) == computer_choice:
            self.user_score += 1
            winner_code = 1
            message, color = f"YOU WIN! {user_choice.capitalize()} takes it!", GREEN_LITE
            self.winner_choice = user_choice
            if not self.is_muted and SOUNDS['win'] is not None and not callable(SOUNDS['win']): 
                SOUNDS['win'].play()
        
        else:
            self.computer_score += 1
            winner_code = -1
            message, color = f"COMPUTER WINS! {computer_choice.capitalize()} dominates.", RED_LITE
            self.winner_choice = computer_choice
            if not self.is_muted and SOUNDS['loss'] is not None and not callable(SOUNDS['loss']): 
                SOUNDS['loss'].play()
        
        # --- Dynamic AI Bias Adjustment ---
        if winner_code == -1: 
            self.ai_win_streak = max(1, self.ai_win_streak + 1)
        elif winner_code == 1: 
            self.ai_win_streak = min(-1, self.ai_win_streak - 1)
        else:
            self.ai_win_streak = 0
            
        if self.ai_win_streak >= 3: 
            self.ai_counter_bias = min(0.90, self.ai_counter_bias + 0.05) 
        elif self.ai_win_streak <= -3:
            self.ai_counter_bias = max(0.50, self.ai_counter_bias - 0.05)
        
        self.last_winner = winner_code
        
        return winner_code, message, color

    def play_round(self, user_choice):
        if self.game_state != 'PLAYING': return
        
        self.user_choice = user_choice
        self.computer_choice = self.get_smart_computer_choice() 
        
        _, message, color = self.determine_winner(self.user_choice, self.computer_choice)
        self.result_message = message
        self.result_color = color
        
        self.last_round_end_time = pygame.time.get_ticks()

        if self.rounds_played >= self.max_rounds:
            self.game_state = 'GAME_OVER_DELAY' 

    # --- Drawing/Rendering (Menu Button Fix Applied) ---
    def draw(self, surface):
        surface.fill(DARK_BLUE)
        
        if self.game_state == 'MENU':
            self._draw_menu(surface)
        elif self.game_state in ('PLAYING', 'GAME_OVER_DELAY'):
            self._draw_playing_screen(surface)
        elif self.game_state == 'GAME_OVER':
            self._draw_playing_screen(surface)
            self._draw_game_over_screen(surface)
        
        self.mute_button.draw(surface)

        pygame.display.flip()

    def _draw_menu(self, surface):
        title_text = FONT_XL.render("RPS: ULTIMATE PRO BUILD", True, YELLOW)
        surface.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        prompt_text = FONT_LG.render("SELECT ROUNDS (Best Of N)", True, WHITE)
        surface.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 200))

        # Menu Button Fix: FINAL Sizing
        self.menu_buttons = []
        start_x = SCREEN_WIDTH // 2 - 320 
        button_y = 350
        spacing = 160 
        button_w = 140 
        
        for i, rounds in enumerate(MAX_ROUNDS_OPTIONS):
            # Using FONT_MD (35) which is smaller than previous FONT_MD (40/45)
            btn = Button(start_x + i * spacing, button_y, button_w, 60, f"BO {rounds}", 
                         action=lambda r=rounds: self.start_game(r), base_color=BUTTON_COLOR, font=FONT_MD) 
            self.menu_buttons.append(btn)
            btn.draw(surface)

    def _draw_playing_screen(self, surface):
        
        # Aligned Scores and Title
        title_text = FONT_LG.render("BATTLE ARENA", True, WHITE)
        surface.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))
        
        score_user = FONT_MD.render(f"YOU: {self.user_score}", True, GREEN_LITE)
        score_comp = FONT_MD.render(f"COMP: {self.computer_score}", True, RED_LITE)
        surface.blit(score_user, (50, 80))
        surface.blit(score_comp, (SCREEN_WIDTH - 50 - score_comp.get_width(), 80))
        
        # Display current AI Bias
        bias_text = FONT_SM.render(f"AI Bias: {self.ai_counter_bias:.2f}", True, GRAY)
        surface.blit(bias_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))
        
        round_text = FONT_SM.render(f"Round {self.rounds_played} of {self.max_rounds}", True, GRAY)
        surface.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, 120))

        # Result Message (Alignment Fix: Using FONT_LG=55)
        result_text = FONT_LG.render(self.result_message, True, self.result_color)
        surface.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 190))

        # Visual Choices Display
        self._draw_choices_visual(surface)
        
        # Draw Play Buttons
        if self.game_state == 'PLAYING':
            for button in self.play_buttons:
                button.draw(surface)
            
        # Handle Post-Round Delay
        self._handle_delay_and_game_over(surface)


    def _draw_choices_visual(self, surface):
        
        pygame.draw.line(surface, WHITE, (SCREEN_WIDTH // 2, 250), (SCREEN_WIDTH // 2, 450), 3)

        # Draw User's choice (Left)
        if self.user_choice:
            user_img = ASSET_MAP[self.user_choice]
            img_x, img_y = 200 - user_img.get_width() // 2, 350 - user_img.get_height() // 2
            
            if self.winner_choice == self.user_choice:
                pygame.draw.circle(surface, GREEN_LITE, (200, 350), 100, 0)
                
            surface.blit(user_img, (img_x, img_y))

        # Draw Computer's choice (Right)
        if self.computer_choice:
            comp_img = pygame.transform.flip(ASSET_MAP[self.computer_choice], True, False)
            img_x, img_y = SCREEN_WIDTH - 200 - comp_img.get_width() // 2, 350 - comp_img.get_height() // 2
            
            if self.winner_choice == self.computer_choice:
                pygame.draw.circle(surface, RED_LITE, (SCREEN_WIDTH - 200, 350), 100, 0)
            
            surface.blit(comp_img, (img_x, img_y))

    def _handle_delay_and_game_over(self, surface):
        
        # Result Display Delay (1.0 second)
        if self.game_state == 'GAME_OVER_DELAY':
            if pygame.time.get_ticks() - self.last_round_end_time > 1000:
                self.game_state = 'PLAYING' if self.rounds_played < self.max_rounds else 'GAME_OVER'

    def _draw_game_over_screen(self, surface):
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220) 
        overlay.fill(DARK_BLUE)
        surface.blit(overlay, (0, 0))

        # Final Message
        final_text = FONT_XL.render(self._get_final_result(), True, YELLOW)
        rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(final_text, rect)
        
        # Final Score
        final_score_text = FONT_LG.render(f"Final Score: You {self.user_score} | Comp {self.computer_score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        surface.blit(final_score_text, score_rect)

        # Advanced Stat Tracking
        if self.user_history:
            total_moves = len(self.user_history)
            win_rate = (self.user_score / total_moves) * 100 if total_moves > 0 else 0
            
            counts = Counter(self.user_history)
            most_common = counts.most_common(1)[0][0] if counts else "N/A"

            stat_line1 = FONT_MD.render(f"Win Rate: {win_rate:.1f}%", True, GREEN_LITE)
            stat_line2 = FONT_MD.render(f"Your Favorite Move: {most_common.upper()}", True, ORANGE)
            
            surface.blit(stat_line1, (SCREEN_WIDTH // 2 - stat_line1.get_width() // 2, 280))
            surface.blit(stat_line2, (SCREEN_WIDTH // 2 - stat_line2.get_width() // 2, 330))


        # Restart Button
        restart_button = Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 120, 240, 60, 'NEW GAME', self.reset_game, GREEN_LITE, FONT_LG)
        restart_button.draw(surface)

# --- 5. MAIN LOOP ---
def main():
    load_assets()
    game = PygameRPS()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            game.mute_button.handle_event(event)
            
            if game.game_state == 'MENU':
                for button in game.menu_buttons:
                    button.handle_event(event)
                    
            elif game.game_state == 'PLAYING':
                for button in game.play_buttons:
                    button.handle_event(event)
            
            elif game.game_state == 'GAME_OVER':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if SCREEN_WIDTH // 2 - 120 <= x <= SCREEN_WIDTH // 2 + 120 and \
                       SCREEN_HEIGHT // 2 + 120 <= y <= SCREEN_HEIGHT // 2 + 180:
                        game.reset_game()
        
        game.draw(SCREEN)
        CLOCK.tick(30) 

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()