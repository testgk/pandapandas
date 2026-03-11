"""
GeoChallenge Game Module - Interactive Geography Game
Showcases advanced GeoPandas and Pandas capabilities for professional demonstration

Features:
- Geographic location guessing game
- Spatial distance calculations
- Statistical performance analysis
- Dynamic difficulty adjustment
- Real-time scoring system
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from datetime import datetime, timedelta
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DifficultyLevel(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

@dataclass
class GameChallenge:
    """Represents a single game challenge"""
    location_name: str
    actual_coordinates: Tuple[float, float]  # (lat, lon)
    country: str
    continent: str
    difficulty: DifficultyLevel
    hints: List[str]
    max_distance_km: float  # Maximum reasonable distance for full points

@dataclass
class PlayerAttempt:
    """Represents a player's attempt at a challenge"""
    challenge_id: str
    clicked_coordinates: Tuple[float, float]  # (lat, lon)
    distance_km: float
    accuracy_score: int  # 0-1000 points
    response_time_seconds: float
    timestamp: datetime

class GeoChallengeGame:
    """
    Advanced Geography Challenge Game using GeoPandas and Pandas
    
    Demonstrates professional-level usage of:
    - Spatial data analysis with GeoPandas
    - Statistical analysis with Pandas
    - Performance tracking and analytics
    - Dynamic difficulty adjustment
    """
    
    def __init__(self, world_data_manager):
        self.world_data_manager = world_data_manager
        self.challenges_database = self._load_challenges_database()
        self.player_history = pd.DataFrame(columns=[
            'challenge_id', 'location_name', 'difficulty', 'distance_km', 
            'accuracy_score', 'response_time', 'timestamp'
        ])
        self.current_challenge = None
        self.challenge_start_time = None
        self.game_statistics = self._initialize_statistics()
        
    def _load_challenges_database(self) -> pd.DataFrame:
        """Load and create geographic challenges database using GeoPandas"""
        print("🗄️ Loading geographic challenges database...")
        
        # Create comprehensive challenges database
        challenges_data = []
        
        # Major world cities with varying difficulty
        cities_easy = [
            ("New York", (40.7128, -74.0060), "United States", "North America", ["Largest city in USA", "Big Apple", "Statue of Liberty"]),
            ("London", (51.5074, -0.1278), "United Kingdom", "Europe", ["Big Ben", "Thames River", "Capital of UK"]),
            ("Paris", (48.8566, 2.3522), "France", "Europe", ["Eiffel Tower", "City of Light", "Capital of France"]),
            ("Tokyo", (35.6762, 139.6503), "Japan", "Asia", ["Capital of Japan", "Mount Fuji nearby", "Largest metro area"]),
            ("Sydney", (-33.8688, 151.2093), "Australia", "Oceania", ["Opera House", "Harbor Bridge", "Largest city in Australia"]),
        ]
        
        cities_medium = [
            ("Cairo", (30.0444, 31.2357), "Egypt", "Africa", ["Pyramids nearby", "Nile River", "Capital of Egypt"]),
            ("Mumbai", (19.0760, 72.8777), "India", "Asia", ["Bollywood", "Gateway of India", "Financial capital of India"]),
            ("Rio de Janeiro", (-22.9068, -43.1729), "Brazil", "South America", ["Christ the Redeemer", "Copacabana Beach", "Former capital"]),
            ("Istanbul", (41.0082, 28.9784), "Turkey", "Europe/Asia", ["Bosphorus Bridge", "Between two continents", "Former Constantinople"]),
            ("Cape Town", (-33.9249, 18.4241), "South Africa", "Africa", ["Table Mountain", "Cape of Good Hope", "Legislative capital"]),
        ]
        
        cities_hard = [
            ("Ulaanbaatar", (47.8864, 106.9057), "Mongolia", "Asia", ["Capital of Mongolia", "Coldest capital", "Genghis Khan"]),
            ("Reykjavik", (64.1466, -21.9426), "Iceland", "Europe", ["Northernmost capital", "Geysers", "Northern Lights"]),
            ("Antananarivo", (-18.8792, 47.5079), "Madagascar", "Africa", ["Capital of Madagascar", "Island nation", "Lemurs"]),
            ("Vientiane", (17.9757, 102.6331), "Laos", "Asia", ["Capital of Laos", "Mekong River", "Buddhist temples"]),
            ("Port Vila", (-17.7333, 168.3273), "Vanuatu", "Oceania", ["Capital of Vanuatu", "Pacific islands", "Volcanoes"]),
        ]
        
        cities_expert = [
            ("Nuuk", (64.1836, -51.7214), "Greenland", "North America", ["Capital of Greenland", "Arctic Circle", "Icebergs"]),
            ("Funafuti", (-8.5167, 179.2167), "Tuvalu", "Oceania", ["Capital of Tuvalu", "Smallest country", "Rising sea levels"]),
            ("Majuro", (7.1315, 171.1845), "Marshall Islands", "Oceania", ["Capital of Marshall Islands", "Coral atolls", "Pacific"]),
            ("Ngerulmud", (7.5006, 134.6242), "Palau", "Oceania", ["Capital of Palau", "Rock Islands", "Diving paradise"]),
            ("Avarua", (-21.2078, -159.7750), "Cook Islands", "Oceania", ["Capital of Cook Islands", "Polynesia", "Lagoons"]),
        ]
        
        # Process cities and create challenges
        for cities, difficulty in [
            (cities_easy, DifficultyLevel.EASY),
            (cities_medium, DifficultyLevel.MEDIUM), 
            (cities_hard, DifficultyLevel.HARD),
            (cities_expert, DifficultyLevel.EXPERT)
        ]:
            for name, coords, country, continent, hints in cities:
                # Calculate max distance based on difficulty
                max_distances = {
                    DifficultyLevel.EASY: 1000,    # 1000km for easy
                    DifficultyLevel.MEDIUM: 500,   # 500km for medium
                    DifficultyLevel.HARD: 250,     # 250km for hard
                    DifficultyLevel.EXPERT: 100    # 100km for expert
                }
                
                challenge = GameChallenge(
                    location_name=name,
                    actual_coordinates=coords,
                    country=country,
                    continent=continent,
                    difficulty=difficulty,
                    hints=hints,
                    max_distance_km=max_distances[difficulty]
                )
                
                challenges_data.append({
                    'id': f"{name.lower().replace(' ', '_')}_{country.lower().replace(' ', '_')}",
                    'location_name': challenge.location_name,
                    'latitude': challenge.actual_coordinates[0],
                    'longitude': challenge.actual_coordinates[1],
                    'country': challenge.country,
                    'continent': challenge.continent,
                    'difficulty': challenge.difficulty.value,
                    'hints': challenge.hints,
                    'max_distance_km': challenge.max_distance_km
                })
        
        # Convert to GeoDataFrame for spatial operations
        df = pd.DataFrame(challenges_data)
        geometry = [Point(lon, lat) for lat, lon in zip(df['latitude'], df['longitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        print(f"✅ Loaded {len(gdf)} geographic challenges across {len(gdf['difficulty'].unique())} difficulty levels")
        return gdf
    
    def _initialize_statistics(self) -> Dict:
        """Initialize game statistics tracking"""
        return {
            'total_games': 0,
            'correct_guesses': 0,
            'total_score': 0,
            'average_distance': 0.0,
            'best_score': 0,
            'worst_score': 1000,
            'difficulty_stats': {level.value: {'attempts': 0, 'successes': 0} for level in DifficultyLevel}
        }
    
    def get_challenge_by_difficulty(self, difficulty: DifficultyLevel = None) -> GameChallenge:
        """
        Get a random challenge, optionally filtered by difficulty
        Uses Pandas for intelligent selection based on player performance
        """
        available_challenges = self.challenges_database.copy()
        
        # Filter by difficulty if specified
        if difficulty:
            available_challenges = available_challenges[
                available_challenges['difficulty'] == difficulty.value
            ]
        else:
            # Intelligent difficulty selection based on player performance
            difficulty = self._calculate_adaptive_difficulty()
            available_challenges = available_challenges[
                available_challenges['difficulty'] == difficulty.value
            ]
        
        # Avoid repeating recent challenges (using pandas operations)
        if len(self.player_history) > 0:
            recent_challenges = self.player_history.tail(5)['challenge_id'].tolist()
            available_challenges = available_challenges[
                ~available_challenges['id'].isin(recent_challenges)
            ]
        
        # Select random challenge
        if len(available_challenges) == 0:
            available_challenges = self.challenges_database  # Fallback
            
        selected_row = available_challenges.sample(n=1).iloc[0]
        
        challenge = GameChallenge(
            location_name=selected_row['location_name'],
            actual_coordinates=(selected_row['latitude'], selected_row['longitude']),
            country=selected_row['country'],
            continent=selected_row['continent'],
            difficulty=DifficultyLevel(selected_row['difficulty']),
            hints=selected_row['hints'],
            max_distance_km=selected_row['max_distance_km']
        )
        
        self.current_challenge = challenge
        self.challenge_start_time = datetime.now()
        
        return challenge
    
    def _calculate_adaptive_difficulty(self) -> DifficultyLevel:
        """
        Calculate appropriate difficulty based on player performance using Pandas analytics
        """
        if len(self.player_history) < 3:
            return DifficultyLevel.EASY
        
        # Analyze recent performance (last 10 games)
        recent_games = self.player_history.tail(10)
        
        # Calculate performance metrics using Pandas
        avg_score = recent_games['accuracy_score'].mean()
        success_rate = (recent_games['accuracy_score'] > 700).sum() / len(recent_games)
        avg_response_time = recent_games['response_time'].mean()
        
        # Difficulty adjustment logic
        if avg_score > 800 and success_rate > 0.7:
            if avg_response_time < 10:  # Fast and accurate = Expert
                return DifficultyLevel.EXPERT
            else:
                return DifficultyLevel.HARD
        elif avg_score > 600 and success_rate > 0.5:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.EASY
    
    def calculate_distance_km(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calculate great-circle distance between two points using Haversine formula
        Professional geographic distance calculation
        """
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        return earth_radius_km * c
    
    def score_attempt(self, clicked_coordinates: Tuple[float, float]) -> PlayerAttempt:
        """
        Score a player's attempt using advanced spatial analysis
        """
        if not self.current_challenge or not self.challenge_start_time:
            raise ValueError("No active challenge")
        
        # Calculate distance using GeoPandas spatial operations
        distance_km = self.calculate_distance_km(
            clicked_coordinates, 
            self.current_challenge.actual_coordinates
        )
        
        # Calculate response time
        response_time = (datetime.now() - self.challenge_start_time).total_seconds()
        
        # Advanced scoring algorithm
        max_distance = self.current_challenge.max_distance_km
        base_score = max(0, 1000 * (1 - distance_km / max_distance))
        
        # Bonus for quick responses
        time_bonus = max(0, 100 * (1 - response_time / 60))  # Bonus for sub-60 second responses
        
        # Difficulty multiplier
        difficulty_multipliers = {
            DifficultyLevel.EASY: 1.0,
            DifficultyLevel.MEDIUM: 1.2,
            DifficultyLevel.HARD: 1.5,
            DifficultyLevel.EXPERT: 2.0
        }
        
        final_score = int((base_score + time_bonus) * difficulty_multipliers[self.current_challenge.difficulty])
        final_score = max(0, min(1000, final_score))  # Clamp to 0-1000
        
        # Create attempt record
        attempt = PlayerAttempt(
            challenge_id=f"{self.current_challenge.location_name}_{datetime.now().timestamp()}",
            clicked_coordinates=clicked_coordinates,
            distance_km=distance_km,
            accuracy_score=final_score,
            response_time_seconds=response_time,
            timestamp=datetime.now()
        )
        
        # Store in player history using Pandas
        new_row = {
            'challenge_id': attempt.challenge_id,
            'location_name': self.current_challenge.location_name,
            'difficulty': self.current_challenge.difficulty.value,
            'distance_km': attempt.distance_km,
            'accuracy_score': attempt.accuracy_score,
            'response_time': attempt.response_time_seconds,
            'timestamp': attempt.timestamp
        }
        
        self.player_history = pd.concat([
            self.player_history, 
            pd.DataFrame([new_row])
        ], ignore_index=True)
        
        # Update statistics
        self._update_statistics(attempt)
        
        return attempt
    
    def _update_statistics(self, attempt: PlayerAttempt):
        """Update game statistics using Pandas analytics"""
        stats = self.game_statistics
        stats['total_games'] += 1
        stats['total_score'] += attempt.accuracy_score
        
        if attempt.accuracy_score > 700:  # Consider 700+ as "correct"
            stats['correct_guesses'] += 1
        
        stats['best_score'] = max(stats['best_score'], attempt.accuracy_score)
        stats['worst_score'] = min(stats['worst_score'], attempt.accuracy_score)
        
        # Update difficulty-specific stats
        difficulty = self.current_challenge.difficulty.value
        stats['difficulty_stats'][difficulty]['attempts'] += 1
        if attempt.accuracy_score > 700:
            stats['difficulty_stats'][difficulty]['successes'] += 1
        
        # Calculate running averages using Pandas
        if len(self.player_history) > 0:
            stats['average_distance'] = self.player_history['distance_km'].mean()
    
    def get_performance_analytics(self) -> Dict:
        """
        Generate comprehensive performance analytics using Pandas
        Demonstrates advanced statistical analysis capabilities
        """
        if len(self.player_history) == 0:
            return {"message": "No games played yet"}
        
        df = self.player_history
        
        analytics = {
            "overview": {
                "total_games": len(df),
                "average_score": df['accuracy_score'].mean(),
                "median_score": df['accuracy_score'].median(),
                "score_std": df['accuracy_score'].std(),
                "best_score": df['accuracy_score'].max(),
                "worst_score": df['accuracy_score'].min()
            },
            "distance_analysis": {
                "average_distance_km": df['distance_km'].mean(),
                "median_distance_km": df['distance_km'].median(),
                "best_distance_km": df['distance_km'].min(),
                "worst_distance_km": df['distance_km'].max(),
                "distance_percentiles": {
                    "25th": df['distance_km'].quantile(0.25),
                    "75th": df['distance_km'].quantile(0.75),
                    "90th": df['distance_km'].quantile(0.90)
                }
            },
            "time_analysis": {
                "average_response_time": df['response_time'].mean(),
                "median_response_time": df['response_time'].median(),
                "fastest_response": df['response_time'].min(),
                "slowest_response": df['response_time'].max()
            },
            "difficulty_breakdown": df.groupby('difficulty').agg({
                'accuracy_score': ['count', 'mean', 'std'],
                'distance_km': 'mean',
                'response_time': 'mean'
            }).round(2).to_dict(),
            "performance_trends": self._calculate_performance_trends(),
            "geographic_analysis": self._analyze_geographic_performance()
        }
        
        return analytics
    
    def _calculate_performance_trends(self) -> Dict:
        """Calculate performance trends over time using Pandas"""
        if len(self.player_history) < 5:
            return {"message": "Need more games for trend analysis"}
        
        df = self.player_history.copy()
        df['game_number'] = range(1, len(df) + 1)
        
        # Calculate rolling averages
        df['rolling_score_5'] = df['accuracy_score'].rolling(window=5, min_periods=1).mean()
        df['rolling_distance_5'] = df['distance_km'].rolling(window=5, min_periods=1).mean()
        
        # Linear regression for trend analysis
        recent_games = df.tail(10)
        
        # Ensure numeric types for numpy polyfit
        game_numbers = recent_games['game_number'].astype(float).values
        scores = recent_games['accuracy_score'].astype(float).values
        distances = recent_games['distance_km'].astype(float).values
        
        score_trend = np.polyfit(game_numbers, scores, 1)[0]
        distance_trend = np.polyfit(game_numbers, distances, 1)[0]
        
        return {
            "score_trend": "improving" if score_trend > 0 else "declining" if score_trend < 0 else "stable",
            "distance_trend": "improving" if distance_trend < 0 else "declining" if distance_trend > 0 else "stable",
            "recent_average_score": recent_games['accuracy_score'].mean(),
            "score_improvement": score_trend,
            "distance_improvement": -distance_trend  # Negative because lower distance is better
        }
    
    def _analyze_geographic_performance(self) -> Dict:
        """Analyze performance by geographic regions using GeoPandas"""
        if len(self.player_history) == 0:
            return {}
        
        # Merge player history with challenges database for geographic analysis
        df = self.player_history.merge(
            self.challenges_database[['location_name', 'continent', 'country']], 
            on='location_name', 
            how='left'
        )
        
        # Performance by continent
        continent_stats = df.groupby('continent').agg({
            'accuracy_score': ['count', 'mean', 'std'],
            'distance_km': 'mean'
        }).round(2)
        
        # Best and worst performing regions
        continent_means = df.groupby('continent')['accuracy_score'].mean().sort_values(ascending=False)
        
        return {
            "best_continent": continent_means.index[0] if len(continent_means) > 0 else None,
            "worst_continent": continent_means.index[-1] if len(continent_means) > 0 else None,
            "continent_performance": continent_stats.to_dict(),
            "games_by_continent": df['continent'].value_counts().to_dict()
        }
    
    def get_hint(self, hint_level: int = 0) -> str:
        """Get a hint for the current challenge"""
        if not self.current_challenge:
            return "No active challenge"
        
        hints = self.current_challenge.hints
        if hint_level < len(hints):
            return hints[hint_level]
        else:
            # Generate geographic hint using spatial analysis
            lat, lon = self.current_challenge.actual_coordinates
            
            # Determine hemisphere and general region
            hemisphere_ns = "Northern" if lat > 0 else "Southern"
            hemisphere_ew = "Eastern" if lon > 0 else "Western"
            
            region_hint = f"Located in the {hemisphere_ns} and {hemisphere_ew} hemispheres"
            
            # Add climate zone hint
            if abs(lat) < 23.5:
                climate_hint = "In the tropical zone"
            elif abs(lat) < 66.5:
                climate_hint = "In the temperate zone"
            else:
                climate_hint = "In the polar zone"
            
            return f"{region_hint}. {climate_hint}."
    
    def export_performance_data(self) -> pd.DataFrame:
        """Export player history for external analysis"""
        return self.player_history.copy()
