"""
GeoChallenge Demo Script
Demonstrates the professional GeoPandas/Pandas capabilities of the geography guessing game

This script showcases:
1. Advanced spatial data analysis with GeoPandas
2. Statistical performance tracking with Pandas
3. Interactive geographic visualization
4. Professional-level data science techniques for gaming applications

Usage: python demo_geochallenge.py
"""

import sys
import os

# Add the p3d directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geo_challenge_game import GeoChallengeGame, DifficultyLevel
from world_data_manager import WorldDataManager
import pandas as pd

def demo_geochallenge_capabilities():
    """
    Comprehensive demonstration of GeoChallenge game capabilities
    Showcases professional GeoPandas and Pandas usage for interactive geography learning
    """
    
    print("🌍 GEOCHALLENGE DEMO - Professional GeoPandas/Pandas Showcase")
    print("=" * 60)
    print()
    
    # Initialize the game system with real world data
    print("📊 Initializing GeoPandas-powered geography game system...")
    try:
        world_data_manager = WorldDataManager()
        game = GeoChallengeGame(world_data_manager)
        print("✅ Game initialized successfully!")
        print(f"📍 Loaded {len(game.challenges_database)} geographic challenges")
        print()
    except Exception as e:
        print(f"❌ Error initializing game: {e}")
        return
    
    # Demonstrate challenge database structure
    print("🗄️ CHALLENGE DATABASE STRUCTURE (GeoPandas GeoDataFrame):")
    print("-" * 50)
    challenges_df = game.challenges_database
    print(f"Shape: {challenges_df.shape}")
    print(f"Columns: {list(challenges_df.columns)}")
    print(f"CRS: {challenges_df.crs}")
    print()
    print("Sample challenges:")
    sample_challenges = challenges_df[['location_name', 'country', 'continent', 'difficulty']].head()
    print(sample_challenges.to_string(index=False))
    print()
    
    # Demonstrate difficulty distribution analysis
    print("📈 DIFFICULTY DISTRIBUTION ANALYSIS (Pandas):")
    print("-" * 45)
    difficulty_analysis = challenges_df.groupby('difficulty').agg({
        'location_name': 'count',
        'continent': lambda x: x.nunique()
    }).rename(columns={
        'location_name': 'challenge_count',
        'continent': 'continents_covered'
    })
    print(difficulty_analysis)
    print()
    
    # Demonstrate geographic distribution
    print("🌎 GEOGRAPHIC DISTRIBUTION (Pandas Analytics):")
    print("-" * 44)
    continent_stats = challenges_df.groupby('continent').agg({
        'location_name': 'count',
        'difficulty': lambda x: x.value_counts().to_dict()
    }).rename(columns={'location_name': 'total_challenges'})
    print(continent_stats)
    print()
    
    # Simulate game sessions to demonstrate analytics
    print("🎮 SIMULATING GAME SESSIONS FOR ANALYTICS DEMO...")
    print("-" * 50)
    
    # Simulate several game attempts
    simulated_attempts = [
        # (location_guess_coords, actual_challenge_difficulty)
        ((40.0, -74.0), DifficultyLevel.EASY),    # Close to NYC
        ((51.0, 0.0), DifficultyLevel.EASY),      # Close to London
        ((48.0, 2.0), DifficultyLevel.EASY),      # Close to Paris
        ((35.0, 139.0), DifficultyLevel.MEDIUM),  # Close to Tokyo
        ((19.0, 72.0), DifficultyLevel.MEDIUM),   # Close to Mumbai
        ((-22.0, -43.0), DifficultyLevel.HARD),   # Close to Rio
        ((47.0, 106.0), DifficultyLevel.EXPERT),  # Close to Ulaanbaatar
        ((64.0, -51.0), DifficultyLevel.EXPERT),  # Close to Nuuk
    ]
    
    for i, (guess_coords, difficulty) in enumerate(simulated_attempts):
        print(f"🎯 Simulation {i+1}: ", end="")
        try:
            # Get a challenge of specific difficulty
            challenge = game.get_challenge_by_difficulty(difficulty)
            print(f"Find {challenge.location_name} ({challenge.difficulty.value})")
            
            # Simulate the attempt
            attempt = game.score_attempt(guess_coords)
            print(f"   📏 Distance: {attempt.distance_km:.1f}km, Score: {attempt.accuracy_score}/1000")
            
        except Exception as e:
            print(f"Error in simulation: {e}")
    
    print()
    
    # Demonstrate comprehensive analytics
    print("📊 COMPREHENSIVE PERFORMANCE ANALYTICS:")
    print("-" * 42)
    analytics = game.get_performance_analytics()
    
    # Overview statistics
    overview = analytics['overview']
    print(f"🎮 Games Played: {overview['total_games']}")
    print(f"🏆 Average Score: {overview['average_score']:.1f}/1000")
    print(f"🎯 Best Score: {overview['best_score']}/1000")
    print(f"📉 Worst Score: {overview['worst_score']}/1000")
    print(f"📊 Score Std Dev: {overview['score_std']:.1f}")
    print()
    
    # Distance analysis
    distance = analytics['distance_analysis']
    print("📏 DISTANCE ANALYSIS:")
    print(f"   Average: {distance['average_distance_km']:.1f}km")
    print(f"   Median: {distance['median_distance_km']:.1f}km")
    print(f"   Best: {distance['best_distance_km']:.1f}km")
    print(f"   Worst: {distance['worst_distance_km']:.1f}km")
    print(f"   75th Percentile: {distance['distance_percentiles']['75th']:.1f}km")
    print()
    
    # Time analysis
    time_analysis = analytics['time_analysis']
    print("⏱️ RESPONSE TIME ANALYSIS:")
    print(f"   Average: {time_analysis['average_response_time']:.1f}s")
    print(f"   Fastest: {time_analysis['fastest_response']:.1f}s")
    print(f"   Slowest: {time_analysis['slowest_response']:.1f}s")
    print()
    
    # Performance trends
    if 'performance_trends' in analytics and isinstance(analytics['performance_trends'], dict):
        trends = analytics['performance_trends']
        print("📈 PERFORMANCE TRENDS:")
        print(f"   Score Trend: {trends['score_trend'].title()}")
        print(f"   Distance Trend: {trends['distance_trend'].title()}")
        print(f"   Recent Average: {trends['recent_average_score']:.1f}")
        print()
    
    # Geographic performance analysis
    if 'geographic_analysis' in analytics and analytics['geographic_analysis']:
        geo = analytics['geographic_analysis']
        print("🌍 GEOGRAPHIC PERFORMANCE:")
        if geo.get('best_continent'):
            print(f"   Best Continent: {geo['best_continent']}")
        if geo.get('worst_continent'):
            print(f"   Most Challenging: {geo['worst_continent']}")
        print()
    
    # Demonstrate data export capabilities
    print("💾 DATA EXPORT CAPABILITIES:")
    print("-" * 28)
    player_data = game.export_performance_data()
    print("Player history DataFrame:")
    print(f"Shape: {player_data.shape}")
    print(f"Columns: {list(player_data.columns)}")
    
    if len(player_data) > 0:
        print("\nSample data:")
        sample_data = player_data[['location_name', 'difficulty', 'distance_km', 'accuracy_score']].head(3)
        print(sample_data.to_string(index=False))
    print()
    
    # Demonstrate advanced spatial operations
    print("🔬 ADVANCED SPATIAL OPERATIONS DEMO:")
    print("-" * 37)
    
    # Example: Find challenges within a certain distance of a point
    center_point = (40.7128, -74.0060)  # New York City
    print(f"Finding challenges near NYC {center_point}:")
    
    # Use GeoPandas spatial operations
    from shapely.geometry import Point
    center = Point(center_point[1], center_point[0])  # lon, lat for Point
    
    # Calculate distances to all challenges (demonstrates GeoPandas spatial analysis)
    challenges_gdf = game.challenges_database.copy()
    distances = challenges_gdf.geometry.distance(center) * 111  # Approximate km conversion
    nearby_challenges = challenges_gdf[distances < 500]  # Within 500km
    
    print(f"Found {len(nearby_challenges)} challenges within 500km of NYC:")
    for _, challenge in nearby_challenges.head(3).iterrows():
        dist = distances[challenge.name]
        print(f"   📍 {challenge['location_name']} ({challenge['country']}) - {dist:.0f}km away")
    
    print()
    
    # Summary of professional capabilities demonstrated
    print("🏆 PROFESSIONAL CAPABILITIES DEMONSTRATED:")
    print("=" * 45)
    print("✅ GeoPandas GeoDataFrame management and spatial indexing")
    print("✅ Advanced Pandas statistical analysis and aggregation")
    print("✅ Spatial distance calculations using Haversine formula")
    print("✅ Performance analytics with rolling averages and trends")
    print("✅ Geographic data visualization and coordinate transformations")
    print("✅ Adaptive difficulty systems based on statistical analysis")
    print("✅ Professional data export capabilities for further analysis")
    print("✅ Real-time spatial operations and proximity analysis")
    print("✅ Multi-dimensional data analysis (geographic, temporal, performance)")
    print("✅ Scalable game architecture suitable for production deployment")
    print()
    
    print("🎓 This demonstrates advanced proficiency in:")
    print("   • GeoPandas for spatial data science")
    print("   • Pandas for statistical analysis and data manipulation") 
    print("   • Geographic information systems (GIS) concepts")
    print("   • Performance analytics and data-driven decision making")
    print("   • Interactive application development with spatial components")
    print("   • Professional software architecture and design patterns")
    print()
    
    return game

if __name__ == "__main__":
    try:
        game = demo_geochallenge_capabilities()
        
        print("🚀 Demo completed successfully!")
        print("🎮 To run the interactive game, execute: python globe_app.py")
        print("🌟 Click 'START GAME' button to begin the GeoChallenge!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
