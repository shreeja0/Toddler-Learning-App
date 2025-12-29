"""
Learning Engine
Core adaptive learning logic with repeat-then-switch behavior.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from app.engine.session_state import SessionState


@dataclass
class LearningItem:
    """Represents a single learning item."""
    name: str
    properties: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningItem':
        """Create LearningItem from dictionary."""
        name = data.get('name', 'Unknown')
        properties = {k: v for k, v in data.items() if k != 'name'}
        return cls(name=name, properties=properties)


class LearningEngine:
    """
    Manages adaptive learning progression logic.
    
    Core Behavior:
    1. Display an item N times (repeat_count)
    2. After N repetitions, advance to next item
    3. When reaching the end, loop back to the beginning
    4. No failure states or time limits
    
    Design Principles:
    - Functional approach with immutable state
    - No global state
    - Testable logic separation
    """
    
    def __init__(self, items: List[Dict[str, Any]], repeat_count: int = 3):
        """
        Initialize learning engine with content.
        
        Args:
            items: List of learning items (from YAML config)
            repeat_count: Number of times to repeat each item before advancing
            
        Raises:
            ValueError: If items is empty or repeat_count < 1
        """
        if not items:
            raise ValueError("Learning engine requires at least one item")
        if repeat_count < 1:
            raise ValueError("Repeat count must be at least 1")
        
        self.items = [LearningItem.from_dict(item) for item in items]
        self.repeat_count = repeat_count
        self.state = SessionState()
    
    def get_current_item(self) -> LearningItem:
        """
        Get the current learning item.
        
        Returns:
            Current LearningItem based on session state
        """
        # Use modulo for automatic wrap-around
        index = self.state.current_item_index % len(self.items)
        return self.items[index]
    
    def get_progress_info(self) -> Dict[str, Any]:
        """
        Get detailed progress information for UI rendering.
        
        Returns:
            Dictionary containing:
                - item: Current LearningItem
                - repeat_number: Current repeat (1-indexed for display)
                - total_repeats: Required repeats per item
                - item_index: Current item index
                - total_items: Total number of items
                - progress_percentage: Overall progress (0-100)
        """
        item = self.get_current_item()
        
        return {
            'item': item,
            'repeat_number': self.state.current_repeat_count + 1,
            'total_repeats': self.repeat_count,
            'item_index': self.state.current_item_index,
            'total_items': len(self.items),
            'progress_percentage': (
                (self.state.current_repeat_count + 1) / self.repeat_count * 100
            )
        }
    
    def handle_interaction(self) -> Dict[str, Any]:
        """
        Process user interaction and advance learning state.
        
        This is the core learning progression logic:
        1. Record the interaction
        2. Increment repeat count
        3. Check if current item's repeats are complete
        4. If complete, advance to next item (with wrap-around)
        5. Return updated progress info
        
        Returns:
            Updated progress information dictionary
        """
        # Record interaction
        self.state = self.state.with_interaction()
        self.state = self.state.with_repeat()
        
        # Check if we've completed required repeats
        if self.state.current_repeat_count >= self.repeat_count:
            # Advance to next item
            next_index = self.state.current_item_index + 1
            
            # Wrap around to beginning if at end
            if next_index >= len(self.items):
                next_index = 0
            
            self.state = self.state.with_next_item(next_index)
        
        return self.get_progress_info()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for current session.
        
        Returns:
            Dictionary with session metrics
        """
        return {
            'total_interactions': self.state.total_interactions,
            'items_completed': self.state.items_completed,
            'current_item_index': self.state.current_item_index,
            'session_duration_seconds': self.state.get_session_duration(),
            'total_items': len(self.items),
            'repeat_count': self.repeat_count
        }
    
    def reset(self) -> None:
        """Reset learning session to beginning."""
        self.state = SessionState()

