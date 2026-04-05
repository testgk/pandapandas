"""
Pydantic models for GeoChallenge API
These models define the request/response schemas for all API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
from datetime import datetime


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"


class ChallengeResponse( BaseModel ):
    """Response when getting a new challenge"""
    challenge_id: str
    location_name: str
    country: str
    continent: str
    difficulty: DifficultyLevel
    hints: List[str]
    max_distance_km: float
    # Note: actual coordinates are NOT sent to client (that would be cheating!)
    
    class Config:
        json_schema_extra = {
            "example": {
                "challenge_id": "paris_france_1234567890",
                "location_name": "Paris",
                "country": "France", 
                "continent": "Europe",
                "difficulty": "Easy",
                "hints": ["Eiffel Tower", "City of Light", "Capital of France"],
                "max_distance_km": 10000
            }
        }


class GuessRequest( BaseModel ):
    """Request to submit a guess for a challenge"""
    challenge_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    
    class Config:
        json_schema_extra = {
            "example": {
                "challenge_id": "paris_france_1234567890",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
        }


class GuessResponse( BaseModel ):
    """Response after submitting a guess"""
    success: bool
    distance_km: float
    accuracy_score: int  # 0-100 percentage
    response_time_seconds: float
    actual_coordinates: Tuple[float, float]  # Revealed after guess
    location_name: str
    feedback: str  # "Excellent!", "Great!", "Good try!", etc.
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "distance_km": 15.7,
                "accuracy_score": 95,
                "response_time_seconds": 8.5,
                "actual_coordinates": [48.8566, 2.3522],
                "location_name": "Paris",
                "feedback": "Excellent! Almost perfect!"
            }
        }


class HintRequest(BaseModel):
    """Request for an additional hint"""
    challenge_id: str
    hint_index: int = Field(..., ge=0, le=5)


class HintResponse(BaseModel):
    """Response with a hint"""
    hint: str
    hints_remaining: int
    total_hints: int


class SessionStats(BaseModel):
    """Statistics for current session"""
    total_games: int
    total_score: int
    average_accuracy: float
    best_score: int
    worst_score: int
    current_streak: int
    best_streak: int
    difficulty_stats: Dict[str, Dict[str, Any]]


class OverviewStats(BaseModel):
    """Overview statistics"""
    total_games: int
    average_score: float
    median_score: float
    score_std: float
    best_score: int
    worst_score: int


class DistanceStats(BaseModel):
    """Distance analysis statistics"""
    average_distance_km: float
    median_distance_km: float
    best_distance_km: float
    worst_distance_km: float
    percentile_25th: float
    percentile_75th: float
    percentile_90th: float


class TimeStats(BaseModel):
    """Response time statistics"""
    average_response_time: float
    median_response_time: float
    fastest_response: float
    slowest_response: float


class PerformanceAnalytics(BaseModel):
    """Comprehensive performance analytics"""
    overview: OverviewStats
    distance_analysis: DistanceStats
    time_analysis: TimeStats
    difficulty_breakdown: Dict[str, Any]
    message: Optional[str] = None


class SessionCreateResponse(BaseModel):
    """Response when creating a new session"""
    session_id: str
    message: str


class ChallengeListItem(BaseModel):
    """Item in list of available challenges (for admin/debug)"""
    id: str
    location_name: str
    country: str
    continent: str
    difficulty: DifficultyLevel


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    challenges_loaded: int
