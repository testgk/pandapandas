"""
Example demonstrating the scoring service usage.

This shows how a game would integrate with the scoring system.

Usage:
    1. Ensure PostgreSQL is running: docker-compose up -d
    2. Run: python scoring_example.py
"""

import random
from db import get_db_connection
from services.scoring_service import get_scoring_service, ScoringService
from entities.game_session import GameMode


def simulate_round() -> tuple:
    """Simulate a game round - returns (distance_error_km, response_time_seconds)."""
    # Random distance error between 10 and 2000 km
    distance = random.uniform(10, 2000)
    # Random response time between 2 and 15 seconds
    time = random.uniform(2, 15)
    return distance, time


def main():
    # Connect to database
    db = get_db_connection()
    db.connect()
    
    print("=" * 60)
    print("GeoChallenge Scoring System Demo")
    print("=" * 60)
    
    # Get scoring service
    scoring = get_scoring_service()
    
    # Use admin user (ID: 1) for demo
    user_id = 1
    
    # Start a new game
    print(f"\nStarting new game for user {user_id}...")
    session = scoring.start_game(
        user_id=user_id,
        game_mode=GameMode.CLASSIC,
        difficulty="medium",
        total_rounds=5
    )
    print(f"Game session started: ID={session.id}")
    
    # Simulate 5 rounds
    print("\n--- Playing Rounds ---")
    for round_num in range(5):
        distance, time = simulate_round()
        
        result = scoring.submit_round(
            session_id=session.id,
            distance_error_km=distance,
            response_time_seconds=time
        )
        
        print(f"\nRound {result.round_number}:")
        print(f"  Distance Error: {distance:.1f} km")
        print(f"  Response Time: {time:.1f}s")
        print(f"  Points Earned: {result.points_earned}")
        print(f"  Accuracy: {result.accuracy_percent}%")
        print(f"  Total Score: {result.total_score}")
    
    # End the game
    print("\n--- Game Complete ---")
    final = scoring.end_game(session.id)
    
    print(f"\nFinal Results:")
    print(f"  Score: {final.final_score}")
    print(f"  Accuracy: {final.accuracy}%")
    print(f"  Grade: {final.grade}")
    print(f"  Avg Response Time: {final.avg_response_time:.1f}s")
    print(f"  Personal Best: {'Yes!' if final.is_personal_best else 'No'}")
    print(f"  Rank: #{final.rank}" if final.rank else "  Rank: Unranked")
    
    # Show user stats
    print("\n--- Player Stats ---")
    stats = scoring.get_user_stats(user_id)
    print(f"  Games Played: {stats['games_played']}")
    print(f"  Total Score: {stats['total_score']}")
    print(f"  Best Score: {stats['best_score']}")
    print(f"  Avg Score: {stats['avg_score']}")
    print(f"  Avg Accuracy: {stats['avg_accuracy']}%")
    
    # Show leaderboard
    print("\n--- Leaderboard (Top 5) ---")
    leaderboard = scoring.get_leaderboard(game_mode="classic", limit=5)
    for entry in leaderboard:
        print(f"  #{entry['rank']} {entry['display_name']}: {entry['score'].points} pts")
    
    db.close()
    print("\n" + "=" * 60)
    print("Demo complete!")


if __name__ == "__main__":
    main()
