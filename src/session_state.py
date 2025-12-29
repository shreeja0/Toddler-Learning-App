"""
Session State Management
Tracks learning progress within a session.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionState:
    """
    Maintains state for a learning session.
    
    Attributes:
        module_name: Name of the current learning module
        current_item_index: Index of the current item being shown
        current_repeat_count: Number of times current item has been shown
        total_interactions: Total number of user interactions in session
        session_start_time: When the session started
        metadata: Additional session data
    """
    module_name: str
    current_item_index: int = 0
    current_repeat_count: int = 0
    total_interactions: int = 0
    session_start_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def increment_interaction(self) -> None:
        """Record a user interaction."""
        self.total_interactions += 1
    
    def increment_repeat(self) -> None:
        """Increment the repeat count for the current item."""
        self.current_repeat_count += 1
    
    def advance_to_next_item(self) -> None:
        """
        Move to the next item and reset repeat count.
        
        Note: This increments the index but doesn't handle wrapping.
        That logic is in the LearningEngine.
        """
        self.current_item_index += 1
        self.current_repeat_count = 0
    
    def reset_repeat_count(self) -> None:
        """Reset the repeat count to 0."""
        self.current_repeat_count = 0
    
    def get_session_duration(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now() - self.session_start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session state to dictionary (for serialization)."""
        return {
            'module_name': self.module_name,
            'current_item_index': self.current_item_index,
            'current_repeat_count': self.current_repeat_count,
            'total_interactions': self.total_interactions,
            'session_start_time': self.session_start_time.isoformat(),
            'session_duration_seconds': self.get_session_duration(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """Create SessionState from dictionary (for deserialization)."""
        session_start = data.get('session_start_time')
        if isinstance(session_start, str):
            session_start = datetime.fromisoformat(session_start)
        
        return cls(
            module_name=data['module_name'],
            current_item_index=data.get('current_item_index', 0),
            current_repeat_count=data.get('current_repeat_count', 0),
            total_interactions=data.get('total_interactions', 0),
            session_start_time=session_start or datetime.now(),
            metadata=data.get('metadata', {})
        )


class SessionStateManager:
    """Manages session state lifecycle."""
    
    def __init__(self):
        self._current_session: Optional[SessionState] = None
    
    def start_session(self, module_name: str) -> SessionState:
        """
        Start a new learning session.
        
        Args:
            module_name: Name of the module to start
            
        Returns:
            New SessionState instance
        """
        self._current_session = SessionState(module_name=module_name)
        return self._current_session
    
    def get_current_session(self) -> Optional[SessionState]:
        """Get the current active session."""
        return self._current_session
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """
        End the current session and return session summary.
        
        Returns:
            Dictionary with session data, or None if no active session
        """
        if not self._current_session:
            return None
        
        summary = self._current_session.to_dict()
        self._current_session = None
        return summary
    
    def has_active_session(self) -> bool:
        """Check if there's an active session."""
        return self._current_session is not None
    
    def save_session(self, filepath: str) -> None:
        """
        Save current session to file (for future persistence).
        
        Args:
            filepath: Path to save session data
        """
        if not self._current_session:
            raise ValueError("No active session to save")
        
        import json
        with open(filepath, 'w') as f:
            json.dump(self._current_session.to_dict(), f, indent=2)
    
    def load_session(self, filepath: str) -> SessionState:
        """
        Load session from file (for future persistence).
        
        Args:
            filepath: Path to load session data from
            
        Returns:
            Loaded SessionState instance
        """
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self._current_session = SessionState.from_dict(data)
        return self._current_session

