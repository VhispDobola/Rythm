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
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1200, 800

# Song library
SONG_LIBRARY = [
    {
        'id': 'default',
        'title': 'Default Beat',
        'file': 'sounds/default_beat.mp3',
        'bpm': 120,
        'difficulty_modes': {
            'beginner': {'speed': 4, 'interval': (1000, 1300)},
            'easy': {'speed': 5, 'interval': (800, 1100)},
            'normal': {'speed': 6.5, 'interval': (600, 900)},
            'hard': {'speed': 8, 'interval': (400, 700)},
            'expert': {'speed': 10, 'interval': (200, 500)}
        }
    },
    {
        'id': 'dont_talk',
        'title': 'Don\'t Talk',
        'file': 'assets/music/dont_talk.mp3',
        'bpm': 140,  # Default BPM, adjust if needed
        'difficulty_modes': {
            'beginner': {'speed': 4.5, 'interval': (900, 1200)},
            'easy': {'speed': 5.5, 'interval': (700, 1000)},
            'normal': {'speed': 7, 'interval': (500, 800)},
            'hard': {'speed': 8.5, 'interval': (300, 600)},
            'expert': {'speed': 10.5, 'interval': (150, 400)}
        }
    },
    {
        'id': 'titanium',
        'title': 'Titanium',
        'file': 'sounds/titanium-170190.mp3',
        'bpm': 126,
        'difficulty_modes': {
            'beginner': {'speed': 4.2, 'interval': (950, 1250)},
            'easy': {'speed': 5.3, 'interval': (750, 1050)},
            'normal': {'speed': 6.8, 'interval': (550, 850)},
            'hard': {'speed': 8.3, 'interval': (350, 650)},
            'expert': {'speed': 10.2, 'interval': (180, 450)}
        }
    },
    {
        'id': 'lost_in_dreams',
        'title': 'Lost in Dreams',
        'file': 'sounds/lost-in-dreams-abstract-chill-downtempo-cinematic-future-beats-270241.mp3',
        'bpm': 90,
        'difficulty_modes': {
            'beginner': {'speed': 3.5, 'interval': (1100, 1400)},
            'easy': {'speed': 4.5, 'interval': (900, 1200)},
            'normal': {'speed': 5.5, 'interval': (700, 1000)},
            'hard': {'speed': 7.0, 'interval': (500, 800)},
            'expert': {'speed': 8.5, 'interval': (250, 550)}
        }
    },
    {
        'id': 'spinning_head',
        'title': 'Spinning Head',
        'file': 'sounds/spinning-head-271171.mp3',
        'bpm': 128,
        'difficulty_modes': {
            'beginner': {'speed': 4.3, 'interval': (930, 1230)},
            'easy': {'speed': 5.4, 'interval': (730, 1030)},
            'normal': {'speed': 7.0, 'interval': (530, 830)},
            'hard': {'speed': 8.6, 'interval': (330, 630)},
            'expert': {'speed': 10.5, 'interval': (170, 430)}
        }
    },
    {
        'id': 'future_design',
        'title': 'Future Design',
        'file': 'sounds/future-design-344320.mp3',
        'bpm': 122,
        'difficulty_modes': {
            'beginner': {'speed': 4.1, 'interval': (970, 1270)},
            'easy': {'speed': 5.2, 'interval': (770, 1070)},
            'normal': {'speed': 6.7, 'interval': (570, 870)},
            'hard': {'speed': 8.2, 'interval': (370, 670)},
            'expert': {'speed': 10.0, 'interval': (190, 470)}
        }
    },
    {
        'id': 'kugelsicher',
        'title': 'Kugelsicher',
        'file': 'sounds/kugelsicher-by-tremoxbeatz-302838.mp3',
        'bpm': 95,
        'difficulty_modes': {
            'beginner': {'speed': 3.8, 'interval': (1050, 1350)},
            'easy': {'speed': 4.8, 'interval': (850, 1150)},
            'normal': {'speed': 6.0, 'interval': (650, 950)},
            'hard': {'speed': 7.5, 'interval': (450, 750)},
            'expert': {'speed': 9.0, 'interval': (220, 500)}
        }
    }
]
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
misses = 0
MAX_MISSES = 10  # Increased miss limit to 10
notes = []
active_notes = set()  # Track which notes are currently being hit
spawn_timer = 0
spawn_interval = 60  # frames
key_bindings = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
key_states = {key: False for key in key_bindings}  # Track key states
high_scores = []
MAX_HIGH_SCORES = 5
current_song = SONG_LIBRARY[0]  # Default to first song in the library
DIFFICULTIES = {
    'beginner': {'speed': 4, 'interval': (1000, 1300), 'bpm': 100},
    'easy': {'speed': 5, 'interval': (800, 1100), 'bpm': 120},
    'normal': {'speed': 6.5, 'interval': (600, 900), 'bpm': 140},
    'hard': {'speed': 7.5, 'interval': (400, 700), 'bpm': 160},
    'expert': {'speed': 9, 'interval': (200, 500), 'bpm': 180}
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
        pygame.mixer.music.load('assets/music/background_music.mp3')
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
    global video_player, video_size, video_pos, background_image, last_valid_frame
    video_player = None
    last_valid_frame = None
    
    # Try to load static background first as fallback
    try:
        background_image = pygame.image.load('menu_background.jpg').convert()
        img_ratio = background_image.get_width() / background_image.get_height()
        target_width = int(HEIGHT * img_ratio)
        background_image = pygame.transform.scale(background_image, (target_width, HEIGHT))
        last_valid_frame = background_image
        print("Loaded static background image")
    except Exception as e:
        print(f"Failed to load background image: {e}")
        background_image = None
    
    # Try to load video
    try:
        if not os.path.exists(VIDEO_FILE):
            print(f"Video file not found: {VIDEO_FILE}")
            return
            
        print(f"Initializing video: {VIDEO_FILE}")
        video_player = MediaPlayer(
            VIDEO_FILE, 
            loop=True, 
            ff_opts={
                'paused': False, 
                'sync': 'video',
                'an': True,  # Disable audio
                'sn': 'v',   # Force video stream
                'hwaccel': 'auto'  # Try hardware acceleration
            }
        )
        
        # Wait a bit for initialization
        pygame.time.delay(200)
        
        # Try to get video metadata
        video_info = video_player.get_metadata()
        print(f"Video metadata: {video_info}")
        
        if video_info and 'src_vid_size' in video_info:
            video_width, video_height = video_info['src_vid_size']
            print(f"Video dimensions: {video_width}x{video_height}")
            
            if video_width > 0 and video_height > 0:
                # Calculate aspect ratio and scale
                video_ratio = video_width / video_height
                target_width = int(HEIGHT * video_ratio)
                video_size = (min(target_width, WIDTH), HEIGHT)
                video_pos = ((WIDTH - video_size[0]) // 2, 0)
                print(f"Video will be displayed at {video_size} position {video_pos}")
                
                # Try to get a few frames to ensure video is playing
                for _ in range(10):  # Try up to 10 times
                    frame, val = video_player.get_frame()
                    if frame and frame != 'eof':
                        img, pts = frame
                        if img is not None:
                            print("Successfully got first video frame")
                            return
                    pygame.time.delay(50)  # Small delay between attempts
                
                print("Warning: Could not get valid video frames after multiple attempts")
                
    except Exception as e:
        print(f"Video initialization error: {str(e)}")
        video_player = None

# Store the last valid frame to prevent flickering
last_valid_frame = None

last_frame_time = 0
frame_count = 0

def update_video():
    global video_player, last_valid_frame, last_frame_time, frame_count
    
    # If we don't have a video player, return the last valid frame (or None)
    if not video_player:
        return last_valid_frame
    
    try:
        # Try to get a frame with a small timeout
        frame, val = video_player.get_frame()
        
        # Debug info (print once per second)
        frame_count += 1
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > 1000:  # Every second
            print(f"Video frame: {frame_count}, Status: {val}, Frame type: {type(frame).__name__ if frame else 'None'}")
            last_frame_time = current_time
        
        # Handle end of video
        if val == 'eof' or frame == 'eof':
            print("End of video, seeking to start...")
            video_player.seek(0, relative=False)
            video_player.set_pause(False)
            return last_valid_frame  # Return last frame while seeking
        
        # Process the frame if we have one
        if frame and frame != 'eof':
            try:
                img, pts = frame
                if img is not None:
                    # Convert frame to Pygame surface
                    img_data = img.to_bytearray()[0]
                    video_surface = pygame.image.frombuffer(
                        img_data, 
                        img.get_size(), 
                        'RGB'
                    ).convert()
                    
                    # Scale the video to fit while maintaining aspect ratio
                    video_surface = pygame.transform.scale(video_surface, video_size)
                    last_valid_frame = video_surface
                    return video_surface
                    
            except Exception as e:
                print(f"Error processing video frame: {str(e)}")
                # Fall through to return last_valid_frame below
        
        # If we get here, we didn't get a valid frame
        if frame_count % 60 == 0:  # Only print this occasionally to avoid spam
            print(f"No valid frame received (attempt {frame_count})")
            
    except Exception as e:
        print(f"Error in update_video: {str(e)}")
        # Try to recover by reinitializing the video player
        if frame_count % 120 == 0:  # Only try to reinitialize occasionally
            print("Attempting to reinitialize video...")
            init_video()
    
    return last_valid_frame  # Return the last valid frame if we couldn't get a new one

def draw_video():
    # Draw video frame if available
    if video_player and last_valid_frame:
        screen.blit(last_valid_frame, video_pos)
    
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
        # Check if note passed the judgment line without being hit
        if self.y > JUDGMENT_LINE + 50 and not self.hit and not self.missed:
            self.missed = True
            return 'auto_miss'  # Return that this was an automatic miss
        return None
    
    def draw(self, surface):
        if not self.hit and not self.missed:
            pygame.draw.rect(surface, COLORS[self.lane], 
                           (self.x, self.y, self.width, self.height))

    def check_hit(self, key_pressed):
        if not self.hit and not self.missed and key_pressed:
            distance = abs((self.y + self.height/2) - JUDGMENT_LINE)
            if distance < 10:  # Perfect hit window (10 pixels)
                self.hit = True
                return 'perfect'
            elif distance < 25:  # Good hit window (25 pixels)
                self.hit = True
                return 'good'
            elif distance < 40:  # Okay hit window (40 pixels)
                self.hit = True
                return 'okay'
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
    misses_text = font.render(f'Misses: {misses}/{MAX_MISSES}', True, (255, 100, 100) if misses >= 2 else WHITE)
    screen.blit(score_text, (20, PROGRESS_BAR_HEIGHT + 20))
    screen.blit(combo_text, (20, PROGRESS_BAR_HEIGHT + 60))
    screen.blit(misses_text, (20, PROGRESS_BAR_HEIGHT + 100))
    
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
        if current_feedback == 'perfect':
            text = 'PERFECT!'
            color = (255, 215, 0)  # Gold
        elif current_feedback == 'good':
            text = 'GOOD!'
            color = (100, 255, 100)  # Green
        elif current_feedback == 'okay':
            text = 'OKAY!'
            color = (100, 200, 255)  # Light blue
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

def show_song_selection():
    global current_difficulty, current_song
    
    selected_song = 0
    selected_difficulty = list(current_song['difficulty_modes'].keys()).index(current_difficulty)
    difficulties = list(current_song['difficulty_modes'].keys())
    
    title_font = pygame.font.Font(None, 80)
    song_font = pygame.font.Font(None, 48)
    diff_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_song = (selected_song - 1) % len(SONG_LIBRARY)
                    sound_manager.play('menu')
                    # Update available difficulties for selected song
                    difficulties = list(SONG_LIBRARY[selected_song]['difficulty_modes'].keys())
                    selected_difficulty = min(selected_difficulty, len(difficulties) - 1)
                elif event.key == pygame.K_DOWN:
                    selected_song = (selected_song + 1) % len(SONG_LIBRARY)
                    sound_manager.play('menu')
                    # Update available difficulties for selected song
                    difficulties = list(SONG_LIBRARY[selected_song]['difficulty_modes'].keys())
                    selected_difficulty = min(selected_difficulty, len(difficulties) - 1)
                elif event.key == pygame.K_LEFT:
                    selected_difficulty = (selected_difficulty - 1) % len(difficulties)
                    sound_manager.play('menu')
                elif event.key == pygame.K_RIGHT:
                    selected_difficulty = (selected_difficulty + 1) % len(difficulties)
                    sound_manager.play('menu')
                elif event.key == pygame.K_RETURN:
                    sound_manager.play('select')
                    current_song = SONG_LIBRARY[selected_song]
                    current_difficulty = difficulties[selected_difficulty]
                    return True  # Start game
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play('select')
                    return False  # Back to menu
        
        # Draw
        screen.fill((0, 0, 0))
        
        # Draw title
        title = title_font.render("SELECT SONG", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Draw song list
        for i, song in enumerate(SONG_LIBRARY):
            y_pos = 180 + i * 60
            color = (255, 255, 0) if i == selected_song else (200, 200, 200)
            text = song_font.render(song['title'], True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
            
            # Draw BPM info
            bpm_text = small_font.render(f"{song['bpm']} BPM", True, (150, 150, 150))
            screen.blit(bpm_text, (WIDTH//2 + 200, y_pos + 10))
        
        # Draw difficulty selector
        diff_y = HEIGHT - 150
        diff_title = diff_font.render("DIFFICULTY:", True, (200, 200, 200))
        screen.blit(diff_title, (WIDTH//2 - 200, diff_y))
        
        for i, diff in enumerate(difficulties):
            x_pos = WIDTH//2 - 100 + i * 120
            color = (255, 255, 0) if i == selected_difficulty else (150, 150, 150)
            text = diff_font.render(diff.upper(), True, color)
            screen.blit(text, (x_pos, diff_y + 50))
        
        # Draw controls
        controls = [
            "↑/↓: Select Song",
            "←/→: Change Difficulty",
            "ENTER: Start Game",
            "ESC: Back to Menu"
        ]
        
        for i, control in enumerate(controls):
            text = small_font.render(control, True, (150, 150, 150))
            screen.blit(text, (50, HEIGHT - 80 + i * 30))
        
        pygame.display.flip()
        clock.tick(FPS)

def show_start_menu():
    global current_difficulty, current_song
    
    # Load menu background
    try:
        menu_bg = pygame.image.load('start_screen.jpg')
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
    
    # Create difficulty display with current selection highlighted
    difficulty_display = [
        "1 - BEGINNER (Slow)",
        "2 - EASY",
        "3 - NORMAL (Default)",
        "4 - HARD",
        "5 - EXPERT (Fast)"
    ]
    
    # Highlight current difficulty
    diff_index = list(DIFFICULTIES.keys()).index(current_difficulty)
    difficulty_display[diff_index] = f"→ {difficulty_display[diff_index]} (SELECTED)"
    
    instructions = [
        "A S D F - Hit notes in the corresponding lanes",
        "",
        "SELECT DIFFICULTY (1-5):",
        *difficulty_display,
        "",
        "M - Toggle sound",
        "Q - Pause/Resume",
        "L - View Leaderboard",
        "",
        f"Current: {current_difficulty.upper()}",
        "",
        "Press ENTER to select song and start!"
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
        
        # Draw current song and difficulty
        song_text = instruction_font.render(
            f"Current: {current_song['title']} ({current_difficulty.upper()})", 
            True, 
            (200, 200, 255)
        )
        screen.blit(song_text, (WIDTH//2 - song_text.get_width()//2, HEIGHT//3 + 20))
        
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
                elif event.key == pygame.K_RETURN:
                    # Show song selection when ENTER is pressed
                    if show_song_selection():
                        waiting = False  # Start game if a song was selected
                        sound_manager.play('select')
                # Handle difficulty shortcuts (1-5)
                elif pygame.K_1 <= event.key <= pygame.K_5:  # 1-5 keys
                    diff_index = event.key - pygame.K_1  # 0-4
                    difficulty_list = list(DIFFICULTIES.keys())
                    if 0 <= diff_index < len(difficulty_list):
                        current_difficulty = difficulty_list[diff_index]
                        sound_manager.play('menu')
        
        clock.tick(FPS)

def reset_game():
    global notes, active_notes, score, combo, misses, spawn_timer, current_feedback, feedback_timer, last_beat_time, beat_interval, NOTE_SPEED, spawn_interval
    
    # Reset game state
    notes = []
    active_notes = set()
    score = 0
    combo = 0
    misses = 0
    current_feedback = None
    feedback_timer = 0
    spawn_timer = 0
    
    # Set game parameters based on song and difficulty
    difficulty_settings = current_song['difficulty_modes'][current_difficulty]
    min_interval, max_interval = difficulty_settings['interval']
    spawn_interval = random.randint(min_interval, max_interval)
    NOTE_SPEED = difficulty_settings['speed']
    
    # Calculate beat interval based on song BPM
    bpm = current_song['bpm']
    beat_interval = (60.0 / bpm) * 1000  # Convert BPM to milliseconds
    last_beat_time = pygame.time.get_ticks()
    
    # Load and play the selected song
    sound_manager.load_music(current_song['file'])
    sound_manager.play_music()

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
                        player_name += event.unicode.upper()
                else:
                    if event.key == pygame.K_ENTER:
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
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
    back_text = score_font.render("Press ENTER to return to menu", True, (150, 150, 150))
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
                if event.key == pygame.K_ENTER:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_q:  # Q key returns to main menu
                    show_start_menu()
                    reset_game()
                    continue
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
    global spawn_timer, score, combo, misses, current_feedback, feedback_timer, current_difficulty, NOTE_SPEED, spawn_interval
    running = True
    paused = False
    game_over = False
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
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_q:  # Q key returns to main menu
                    show_start_menu()
                    reset_game()
                    continue
                elif event.key == pygame.K_RETURN:
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
                        
                        if result in ['perfect', 'good', 'okay']:
                            # Different scoring based on accuracy
                            if result == 'perfect':
                                score += 150 * (1 + combo * 0.1)  # 150% points for perfect
                                current_feedback = 'perfect'
                            elif result == 'good':
                                score += 125 * (1 + combo * 0.1)  # 125% points for good
                                current_feedback = 'good'
                            elif result == 'okay':
                                score += 100 * (1 + combo * 0.1)  # 100% points for okay
                                current_feedback = 'okay'
                            
                            combo += 1
                            hit = True
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
                result = note.update()
                if note.missed:
                    notes.remove(note)
                    if result == 'auto_miss':  # Note passed the judgment line
                        misses += 1
                        combo = 0
                        current_feedback = 'miss'
                        feedback_timer = feedback_duration
                        sound_manager.play('miss')
                        
                        # Check for game over
                        if misses >= MAX_MISSES:
                            game_over = True
                elif note.hit:
                    notes.remove(note)
        
        # Check for game over
        if game_over:
            show_game_over()
            reset_game()
            game_over = False
            continue
        
        # Clear the screen with black (this will be overdrawn by the video)
        screen.fill(BLACK)
        
        # Always try to update the video frame
        if video_player:
            update_video()  # This will update last_valid_frame
        
        # Draw the background (video or static)
        if video_player and last_valid_frame:
            screen.blit(last_valid_frame, video_pos)
        elif background_image:
            screen.blit(background_image, ((WIDTH - background_image.get_width()) // 2, 0))
        
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
            if current_feedback in ['perfect', 'good', 'okay']:
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
