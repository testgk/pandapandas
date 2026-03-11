"""
Abstract interface for Globe Application
Defines the contract that any globe application must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IGlobeApplication(ABC):
    """Abstract interface for Globe Application implementations"""

    @abstractmethod
    def zoomIn(self) -> None:
        """Move camera closer to globe center"""
        pass

    @abstractmethod
    def zoomOut(self) -> None:
        """Move camera further from globe center"""
        pass

    @abstractmethod
    def resetView(self) -> None:
        """Reset camera position and globe rotation to default"""
        pass

    @abstractmethod
    def rotateUp(self) -> None:
        """Rotate globe up by increment amount"""
        pass

    @abstractmethod
    def rotateDown(self) -> None:
        """Rotate globe down by increment amount"""
        pass

    @abstractmethod
    def rotateLeft(self) -> None:
        """Rotate globe left by increment amount"""
        pass

    @abstractmethod
    def rotateRight(self) -> None:
        """Rotate globe right by increment amount"""
        pass

    @abstractmethod
    def increaseRotationIncrement(self) -> None:
        """Increase rotation increment by 1 degree"""
        pass

    @abstractmethod
    def decreaseRotationIncrement(self) -> None:
        """Decrease rotation increment by 1 degree"""
        pass

    @abstractmethod
    def setPresetView(self, index: int) -> None:
        """Set the globe to a specific preset view"""
        pass
    
    @abstractmethod
    def startGame(self) -> None:
        """Start the GeoChallenge game mode"""
        pass
    
    @abstractmethod
    def nextChallenge(self) -> None:
        """Start the next GeoChallenge"""
        pass
    
    @abstractmethod
    def getHint(self) -> None:
        """Get a hint for the current challenge"""
        pass
    
    @abstractmethod
    def showGameStats(self) -> str:
        """Show comprehensive game statistics"""
        pass

    @abstractmethod
    def increaseContinentRadius( self ) -> None:
        """Increase continent radius by 0.01"""
        pass

    @abstractmethod
    def decreaseContinentRadius( self ) -> None:
        """Decrease continent radius by 0.01"""
        pass

    @property
    @abstractmethod
    def continentRadius( self ) -> float:
        """Get current continent radius"""
        pass

    @property
    @abstractmethod
    def rotationIncrement(self) -> int:
        """Get current rotation increment in degrees"""
        pass

    @property
    @abstractmethod
    def globeRotationX(self) -> int:
        """Get globe X rotation in degrees"""
        pass

    @property
    @abstractmethod
    def globeRotationY(self) -> int:
        """Get globe Y rotation in degrees"""
        pass

    @property
    @abstractmethod
    def globeRotationZ(self) -> int:
        """Get globe Z rotation in degrees"""
        pass

    @property
    @abstractmethod
    def taskManager(self) -> Any:
        """Get task manager for scheduling tasks"""
        pass
