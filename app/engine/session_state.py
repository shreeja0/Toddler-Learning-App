"""
Session State Management
Tracks learning progress within a session using dataclasses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class SessionState:
    """
    Immutable-style session state tracking for learning sessions.
    
    Attributes:
        current_item_index: Index of the current learning item
        current_repeat_count: Number of times current item has been shown
        total_interactions: Total user interactions in this session
        session_start_time: Timestamp when session began
        items_completed: Number of items fully completed
        metadata: Additional session information
    """
    current_item_index: int = 0
    current_repeat_count: int = 0
    total_interactions: int = 0
    session_start_time: datetime = field(default_factory=datetime.now)
    items_completed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def with_interaction(self) -> 'SessionState':
        """
        Return new state with incremented interaction count.
        
        Returns:
            New SessionState with updated interaction count
        """
        return SessionState(
            current_item_index=self.current_item_index,
            current_repeat_count=self.current_repeat_count,
            total_interactions=self.total_interactions + 1,
            session_start_time=self.session_start_time,
            items_completed=self.items_completed,
            metadata=self.metadata
        )
    
    def with_repeat(self) -> 'SessionState':
        """
        Return new state with incremented repeat count.
        
        Returns:
            New SessionState with updated repeat count
        """
        return SessionState(
            current_item_index=self.current_item_index,
            current_repeat_count=self.current_repeat_count + 1,
            total_interactions=self.total_interactions,
            session_start_time=self.session_start_time,
            items_completed=self.items_completed,
            metadata=self.metadata
        )
    
    def with_next_item(self, new_index: int) -> 'SessionState':
        """
        Return new state advanced to next item.
        
        Args:
            new_index: Index of the next item
            
        Returns:
            New SessionState at next item with reset repeat count
        """
        return SessionState(
            current_item_index=new_index,
            current_repeat_count=0,
            total_interactions=self.total_interactions,
            session_start_time=self.session_start_time,
            items_completed=self.items_completed + 1,
            metadata=self.metadata
        )
    
    def get_session_duration(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now() - self.session_start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session state to dictionary for serialization or display.
        
        Returns:
            Dictionary representation of session state
        """
        return {
            'current_item_index': self.current_item_index,
            'current_repeat_count': self.current_repeat_count,
            'total_interactions': self.total_interactions,
            'session_duration_seconds': self.get_session_duration(),
            'items_completed': self.items_completed,
            'metadata': self.metadata
        }

