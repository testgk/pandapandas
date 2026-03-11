#!/usr/bin/env python3
"""
Simple GeoChallenge Game Runner - Text-based interface
Demonstrates the GeoPandas-powered geography challenge game
"""
import sys
import os
from pathlib import Path
import math

# Add p3d directory to path so we can import the game modules
sys.path.append(str(Path(__file__).parent / "p3d"))

try:
    # Try importing required modules
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import Point
    print("✅ Successfully imported core dependencies")
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Please install required packages with: pip install pandas numpy shapely")
    sys.exit(1)

# Simple WorldDataManager mock for the text-based version
class SimpleWorldDataManager:
    """Simple mock for WorldDataManager that doesn't require downloading data"""
    def __init__(self):
        pass

def run_text_based_game():
    """Run a simple text-based version of the geography challenge game"""
    print("🌍 Welcome to the GeoChallenge Game!")
    print("=" * 50)
    
    try:
        # Import the game class
        from geo_challenge_game import GeoChallengeGame, DifficultyLevel
        
        # Create world data manager (mock)
        world_manager = SimpleWorldDataManager()
        
        # Initialize the game
        print("🎮 Initializing GeoChallenge Game...")
        game = GeoChallengeGame(world_manager)
        
        print("✅ Game initialized successfully!")
        print(f"📊 Loaded challenges database with {len(game.challenges_database)} locations")
        
        # Game loop
        game_count = 0
        max_games = 5  # Play 5 rounds for demo
        
        print(f"\n🏁 Starting game session ({max_games} rounds)")
        print("=" * 50)
        
        while game_count < max_games:
            game_count += 1
            print(f"\n🎯 Round {game_count}/{max_games}")
            print("-" * 30)
            
            # Get a challenge
            difficulty = DifficultyLevel.EASY if game_count <= 2 else DifficultyLevel.MEDIUM
            challenge = game.get_challenge_by_difficulty(difficulty)
            
            # Display challenge info
            print(f"📍 Challenge: Locate '{challenge.location_name}'")
            print(f"🎚️  Difficulty: {challenge.difficulty.value}")
            print(f"🏛️  Country: {challenge.country}")
            print(f"🌎 Continent: {challenge.continent}")
            
            # Show hints
            print("\n💡 Hints:")
            for i, hint in enumerate(challenge.hints, 1):
                print(f"   {i}. {hint}")
            
            # Get additional geographic hint
            additional_hint = game.get_hint(len(challenge.hints))
            print(f"   {len(challenge.hints) + 1}. {additional_hint}")
            
            # Interactive help system
            print("\n📚 Need help? Commands:")
            print("   • Type 'help' for geographic tips")
            print("   • Type 'hint' for an extra clue")
            print("   • Type 'quit' to exit the game")
            print("   • Or enter coordinates directly: lat lon (e.g., 48.86 2.35)")
            
            # Track hints used for scoring
            extra_hints_used = 0
            
            # Get user input for coordinates
            print("\n🎯 Your turn! Enter your guess:")
            print("📝 Enter coordinates as latitude and longitude (e.g., 48.86 2.35)")
            print("💡 Latitude: -90 to 90 (North positive, South negative)")
            print("💡 Longitude: -180 to 180 (East positive, West negative)")
            
            # Input validation loop
            while True:
                try:
                    user_input = input("\n🌍 Enter your guess (lat lon) or command: ").strip()
                    
                    # Handle quit command
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Thanks for playing! Goodbye!")
                        return
                    
                    # Handle help commands
                    elif user_input.lower() == 'help':
                        print("\n🗺️  Geographic Tips:")
                        print("   • Europe: Latitude ~35-70°N, Longitude ~10°W-40°E")
                        print("   • North America: Latitude ~25-70°N, Longitude ~170-50°W")
                        print("   • Asia: Latitude ~10-70°N, Longitude ~25-180°E")
                        print("   • Africa: Latitude ~35°S-35°N, Longitude ~20°W-50°E")
                        print("   • South America: Latitude ~55°S-15°N, Longitude ~80-35°W")
                        print("   • Australia: Latitude ~45-10°S, Longitude ~110-155°E")
                        continue
                    
                    elif user_input.lower() == 'hint':
                        extra_hints_used += 1
                        if extra_hints_used == 1:
                            print(f"💡 Extra Hint: This location is in {challenge.continent}")
                        elif extra_hints_used == 2:
                            # Get actual coordinates for more specific hint
                            actual_lat, actual_lon = challenge.actual_coordinates
                            if actual_lat > 0:
                                print("💡 Extra Hint: This location is in the Northern Hemisphere")
                            else:
                                print("💡 Extra Hint: This location is in the Southern Hemisphere")
                        elif extra_hints_used == 3:
                            actual_lat, actual_lon = challenge.actual_coordinates
                            if actual_lon > 0:
                                print("💡 Extra Hint: This location is in the Eastern Hemisphere")
                            else:
                                print("💡 Extra Hint: This location is in the Western Hemisphere")
                        else:
                            print("💡 No more hints available! Make your best guess.")
                        continue
                    
                    # Parse coordinates
                    coords = user_input.split()
                    if len(coords) != 2:
                        print("❌ Please enter exactly two numbers (latitude longitude)")
                        print("💡 Example: 48.86 2.35 (for Paris)")
                        continue
                    
                    guess_lat = float(coords[0])
                    guess_lon = float(coords[1])
                    
                    # Validate ranges
                    if not (-90 <= guess_lat <= 90):
                        print("❌ Latitude must be between -90 and 90")
                        continue
                    
                    if not (-180 <= guess_lon <= 180):
                        print("❌ Longitude must be between -180 and 180")
                        continue
                    
                    print(f"✅ Your guess: ({guess_lat:.2f}, {guess_lon:.2f})")
                    break
                    
                except ValueError:
                    print("❌ Please enter valid numbers or a command")
                    print("💡 Commands: help, hint, quit")
                    print("💡 Coordinates: lat lon (e.g., 48.86 2.35)")
                except KeyboardInterrupt:
                    print("\n👋 Thanks for playing! Goodbye!")
                    return
                except EOFError:
                    print("\n👋 Thanks for playing! Goodbye!")
                    return
            
            # Score the attempt
            attempt = game.score_attempt((guess_lat, guess_lon))
            actual_lat, actual_lon = challenge.actual_coordinates
            
            # Display results
            print(f"\n📊 Results:")
            print(f"   🎯 Actual location: ({actual_lat:.2f}, {actual_lon:.2f})")
            print(f"   📏 Distance off: {attempt.distance_km:.1f} km")
            print(f"   ⭐ Score: {attempt.accuracy_score}/1000 points")
            print(f"   ⏱️  Response time: {attempt.response_time_seconds:.1f} seconds")
            
            # Adjust score for extra hints used
            if extra_hints_used > 0:
                penalty = min(100, extra_hints_used * 25)  # 25 points per extra hint, max 100
                adjusted_score = max(0, attempt.accuracy_score - penalty)
                print(f"   🔻 Hint penalty: -{penalty} points ({extra_hints_used} extra hints)")
                print(f"   📊 Final score: {adjusted_score}/1000 points")
            
            # Performance feedback
            final_score = attempt.accuracy_score - (min(100, extra_hints_used * 25) if extra_hints_used > 0 else 0)
            if final_score >= 800:
                print("   🎉 Excellent! You're very close!")
            elif final_score >= 600:
                print("   👍 Good guess! Getting warmer!")
            elif final_score >= 400:
                print("   🤔 Not bad, but you can do better!")
            else:
                print("   📚 Keep practicing! Geography takes time to master!")
            
            # Wait for user to continue
            input("\n⏳ Press Enter to continue to the next round...")
        
        # Show final statistics
        print(f"\n📈 Game Session Complete!")
        print("=" * 50)
        
        analytics = game.get_performance_analytics()
        if "message" not in analytics:
            overview = analytics["overview"]
            distance = analytics["distance_analysis"]
            
            print(f"🎮 Games played: {overview['total_games']}")
            print(f"⭐ Average score: {overview['average_score']:.1f}/1000")
            print(f"🏆 Best score: {overview['best_score']}/1000")
            print(f"📏 Average distance: {distance['average_distance_km']:.1f} km")
            print(f"🎯 Best guess: {distance['best_distance_km']:.1f} km away")
            
            # Show performance trends
            trends = analytics.get("performance_trends", {})
            if isinstance(trends, dict) and "score_trend" in trends:
                trend = trends["score_trend"]
                print(f"📊 Performance trend: {trend}")
        
        print(f"\n🎓 Thanks for playing the GeoChallenge Game!")
        print("This demonstrates advanced GeoPandas and Pandas capabilities:")
        print("• Spatial data analysis and distance calculations")
        print("• Statistical performance tracking and analytics")
        print("• Dynamic difficulty adjustment based on player performance")
        print("• Geographic data processing and visualization")
        
    except Exception as e:
        print(f"❌ Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_text_based_game()
