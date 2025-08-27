import pygame
import sys
import random
import json
import os
import math
from sounds import SoundManager
from ffpyplayer.player import MediaPlayer
from leaderboard import leaderboard
from sounds import SoundManager

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
VIDEO_FILE = 'background_video.mp4'
FPS = 60

# Progress bar
PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_COLOR = (100, 100, 255)  # Light blue
PROGRESS_BAR_BG_COLOR = (50, 50, 80)  # Dark blue-gray
LANE_COUNT = 4
LANE_WIDTH = 100
NOTE_HEIGHT = 20
NOTE_SPEED = 5
JUDGMENT_LINE = HEIGHT - 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0)   # Yellow
]

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Python Rhythm Game")
clock = pygame.time.Clock()

# Update judgment line position based on screen height
JUDGMENT_LINE = HEIGHT - 100

# Game variables
score = 0
combo = 0
notes = []
active_notes = set()  # Track which notes are currently being hit
spawn_timer = 0
spawn_interval = 60  # frames
key_bindings = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
key_states = {key: False for key in key_bindings}  # Track key states
high_scores = []
MAX_HIGH_SCORES = 5
DIFFICULTIES = {
    'beginner': {'speed': 2, 'interval': (1000, 1500), 'bpm': 60},
    'easy': {'speed': 3, 'interval': (800, 1200), 'bpm': 90},
    'normal': {'speed': 5, 'interval': (600, 1000), 'bpm': 120},
    'hard': {'speed': 7, 'interval': (400, 800), 'bpm': 150},
    'expert': {'speed': 9, 'interval': (200, 600), 'bpm': 180}
}
current_difficulty = 'normal'

# Beat detection
BEAT_MARGIN = 30  # Pixels of leeway for hitting notes
last_beat_time = 0
beat_interval = 0  # Will be set based on BPM

# Visual feedback
hit_effects = []  # List to store hit effects
MISS_COLOR = (255, 50, 50)  # Red tint for misses
HIT_COLOR = (100, 255, 100)  # Green tint for hits
feedback_duration = 10  # Frames to show feedback
feedback_timer = 0
current_feedback = None  # 'hit' or 'miss'

# Initialize sound manager and load music
def load_background_music():
    try:
        pygame.mixer.music.load('background_music.mp3')
        pygame.mixer.music.set_volume(0.5)  # 50% volume
    except Exception as e:
        print(f"Could not load background music: {e}")

sound_manager = SoundManager()
load_background_music()
sound_manager.load_sounds()


# Video playback
video_player = None
video_size = (WIDTH, HEIGHT)
video_pos = (0, 0)

def init_video():
    global video_player, video_size, video_pos, background_image
    video_player = None
    
    # Try to load video first
    try:
        if os.path.exists(VIDEO_FILE):
            video_player = MediaPlayer(VIDEO_FILE, loop=True, ff_opts={'paused': False, 'sync': 'video'})
            video_info = video_player.get_metadata()
            if video_info and 'src_vid_size' in video_info:
                video_width, video_height = video_info['src_vid_size']
                if video_width > 0 and video_height > 0:  # Ensure valid dimensions
                    video_ratio = video_width / video_height
                    target_width = int(HEIGHT * video_ratio)
                    video_size = (max(100, min(target_width, WIDTH)), HEIGHT)  # Ensure reasonable size
                    video_pos = ((WIDTH - video_size[0]) // 2, 0)
                    print(f"Video initialized: {video_size[0]}x{video_size[1]}")
                    return
    except Exception as e:
        print(f"Video initialization warning: {e}")
    
    # Fallback to static background if video fails
    try:
        background_image = pygame.image.load('menu_background.jpg').convert()
        img_ratio = background_image.get_width() / background_image.get_height()
        target_width = int(HEIGHT * img_ratio)
        background_image = pygame.transform.scale(background_image, (target_width, HEIGHT))
        print("Using static background image")
    except Exception as e:
        print(f"Failed to load background image: {e}")
        background_image = None

def update_video():
    if video_player:
        frame, val = video_player.get_frame()
        if frame != 'eof' and frame is not None:
            # Convert frame to Pygame surface
            img, pts = frame
            img_data = img.to_bytearray()[0]
            video_surface = pygame.image.frombuffer(
                img_data, img.get_size(), 'RGB'
            ).convert()
            
            # Scale the video to fit the screen while maintaining aspect ratio
            video_surface = pygame.transform.scale(video_surface, video_size)
            return video_surface
    return None

def draw_video():
    # Try to draw video frame
    if video_player:
        video_frame = update_video()
        if video_frame:
            screen.blit(video_frame, video_pos)
    # Fall back to static background if available
    elif background_image:
        screen.blit(background_image, ((WIDTH - background_image.get_width()) // 2, 0))
    # Fall back to black background
    else:
        screen.fill(BLACK)
    
    # Add dark overlay for better visibility
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

# Load high scores
try:
    with open('highscores.json', 'r') as f:
        high_scores = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    high_scores = [{'name': 'Player', 'score': 0, 'difficulty': 'normal'}] * 5

# Set note speed based on difficulty
NOTE_SPEED = DIFFICULTIES[current_difficulty]['speed']

# Initialize font
font = pygame.font.Font(None, 36)

class Note:
    def __init__(self, lane):
        self.lane = lane
        self.y = -NOTE_HEIGHT
        self.width = LANE_WIDTH - 10
        self.height = NOTE_HEIGHT
        self.x = (WIDTH - LANE_COUNT * LANE_WIDTH) // 2 + lane * LANE_WIDTH + 5
        self.hit = False
        self.missed = False
        self.speed = NOTE_SPEED
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.missed = True
    
    def draw(self, surface):
        if not self.hit and not self.missed:
            pygame.draw.rect(surface, COLORS[self.lane], 
                           (self.x, self.y, self.width, self.height))

    def check_hit(self, key_pressed):
        if not self.hit and not self.missed and key_pressed:
            distance = abs((self.y + self.height/2) - JUDGMENT_LINE)
            if distance < 30:  # Hit window of 30 pixels
                self.hit = True
                return 'hit'
            elif distance < 60:  # Near miss window
                self.missed = True
                return 'near_miss'
        return 'miss'

def spawn_note():
    # Only spawn notes on beats
    current_time = pygame.time.get_ticks()
    if current_time - last_beat_time >= beat_interval * 0.8:  # 80% into the beat
        lane = random.randint(0, LANE_COUNT - 1)
        note = Note(lane)
        note.speed = NOTE_SPEED
        notes.append(note)
        return True
    return False

def draw_judgment_line():
    pygame.draw.rect(screen, WHITE, (0, JUDGMENT_LINE, WIDTH, 2))

def draw_lanes():
    # Draw semi-transparent lane backgrounds
    for i in range(LANE_COUNT):
        x = (WIDTH - LANE_COUNT * LANE_WIDTH) // 2 + i * LANE_WIDTH
        lane_surface = pygame.Surface((LANE_WIDTH, HEIGHT), pygame.SRCALPHA)
        lane_surface.fill((255, 255, 255, 10))  # Semi-transparent white
        screen.blit(lane_surface, (x, 0))
    
    # Draw lane dividers
    for i in range(LANE_COUNT + 1):
        x = (WIDTH - LANE_COUNT * LANE_WIDTH) // 2 + i * LANE_WIDTH
        pygame.draw.line(screen, (100, 100, 100, 100), (x, 0), (x, HEIGHT), 2)

def draw_score():
    score_text = font.render(f'Score: {int(score)}', True, WHITE)
    combo_text = font.render(f'Combo: {combo}', True, WHITE)
    screen.blit(score_text, (20, PROGRESS_BAR_HEIGHT + 20))
    screen.blit(combo_text, (20, PROGRESS_BAR_HEIGHT + 60))
    
    # Draw combo text with size based on combo count
    if combo > 5:
        combo_size = min(36 + combo, 72)  # Cap the maximum size
        combo_font = pygame.font.Font(None, int(combo_size))
        combo_text = combo_font.render(f'{combo} COMBO!', True, (255, 255, 0))
        screen.blit(combo_text, 
                   (WIDTH//2 - combo_text.get_width()//2, 
                    HEIGHT//4))

    # Draw hit/miss feedback
    if current_feedback:
        feedback_font = pygame.font.Font(None, 48)
        if current_feedback == 'hit':
            text = random.choice(['PERFECT!', 'GREAT!', 'GOOD!', 'NICE!'])
            color = (100, 255, 100)  # Green
        elif current_feedback == 'near_miss':
            text = 'CLOSE!'
            color = (255, 255, 0)  # Yellow
        else:
            text = 'MISS!'
            color = (255, 100, 100)  # Red
            
        feedback = feedback_font.render(text, True, color)
        screen.blit(feedback, 
                   (WIDTH//2 - feedback.get_width()//2, 
                    JUDGMENT_LINE - 80))

def save_high_scores():
    with open('highscores.json', 'w') as f:
        json.dump(high_scores, f)

def add_high_score(name, score, difficulty):
    global high_scores
    high_scores.append({'name': name, 'score': int(score), 'difficulty': difficulty})
    high_scores.sort(key=lambda x: x['score'], reverse=True)
    high_scores = high_scores[:MAX_HIGH_SCORES]
    save_high_scores()

def draw_high_scores(surface, x, y):
    title = font.render("HIGH SCORES", True, (255, 255, 0))
    surface.blit(title, (x, y))
    
    for i, entry in enumerate(high_scores[:5]):
        score_text = f"{i+1}. {entry['name']}: {entry['score']} ({entry['difficulty']})"
        text = font.render(score_text, True, WHITE)
        surface.blit(text, (x, y + 40 + i * 30))

def show_start_menu():
    global current_difficulty
    
    # Load menu background
    try:
        menu_bg = pygame.image.load('menu_background.jpg')
        # Scale background to fit screen while maintaining aspect ratio
        bg_ratio = menu_bg.get_width() / menu_bg.get_height()
        new_width = int(HEIGHT * bg_ratio)
        menu_bg = pygame.transform.scale(menu_bg, (new_width, HEIGHT))
    except Exception as e:
        print(f"Error loading menu background: {e}")
        menu_bg = None
    
    title_font = pygame.font.Font(None, 100)
    instruction_font = pygame.font.Font(None, 36)
    
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Semi-transparent black
    
    # Create title with outline
    def draw_text_outline(text, font, x, y, color, outline_color, outline_size=2):
        # Render outline
        for dx in [-outline_size, 0, outline_size]:
            for dy in [-outline_size, 0, outline_size]:
                if dx != 0 or dy != 0:
                    text_surface = font.render(text, True, outline_color)
                    screen.blit(text_surface, (x + dx - text_surface.get_width()//2, y + dy))
        # Render main text
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x - text_surface.get_width()//2, y))
    
    # Difficulty options
    difficulty_options = list(DIFFICULTIES.keys())
    current_difficulty_index = difficulty_options.index(current_difficulty)
    
    instructions = [
        "A S D F - Hit notes in the corresponding lanes",
        "1 - Beginner (Slow)",
        "2 - Easy",
        "3 - Normal (Default)",
        "4 - Hard",
        "5 - Expert (Very Fast)",
        "M - Toggle sound",
        "Q - Pause/Resume",
        "L - View Leaderboard",
        "ESC - Return to menu",
        "",
        f"Current: {current_difficulty.upper()}",
        "Press any key to start!"
    ]
    
    # Create a pulsing effect for the title
    title_scale = 1.0
    scale_dir = 0.002
    
    waiting = True
    while waiting:
        # Draw background
        if menu_bg:
            # Center the background image
            bg_x = (WIDTH - menu_bg.get_width()) // 2
            screen.blit(menu_bg, (bg_x, 0))
        else:
            screen.fill(BLACK)
        
        # Draw overlay
        screen.blit(overlay, (0, 0))
        
        # Draw title with pulsing effect
        title_scale += scale_dir
        if title_scale > 1.05:
            title_scale = 1.05
            scale_dir = -scale_dir
        elif title_scale < 0.95:
            title_scale = 0.95
            scale_dir = -scale_dir
            
        title_surface = title_font.render("PYTHON RHYTHM", True, (255, 200, 0))
        scaled_title = pygame.transform.scale(
            title_surface,
            (int(title_surface.get_width() * title_scale),
             int(title_surface.get_height() * title_scale))
        )
        screen.blit(scaled_title, 
                   (WIDTH//2 - scaled_title.get_width()//2, 
                    HEIGHT//6 - scaled_title.get_height()//2))
        
        # Draw instructions with fade-in effect
        for i, line in enumerate(instructions):
            if i == len(instructions) - 1:  # Last line (press any key)
                alpha = int((pygame.time.get_ticks() % 2000) / 2000 * 255)
                if alpha > 255: alpha = 255
                text_surface = instruction_font.render(line, True, (255, 255, 255))
                text_surface.set_alpha(alpha)
            else:
                text_surface = instruction_font.render(line, True, WHITE)
            
            screen.blit(text_surface, 
                       (WIDTH//2 - text_surface.get_width()//2, 
                        HEIGHT//2 + i * 40))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                waiting = False
        
        clock.tick(FPS)

def reset_game():
    global score, combo, notes, spawn_timer, current_feedback, feedback_timer, NOTE_SPEED
    # Start or restart music
    try:
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except:
        print("Could not play background music")
    score = 0
    combo = 0
    notes = []
    active_notes.clear()
    spawn_timer = 0
    current_feedback = None
    feedback_timer = 0
    NOTE_SPEED = DIFFICULTIES[current_difficulty]['speed']
    global beat_interval, last_beat_time
    bpm = DIFFICULTIES[current_difficulty]['bpm']
    beat_interval = (60.0 / bpm) * 1000  # Convert BPM to milliseconds
    last_beat_time = pygame.time.get_ticks()

def show_game_over():
    global score, current_difficulty
    
    # Play level complete sound
    sound_manager.play_level_complete()
    
    input_active = True
    player_name = ''
    
    # Check if score is a high score
    is_high_score = len(high_scores) < MAX_HIGH_SCORES or score > high_scores[-1]['score']
    
    while True:
        screen.fill(BLACK)
        
        # Draw game over text
        game_over = font.render("GAME OVER", True, (255, 0, 0))
        score_text = font.render(f"Score: {int(score)}", True, WHITE)
        
        screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        if is_high_score:
            high_score_text = font.render("NEW HIGH SCORE!", True, (255, 215, 0))
            name_prompt = font.render("Enter your name:", True, WHITE)
            name_surface = font.render(player_name, True, WHITE)
            
            screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))
            screen.blit(name_prompt, (WIDTH//2 - name_prompt.get_width()//2, HEIGHT//2 + 100))
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 150, HEIGHT//2 + 140, 300, 40), 2)
            screen.blit(name_surface, (WIDTH//2 - 140, HEIGHT//2 + 145))
        
        draw_high_scores(screen, WIDTH - 250, 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if is_high_score and input_active:
                    if event.key == pygame.K_RETURN and player_name:
                        add_high_score(player_name, score, current_difficulty)
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < 10 and event.unicode.isalnum():
                        player_name += event.upper()
                else:
                    if event.key == pygame.K_ESCAPE:
                        return
                    else:
                        return
        
        pygame.display.flip()
        clock.tick(FPS)

def show_leaderboard():
    """Display the online leaderboard"""
    # Get top 10 scores for current difficulty
    scores = leaderboard.get_high_scores(difficulty=current_difficulty, limit=10)
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Draw leaderboard title
    title_font = pygame.font.Font(None, 48)
    title = title_font.render(f"LEADERBOARD - {current_difficulty.upper()}", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    # Draw column headers
    header_font = pygame.font.Font(None, 36)
    headers = ["RANK", "PLAYER", "SCORE", "DATE"]
    x_positions = [WIDTH//4 - 100, WIDTH//4, WIDTH//2, 3*WIDTH//4 + 50]
    
    for i, header in enumerate(headers):
        text = header_font.render(header, True, (200, 200, 200))
        screen.blit(text, (x_positions[i], 180))
    
    # Draw scores
    score_font = pygame.font.Font(None, 32)
    if not scores:
        no_scores = score_font.render("No scores yet - be the first!", True, WHITE)
        screen.blit(no_scores, (WIDTH//2 - no_scores.get_width()//2, 250))
    else:
        for i, entry in enumerate(scores):
            # Rank
            rank = f"{i+1}."
            rank_text = score_font.render(rank, True, WHITE)
            screen.blit(rank_text, (x_positions[0], 230 + i * 40))
            
            # Player name (truncate if too long)
            player = entry.get('player', 'Anonymous')[:12]
            player_text = score_font.render(player, True, WHITE)
            screen.blit(player_text, (x_positions[1], 230 + i * 40))
            
            # Score
            score_text = score_font.render(str(entry.get('score', 0)), True, WHITE)
            screen.blit(score_text, (x_positions[2], 230 + i * 40))
            
            # Date (format: MM-DD)
            date = entry.get('timestamp', '')
            if date and isinstance(date, str) and '-' in date:
                date_parts = date.split(' ')[0].split('-')
                if len(date_parts) >= 3:
                    date = f"{date_parts[1]}-{date_parts[2]}"  # MM-DD
            date_text = score_font.render(str(date), True, (180, 180, 180))
            screen.blit(date_text, (x_positions[3], 230 + i * 40))
    
    # Instructions
    back_text = score_font.render("Press ESC to return to menu", True, (150, 150, 150))
    screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    # Wait for ESC key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
        clock.tick(FPS)

def get_player_name():
    """Show a dialog to get player name for high score"""
    name = ""
    input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 20, 300, 40)
    active = True
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12:  # Limit name length
                    name += event.unicode
        
        # Draw
        screen.fill(BLACK)
        
        # Draw background
        if background_image:
            screen.blit(background_image, ((WIDTH - background_image.get_width()) // 2, 0))
        
        # Add overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw input box
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        prompt = font.render("New High Score! Enter your name:", True, WHITE)
        name_surface = font.render(name, True, WHITE)
        
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 60))
        screen.blit(name_surface, (input_rect.x + 10, input_rect.y + 10))
        
        # Draw instructions
        font_small = pygame.font.Font(None, 24)
        instructions = font_small.render("Press ENTER to submit, ESC to cancel", True, (180, 180, 180))
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT//2 + 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return name.strip() or "Player"

def draw_progress_bar(progress):
    """Draw the song progress bar at the top of the screen"""
    # Background bar
    pygame.draw.rect(screen, PROGRESS_BAR_BG_COLOR, 
                    (0, 0, WIDTH, PROGRESS_BAR_HEIGHT))
    
    # Progress indicator
    progress_width = int(WIDTH * progress)
    pygame.draw.rect(screen, PROGRESS_BAR_COLOR,
                    (0, 0, progress_width, PROGRESS_BAR_HEIGHT))
    
    # Add a subtle highlight at the top of the progress bar
    highlight = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
    highlight.fill((255, 255, 255, 50))
    screen.blit(highlight, (0, 0))

def draw_ui():
    # Draw progress bar (full width at the very top)
    if pygame.mixer.music.get_busy():
        # Calculate progress (0.0 to 1.0)
        current_pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
        song_length = 180  # Default song length in seconds (adjust based on your music)
        progress = min(1.0, max(0.0, current_pos / song_length))
        draw_progress_bar(progress)
    
    # Draw score and combo (positioned below the progress bar)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (20, PROGRESS_BAR_HEIGHT + 20))
    
    # Draw combo counter if combo > 0
    if combo > 0:
        combo_text = font.render(f"Combo: {combo}", True, WHITE)
        screen.blit(combo_text, (20, PROGRESS_BAR_HEIGHT + 60))

def main():
    global spawn_timer, score, combo, current_feedback, feedback_timer, current_difficulty, NOTE_SPEED, spawn_interval, paused
    running = True
    paused = False
    last_beat_time = pygame.time.get_ticks()
    
    # Initialize video
    init_video()
    
    # Initialize spawn_interval based on current difficulty
    min_interval, max_interval = DIFFICULTIES[current_difficulty]['interval']
    spawn_interval = random.randint(min_interval, max_interval)
    
    # Play menu music
    sound_manager.play('menu', loops=-1)
    
    # Show start menu
    show_start_menu()
    reset_game()
    
    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sound_manager.play('menu')
                    # Check if this is a high score
                    if leaderboard.initialized and leaderboard.is_high_score(score, current_difficulty):
                        player_name = get_player_name()
                        if player_name is not None:  # User didn't cancel
                            leaderboard.submit_score(player_name, int(score), current_difficulty)
                    show_start_menu()
                    reset_game()
                    continue
                elif event.key == pygame.K_l:  # Show leaderboard
                    show_leaderboard()
                    # Redraw the game screen
                    screen.fill(BLACK)
                    draw_video()
                    draw_lanes()
                    draw_judgment_line()
                    for note in notes:
                        note.draw(screen)
                    draw_score()
                    pygame.display.flip()
                    continue
                elif event.key == pygame.K_q:  # Pause/Resume with 'q'
                    global paused
                    paused = not paused
                    if video_player:
                        video_player.set_pause(paused)
                    current_feedback = 'PAUSED' if paused else 'RESUMED'
                    feedback_timer = feedback_duration
                    pygame.time.delay(200)  # Small delay to prevent multiple toggles
                    
                elif event.key == pygame.K_m:
                    muted = sound_manager.toggle_mute()
                    current_feedback = 'MUTED' if muted else 'UNMUTED'
                    feedback_timer = feedback_duration
                elif event.key == pygame.K_1 and current_difficulty != 'beginner':
                    current_difficulty = 'beginner'
                    current_feedback = 'BEGINNER MODE'
                    feedback_timer = feedback_duration
                    reset_game()
                elif event.key == pygame.K_2 and current_difficulty != 'easy':
                    current_difficulty = 'easy'
                    current_feedback = 'EASY MODE'
                    feedback_timer = feedback_duration
                    reset_game()
                elif event.key == pygame.K_3 and current_difficulty != 'normal':
                    current_difficulty = 'normal'
                    current_feedback = 'NORMAL MODE'
                    feedback_timer = feedback_duration
                    reset_game()
                elif event.key == pygame.K_4 and current_difficulty != 'hard':
                    current_difficulty = 'hard'
                    current_feedback = 'HARD MODE'
                    feedback_timer = feedback_duration
                    reset_game()
                elif event.key == pygame.K_5 and current_difficulty != 'expert':
                    current_difficulty = 'expert'
                    current_feedback = 'EXPERT MODE'
                    feedback_timer = feedback_duration
                    reset_game()
                # Update key states
                if event.key in key_states:
                    key_states[event.key] = True
                    key_index = key_bindings.index(event.key)
                    hit = False
                    
                    # Find the closest note to hit
                    closest_note = None
                    min_distance = float('inf')
                    
                    for note in notes:
                        if (note.lane == key_index and not note.hit and not note.missed and 
                            note not in active_notes):
                            distance = abs(note.y + note.height/2 - JUDGMENT_LINE)
                            if distance < min_distance and distance < BEAT_MARGIN:
                                min_distance = distance
                                closest_note = note
                    
                    # Only process hit if we haven't already processed this note
                    if closest_note and not hasattr(closest_note, 'hit_processed'):
                        result = closest_note.check_hit(True)
                        closest_note.hit_processed = True
                        
                        if result == 'hit':
                            score += 100 * (1 + combo * 0.1)
                            combo += 1
                            hit = True
                            current_feedback = 'hit'
                            feedback_timer = feedback_duration
                            sound_manager.play('hit')
                            if combo % 10 == 0 and combo > 0:
                                sound_manager.play('combo')
                                if combo >= 10:  # Play special sound for 10+ combos
                                    sound_manager.play_combo_special()
                        elif result == 'near_miss':
                            combo = max(0, combo - 1)  # Small penalty for near miss
                            current_feedback = 'close!'
                            feedback_timer = feedback_duration / 2
                            sound_manager.play('miss')
                    
                    # Only count as a miss if no note was close
                    if not hit and not any(note.lane == key_index and not note.hit and not note.missed 
                                        for note in notes):
                        combo = 0
                        current_feedback = 'miss'
                        feedback_timer = feedback_duration
                        sound_manager.play('miss')
            
            elif event.type == pygame.KEYUP:
                if event.key in key_states:
                    key_states[event.key] = False
        
        # Only update game logic if not paused
        if not paused:
            # Handle beat detection and note spawning
            current_time = pygame.time.get_ticks()
            if current_time - last_beat_time >= beat_interval:
                last_beat_time = current_time
                # Spawn notes on beat
                if random.random() > 0.3:  # 70% chance to spawn a note on each beat
                    spawn_note()
            
            # Update notes
            for note in notes[:]:
                note.update()
                if note.missed:
                    notes.remove(note)
                    if combo > 0:  # Only play miss sound if we had a combo
                        sound_manager.play('miss')
                    combo = 0
                elif note.hit:
                    notes.remove(note)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw video background
        draw_video()
        
        # Draw UI elements (progress bar first, behind notes)
        draw_ui()
        
        # Draw game elements on top
        draw_lanes()
        draw_judgment_line()
        
        # Draw notes on top of everything
        for note in notes:
            note.draw(screen)
        
        # Apply hit/miss tint
        if current_feedback and feedback_timer > 0:
            if current_feedback == 'hit':
                tint = HIT_COLOR
            else:
                tint = MISS_COLOR
            
            # Create a semi-transparent overlay
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((*tint, 30))  # 30 is alpha/opacity
            screen.blit(s, (0, 0))
            
            feedback_timer -= 1
            if feedback_timer <= 0:
                current_feedback = None
        
        draw_score()
        
        # Update the display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
