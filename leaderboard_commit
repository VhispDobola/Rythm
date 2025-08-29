import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from typing import List, Dict, Optional

class Leaderboard:
    def __init__(self, config_file: str = 'firebase_config.json'):
        """
        Initialize the leaderboard with Firebase credentials.
        
        Args:
            config_file: Path to Firebase service account JSON file
        """
        self.scores = []
        self.initialized = False
        
        # Initialize Firebase if config exists
        if os.path.exists(config_file):
            try:
                cred = credentials.Certificate(config_file)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                print("Leaderboard: Connected to Firebase")
            except Exception as e:
                print(f"Leaderboard: Failed to initialize - {e}")
        else:
            print(f"Leaderboard: Firebase config file '{config_file}' not found")
    
    def submit_score(self, player_name: str, score: int, difficulty: str, song: str = "default") -> bool:
        """
        Submit a score to the leaderboard.
        
        Args:
            player_name: Name of the player
            score: Score achieved
            difficulty: Game difficulty
            song: Song name (default: "default")
            
        Returns:
            bool: True if submission was successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('scores').document()
            doc_ref.set({
                'player': player_name,
                'score': score,
                'difficulty': difficulty,
                'song': song,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            print(f"Failed to submit score: {e}")
            return False
    
    def get_high_scores(self, difficulty: str = None, song: str = "default", limit: int = 10) -> List[Dict]:
        """
        Get top scores from the leaderboard.
        
        Args:
            difficulty: Filter by difficulty (optional)
            song: Filter by song name (default: "default")
            limit: Maximum number of scores to return (default: 10)
            
        Returns:
            List of score entries, each containing player, score, and timestamp
        """
        if not self.initialized:
            return []
            
        try:
            query = self.db.collection('scores')
            
            # Apply filters
            if difficulty:
                query = query.where('difficulty', '==', difficulty)
            if song:
                query = query.where('song', '==', song)
                
            # Get top scores
            results = query.order_by('score', direction='DESCENDING').limit(limit).stream()
            
            # Convert to list of dicts
            scores = []
            for doc in results:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convert Firestore timestamp to string if it exists
                if 'timestamp' in data and hasattr(data['timestamp'], 'strftime'):
                    data['timestamp'] = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                scores.append(data)
                
            return scores
            
        except Exception as e:
            print(f"Failed to fetch scores: {e}")
            return []
    
    def is_high_score(self, score: int, difficulty: str, song: str = "default") -> bool:
        """
        Check if a score would make it to the top 10 for the given difficulty and song.
        
        Args:
            score: Score to check
            difficulty: Game difficulty
            song: Song name (default: "default")
            
        Returns:
            bool: True if the score would be in the top 10, False otherwise
        """
        if not self.initialized:
            return False
            
        # Get current top 10 scores
        current_scores = self.get_high_scores(difficulty, song, limit=10)
        
        # If we have less than 10 scores, it's automatically a high score
        if len(current_scores) < 10:
            return True
            
        # Check if the new score is higher than the lowest score in the top 10
        return score > current_scores[-1]['score']

# Global leaderboard instance
leaderboard = Leaderboard()

# Example usage
if __name__ == "__main__":
    # Test the leaderboard
    lb = Leaderboard()
    if lb.initialized:
        # Submit a test score
        lb.submit_score("TestPlayer", 1000, "normal")
        
        # Get top scores
        print("Top scores:")
        for score in lb.get_high_scores():
            print(f"{score['player']}: {score['score']}")
