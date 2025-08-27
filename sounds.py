import os
import pygame

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.muted = False
        self.level_complete_sound = None
        self.combo_special_sound = None
        self.load_sounds()
        self.load_level_complete_sound()
        self.load_combo_special_sound()

    def load_level_complete_sound(self):
        """Load the level complete sound"""
        try:
            if os.path.exists('level_complete.mp3'):
                self.level_complete_sound = pygame.mixer.Sound('level_complete.mp3')
                self.level_complete_sound.set_volume(0.7)
        except Exception as e:
            print(f"Error loading level complete sound: {e}")
            
    def load_combo_special_sound(self):
        """Load the special combo sound"""
        try:
            if os.path.exists('combo_special.mp3'):
                self.combo_special_sound = pygame.mixer.Sound('combo_special.mp3')
                self.combo_special_sound.set_volume(0.7)
        except Exception as e:
            print(f"Error loading combo special sound: {e}")
            
    def load_sounds(self):
        """Load all game sounds"""
        sound_files = {
            'hit': 'hit.wav',
            'miss': 'miss.wav',
            'combo': 'combo.wav',
            'menu': 'menu.wav'
        }
        
        # Create silent sound as fallback
        silent = pygame.mixer.Sound(buffer=bytearray([0] * 1024))
        
        for name, filename in sound_files.items():
            try:
                if os.path.exists(filename):
                    sound = pygame.mixer.Sound(filename)
                    sound.set_volume(0.5)
                    self.sounds[name] = sound
                else:
                    print(f"Warning: Sound file not found: {filename}")
                    self.sounds[name] = silent
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                self.sounds[name] = silent
    
    def play(self, name, loops=0):
        """Play a sound effect"""
        if not self.muted and name in self.sounds:
            self.sounds[name].play(loops=loops)
    
    def play_level_complete(self):
        """Play the level complete sound"""
        if not self.muted and self.level_complete_sound:
            self.level_complete_sound.play()
            
    def play_combo_special(self):
        """Play the special combo sound"""
        if not self.muted and self.combo_special_sound:
            self.combo_special_sound.play()
            
    def toggle_mute(self):
        """Toggle sound on/off"""
        self.muted = not self.muted
        volume = 0.0 if self.muted else 0.5
        for sound in self.sounds.values():
            sound.set_volume(volume)
        if self.level_complete_sound:
            self.level_complete_sound.set_volume(volume)
        return self.muted
