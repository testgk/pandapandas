#!/usr/bin/env python3
"""
Interactive Map-based GeoChallenge Game
Click on the map to make your guess!
"""
import sys
import os
from pathlib import Path
import math
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches

# Add p3d directory to path so we can import the game modules
sys.path.append(str(Path(__file__).parent / "p3d"))

try:
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import Point
    print("✅ Successfully imported core dependencies")
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Please install required packages with: pip install pandas numpy shapely matplotlib tkinter")
    sys.exit(1)

# Simple WorldDataManager mock for the map-based version
class SimpleWorldDataManager:
    """Simple mock for WorldDataManager that doesn't require downloading data"""
    def __init__(self):
        pass

class InteractiveMapGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 GeoChallenge - Interactive Map Game")
        self.root.geometry("1200x800")
        
        # Import the game class
        from geo_challenge_game import GeoChallengeGame, DifficultyLevel
        
        # Initialize game
        world_manager = SimpleWorldDataManager()
        self.game = GeoChallengeGame(world_manager)
        self.DifficultyLevel = DifficultyLevel
        
        # Game state
        self.current_challenge = None
        self.game_count = 0
        self.max_games = 5
        self.extra_hints_used = 0
        self.guess_lat = None
        self.guess_lon = None
        
        self.setup_ui()
        self.setup_map()
        self.start_new_round()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for game info
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Game info
        self.info_frame = ttk.LabelFrame(left_panel, text="🎯 Current Challenge", padding=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.round_label = ttk.Label(self.info_frame, text="Round: 0/5", font=('Arial', 12, 'bold'))
        self.round_label.pack(anchor=tk.W)
        
        self.location_label = ttk.Label(self.info_frame, text="Location: ", font=('Arial', 11))
        self.location_label.pack(anchor=tk.W, pady=2)
        
        self.difficulty_label = ttk.Label(self.info_frame, text="Difficulty: ", font=('Arial', 11))
        self.difficulty_label.pack(anchor=tk.W, pady=2)
        
        self.country_label = ttk.Label(self.info_frame, text="Country: ", font=('Arial', 11))
        self.country_label.pack(anchor=tk.W, pady=2)
        
        self.continent_label = ttk.Label(self.info_frame, text="Continent: ", font=('Arial', 11))
        self.continent_label.pack(anchor=tk.W, pady=2)
        
        # Hints section
        self.hints_frame = ttk.LabelFrame(left_panel, text="💡 Hints", padding=10)
        self.hints_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.hints_text = tk.Text(self.hints_frame, wrap=tk.WORD, height=8, width=30)
        self.hints_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X)
        
        self.hint_button = ttk.Button(button_frame, text="Get Extra Hint", command=self.get_extra_hint)
        self.hint_button.pack(fill=tk.X, pady=2)
        
        self.submit_button = ttk.Button(button_frame, text="Submit Guess", command=self.submit_guess, state=tk.DISABLED)
        self.submit_button.pack(fill=tk.X, pady=2)
        
        self.next_button = ttk.Button(button_frame, text="Next Round", command=self.start_new_round, state=tk.DISABLED)
        self.next_button.pack(fill=tk.X, pady=2)
        
        # Coordinates display
        coord_frame = ttk.LabelFrame(left_panel, text="📍 Your Guess", padding=10)
        coord_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.coord_label = ttk.Label(coord_frame, text="Click on the map to make your guess!", font=('Arial', 10))
        self.coord_label.pack()
        
        # Right panel for map
        self.map_frame = ttk.LabelFrame(main_frame, text="🗺️ World Map - Click to Guess!", padding=5)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def setup_map(self):
        """Setup the interactive world map"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create world map
        self.draw_world_map()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind click event
        self.canvas.mpl_connect('button_press_event', self.on_map_click)
        
        # Initialize markers
        self.guess_marker = None
        self.actual_marker = None
    
    def draw_world_map(self):
        """Draw a simple world map"""
        self.ax.clear()
        
        # Set up the map bounds
        self.ax.set_xlim(-180, 180)
        self.ax.set_ylim(-90, 90)
        
        # Add grid
        self.ax.grid(True, alpha=0.3)
        
        # Add continent outlines (simplified)
        continents = [
            # North America
            patches.Polygon([(-160, 70), (-160, 15), (-60, 15), (-60, 70)], 
                          closed=True, fill=False, edgecolor='darkgreen', linewidth=2),
            # South America  
            patches.Polygon([(-85, 15), (-85, -55), (-35, -55), (-35, 15)], 
                          closed=True, fill=False, edgecolor='darkgreen', linewidth=2),
            # Europe
            patches.Polygon([(-10, 35), (-10, 70), (40, 70), (40, 35)], 
                          closed=True, fill=False, edgecolor='darkblue', linewidth=2),
            # Africa
            patches.Polygon([(-20, 35), (-20, -35), (50, -35), (50, 35)], 
                          closed=True, fill=False, edgecolor='darkorange', linewidth=2),
            # Asia
            patches.Polygon([(40, 70), (40, 10), (180, 10), (180, 70)], 
                          closed=True, fill=False, edgecolor='darkred', linewidth=2),
            # Australia
            patches.Polygon([(110, -10), (110, -45), (155, -45), (155, -10)], 
                          closed=True, fill=False, edgecolor='purple', linewidth=2),
        ]
        
        for continent in continents:
            self.ax.add_patch(continent)
        
        # Add labels
        self.ax.text(-110, 50, 'North America', fontsize=10, ha='center', color='darkgreen', weight='bold')
        self.ax.text(-60, -20, 'South America', fontsize=10, ha='center', color='darkgreen', weight='bold')
        self.ax.text(15, 52, 'Europe', fontsize=10, ha='center', color='darkblue', weight='bold')
        self.ax.text(15, 0, 'Africa', fontsize=10, ha='center', color='darkorange', weight='bold')
        self.ax.text(110, 40, 'Asia', fontsize=10, ha='center', color='darkred', weight='bold')
        self.ax.text(132, -27, 'Australia', fontsize=10, ha='center', color='purple', weight='bold')
        
        # Set labels
        self.ax.set_xlabel('Longitude (°)')
        self.ax.set_ylabel('Latitude (°)')
        self.ax.set_title('Click anywhere on the map to make your guess!')
        
        # Add equator and prime meridian
        self.ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        self.ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    def on_map_click(self, event):
        """Handle map click events"""
        if event.inaxes != self.ax:
            return
        
        # Get coordinates from click
        self.guess_lon = event.xdata
        self.guess_lat = event.ydata
        
        # Validate coordinates
        if self.guess_lat is None or self.guess_lon is None:
            return
        
        # Clamp to valid ranges
        self.guess_lat = max(-90, min(90, self.guess_lat))
        self.guess_lon = max(-180, min(180, self.guess_lon))
        
        # Remove previous guess marker
        if self.guess_marker:
            self.guess_marker.remove()
        
        # Add new guess marker
        self.guess_marker = self.ax.plot(self.guess_lon, self.guess_lat, 'ro', 
                                       markersize=10, label='Your Guess')[0]
        
        # Update coordinate display
        self.coord_label.config(text=f"Your Guess: ({self.guess_lat:.2f}°, {self.guess_lon:.2f}°)")
        
        # Enable submit button
        self.submit_button.config(state=tk.NORMAL)
        
        # Refresh canvas
        self.canvas.draw()
    
    def start_new_round(self):
        """Start a new round"""
        if self.game_count >= self.max_games:
            self.show_final_results()
            return
        
        self.game_count += 1
        self.extra_hints_used = 0
        self.guess_lat = None
        self.guess_lon = None
        
        # Clear markers
        if self.guess_marker:
            self.guess_marker.remove()
            self.guess_marker = None
        if self.actual_marker:
            self.actual_marker.remove()
            self.actual_marker = None
        
        # Get new challenge
        difficulty = self.DifficultyLevel.EASY if self.game_count <= 2 else self.DifficultyLevel.MEDIUM
        self.current_challenge = self.game.get_challenge_by_difficulty(difficulty)
        
        # Update UI
        self.round_label.config(text=f"Round: {self.game_count}/{self.max_games}")
        self.location_label.config(text=f"Location: {self.current_challenge.location_name}")
        self.difficulty_label.config(text=f"Difficulty: {self.current_challenge.difficulty.value}")
        self.country_label.config(text=f"Country: {self.current_challenge.country}")
        self.continent_label.config(text=f"Continent: {self.current_challenge.continent}")
        
        # Display hints
        self.update_hints()
        
        # Reset buttons
        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.hint_button.config(state=tk.NORMAL)
        
        # Reset coordinate display
        self.coord_label.config(text="Click on the map to make your guess!")
        
        # Redraw map
        self.draw_world_map()
        self.canvas.draw()
    
    def update_hints(self):
        """Update the hints display"""
        self.hints_text.delete(1.0, tk.END)
        
        # Add initial hints
        for i, hint in enumerate(self.current_challenge.hints, 1):
            self.hints_text.insert(tk.END, f"{i}. {hint}\n")
        
        # Add geographic hint
        additional_hint = self.game.get_hint(len(self.current_challenge.hints))
        self.hints_text.insert(tk.END, f"{len(self.current_challenge.hints) + 1}. {additional_hint}\n")
    
    def get_extra_hint(self):
        """Provide extra hint"""
        self.extra_hints_used += 1
        
        if self.extra_hints_used == 1:
            hint = f"Extra Hint: This location is in {self.current_challenge.continent}"
        elif self.extra_hints_used == 2:
            actual_lat, actual_lon = self.current_challenge.actual_coordinates
            hemisphere = "Northern" if actual_lat > 0 else "Southern"
            hint = f"Extra Hint: This location is in the {hemisphere} Hemisphere"
        elif self.extra_hints_used == 3:
            actual_lat, actual_lon = self.current_challenge.actual_coordinates
            hemisphere = "Eastern" if actual_lon > 0 else "Western"
            hint = f"Extra Hint: This location is in the {hemisphere} Hemisphere"
        else:
            hint = "No more hints available!"
            self.hint_button.config(state=tk.DISABLED)
        
        self.hints_text.insert(tk.END, f"\n💡 {hint}\n")
        self.hints_text.see(tk.END)
    
    def submit_guess(self):
        """Submit the current guess"""
        if self.guess_lat is None or self.guess_lon is None:
            messagebox.showwarning("No Guess", "Please click on the map to make your guess!")
            return
        
        # Score the attempt
        attempt = self.game.score_attempt((self.guess_lat, self.guess_lon))
        actual_lat, actual_lon = self.current_challenge.actual_coordinates
        
        # Show actual location on map
        if self.actual_marker:
            self.actual_marker.remove()
        self.actual_marker = self.ax.plot(actual_lon, actual_lat, 'g*', 
                                        markersize=15, label='Actual Location')[0]
        
        # Draw line between guess and actual
        self.ax.plot([self.guess_lon, actual_lon], [self.guess_lat, actual_lat], 
                    'r--', alpha=0.7, linewidth=2)
        
        # Add legend
        self.ax.legend()
        self.canvas.draw()
        
        # Calculate final score with hint penalty
        penalty = min(100, self.extra_hints_used * 25) if self.extra_hints_used > 0 else 0
        final_score = max(0, attempt.accuracy_score - penalty)
        
        # Show results
        result_text = f"""
🎯 Results for {self.current_challenge.location_name}:

📍 Your guess: ({self.guess_lat:.2f}°, {self.guess_lon:.2f}°)
🎯 Actual location: ({actual_lat:.2f}°, {actual_lon:.2f}°)
📏 Distance off: {attempt.distance_km:.1f} km
⭐ Base score: {attempt.accuracy_score}/1000 points
"""
        
        if penalty > 0:
            result_text += f"🔻 Hint penalty: -{penalty} points\n"
            result_text += f"📊 Final score: {final_score}/1000 points\n"
        
        # Performance feedback
        if final_score >= 800:
            feedback = "🎉 Excellent! You're very close!"
        elif final_score >= 600:
            feedback = "👍 Good guess! Getting warmer!"
        elif final_score >= 400:
            feedback = "🤔 Not bad, but you can do better!"
        else:
            feedback = "📚 Keep practicing! Geography takes time to master!"
        
        result_text += f"\n{feedback}"
        
        messagebox.showinfo("Round Results", result_text)
        
        # Disable submit, enable next
        self.submit_button.config(state=tk.DISABLED)
        self.hint_button.config(state=tk.DISABLED)
        if self.game_count < self.max_games:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(text="View Final Results", state=tk.NORMAL)
    
    def show_final_results(self):
        """Show final game statistics"""
        analytics = self.game.get_performance_analytics()
        
        if "message" not in analytics:
            overview = analytics["overview"]
            distance = analytics["distance_analysis"]
            
            result_text = f"""
🎮 Game Session Complete!
═══════════════════════

🎮 Games played: {overview['total_games']}
⭐ Average score: {overview['average_score']:.1f}/1000
🏆 Best score: {overview['best_score']}/1000
📏 Average distance: {distance['average_distance_km']:.1f} km
🎯 Best guess: {distance['best_distance_km']:.1f} km away

Thanks for playing the GeoChallenge Game!

This demonstrates:
• Interactive map-based geographic guessing
• Real-time distance calculations using GeoPandas
• Statistical performance analysis with Pandas
• GUI integration with matplotlib and tkinter
"""
        else:
            result_text = "Game complete! Thanks for playing!"
        
        messagebox.showinfo("Final Results", result_text)
        self.root.quit()

def main():
    """Main function to run the interactive map game"""
    try:
        print("🌍 Starting Interactive Map-based GeoChallenge Game...")
        
        root = tk.Tk()
        app = InteractiveMapGame(root)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
