"""
Learning Engine
Core business logic for adaptive learning progression.
"""

from typing import Dict, Any, Optional
from src.config_loader import LearningModule, ConfigLoader
from src.session_state import SessionState, SessionStateManager


class LearningEngine:
    """
    Manages learning progression logic.
    
    Responsibilities:
    - Determines which item to display
    - Handles repeat count logic
    - Advances to next item when appropriate
    - Wraps around to beginning when reaching end
    """
    
    def __init__(self, config_loader: ConfigLoader, session_manager: SessionStateManager):
        """
        Initialize learning engine.
        
        Args:
            config_loader: Configuration loader instance
            session_manager: Session state manager instance
        """
        self.config_loader = config_loader
        self.session_manager = session_manager
        self._current_module: Optional[LearningModule] = None
    
    def start(self, module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new learning session.
        
        Args:
            module_name: Name of module to start (uses default if not specified)
            
        Returns:
            Dictionary containing the first item to display
        """
        # Load module
        if module_name:
            self._current_module = self.config_loader.get_module(module_name)
        else:
            self._current_module = self.config_loader.get_default_module()
        
        # Start session
        self.session_manager.start_session(self._current_module.name)
        
        # Return first item
        return self.get_current_item()
    
    def get_current_item(self) -> Dict[str, Any]:
        """
        Get the current learning item to display.
        
        Returns:
            Dictionary containing:
                - item: The learning item data
                - item_name: Name of the item
                - item_index: Current item index
                - repeat_number: Current repeat number (1-indexed)
                - total_repeats: Total repeats required
                - progress: Progress through current item (0.0 to 1.0)
        """
        session = self.session_manager.get_current_session()
        if not session:
            raise RuntimeError("No active session. Call start() first.")
        
        if not self._current_module:
            raise RuntimeError("No active module loaded")
        
        # Get item from module
        item = self._current_module.get_item(session.current_item_index)
        
        # Calculate progress
        repeat_progress = (session.current_repeat_count + 1) / self._current_module.repeat_count
        
        return {
            'item': item,
            'item_name': item.get('name', 'Unknown'),
            'item_index': session.current_item_index,
            'repeat_number': session.current_repeat_count + 1,
            'total_repeats': self._current_module.repeat_count,
            'progress': min(repeat_progress, 1.0),
            'module_name': self._current_module.display_name,
            'total_items': self._current_module.get_item_count()
        }
    
    def handle_interaction(self) -> Dict[str, Any]:
        """
        Process a user interaction (click).
        
        This is the core progression logic:
        1. Record the interaction
        2. Increment repeat count
        3. Check if we need to advance to next item
        4. Return the next item to display
        
        Returns:
            Dictionary containing the next item to display
        """
        session = self.session_manager.get_current_session()
        if not session:
            raise RuntimeError("No active session. Call start() first.")
        
        if not self._current_module:
            raise RuntimeError("No active module loaded")
        
        # Record interaction
        session.increment_interaction()
        session.increment_repeat()
        
        # Check if we've completed required repeats for current item
        if session.current_repeat_count >= self._current_module.repeat_count:
            # Move to next item
            session.advance_to_next_item()
            
            # Handle wrap-around
            total_items = self._current_module.get_item_count()
            if session.current_item_index >= total_items:
                session.current_item_index = 0  # Loop back to beginning
        
        # Return next item
        return self.get_current_item()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session.
        
        Returns:
            Dictionary with session statistics
        """
        session = self.session_manager.get_current_session()
        if not session:
            return {}
        
        return {
            'module': session.module_name,
            'total_interactions': session.total_interactions,
            'current_item_index': session.current_item_index,
            'session_duration': session.get_session_duration(),
            'items_completed': session.current_item_index if session.current_repeat_count == 0 else session.current_item_index + 1
        }
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset to the beginning of the current module.
        
        Returns:
            Dictionary containing the first item
        """
        session = self.session_manager.get_current_session()
        if not session:
            raise RuntimeError("No active session")
        
        session.current_item_index = 0
        session.reset_repeat_count()
        
        return self.get_current_item()
    
    def stop(self) -> Optional[Dict[str, Any]]:
        """
        Stop the current learning session.
        
        Returns:
            Session summary or None if no active session
        """
        summary = self.get_session_summary()
        self.session_manager.end_session()
        self._current_module = None
        return summary
    
    def is_active(self) -> bool:
        """Check if there's an active learning session."""
        return self.session_manager.has_active_session()

