"""
Abstract interface for Globe Application
Defines the contract that any globe application must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IGlobeApplication(ABC):
    """Abstract interface for Globe Application implementations"""

    @abstractmethod
    def zoom_in(self) -> None:
        """Move camera closer to globe center"""
        pass

    @abstractmethod
    def zoom_out(self) -> None:
        """Move camera further from globe center"""
        pass

    @abstractmethod
    def reset_view(self) -> None:
        """Reset camera position and globe rotation to default"""
        pass

    @abstractmethod
    def rotate_up(self) -> None:
        """Rotate globe up by increment amount"""
        pass

    @abstractmethod
    def rotate_down(self) -> None:
        """Rotate globe down by increment amount"""
        pass

    @abstractmethod
    def rotate_left(self) -> None:
        """Rotate globe left by increment amount"""
        pass

    @abstractmethod
    def rotate_right(self) -> None:
        """Rotate globe right by increment amount"""
        pass

    @abstractmethod
    def increase_rotation_increment(self) -> None:
        """Increase rotation increment by 1 degree"""
        pass

    @abstractmethod
    def decrease_rotation_increment(self) -> None:
        """Decrease rotation increment by 1 degree"""
        pass

    @abstractmethod
    def set_preset_view(self, index: int) -> None:
        """Set the globe to a specific preset view"""
        pass

    @property
    @abstractmethod
    def rotation_increment(self) -> int:
        """Get current rotation increment in degrees"""
        pass

    @property
    @abstractmethod
    def globe_rotation_x(self) -> int:
        """Get globe X rotation in degrees"""
        pass

    @property
    @abstractmethod
    def globe_rotation_y(self) -> int:
        """Get globe Y rotation in degrees"""
        pass

    @property
    @abstractmethod
    def globe_rotation_z(self) -> int:
        """Get globe Z rotation in degrees"""
        pass

    @property
    @abstractmethod
    def taskManager(self) -> Any:
        """Get task manager for scheduling tasks"""
        pass
