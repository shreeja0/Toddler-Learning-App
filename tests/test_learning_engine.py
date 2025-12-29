"""
Unit Tests for Learning Engine
Validates core repeat → switch behavior and progression logic.
"""

import pytest
from app.engine import LearningEngine, SessionState


# Test Data
SAMPLE_ITEMS = [
    {'name': 'Red', 'color': [255, 0, 0]},
    {'name': 'Blue', 'color': [0, 0, 255]},
    {'name': 'Green', 'color': [0, 255, 0]}
]


class TestLearningEngineInitialization:
    """Test suite for engine initialization."""
    
    def test_initialization_with_valid_data(self):
        """Test creating engine with valid items and repeat count."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=3)
        
        assert len(engine.items) == 3
        assert engine.repeat_count == 3
        assert engine.state.current_item_index == 0
        assert engine.state.current_repeat_count == 0
    
    def test_initialization_with_empty_items(self):
        """Test that empty items raises ValueError."""
        with pytest.raises(ValueError, match="at least one item"):
            LearningEngine([], repeat_count=3)
    
    def test_initialization_with_invalid_repeat_count(self):
        """Test that repeat_count < 1 raises ValueError."""
        with pytest.raises(ValueError, match="at least 1"):
            LearningEngine(SAMPLE_ITEMS, repeat_count=0)


class TestItemRetrieval:
    """Test suite for getting current item."""
    
    def test_get_current_item_at_start(self):
        """Test getting first item at session start."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        item = engine.get_current_item()
        
        assert item.name == 'Red'
        assert item.properties['color'] == [255, 0, 0]
    
    def test_get_progress_info_structure(self):
        """Test that progress info contains all required fields."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        info = engine.get_progress_info()
        
        assert 'item' in info
        assert 'repeat_number' in info
        assert 'total_repeats' in info
        assert 'item_index' in info
        assert 'total_items' in info
        assert 'progress_percentage' in info
        
        assert info['repeat_number'] == 1  # 1-indexed for display
        assert info['total_repeats'] == 2
        assert info['total_items'] == 3


class TestRepeatBehavior:
    """Test suite for repeat-before-advance logic."""
    
    def test_stays_on_same_item_during_repeats(self):
        """Test that item doesn't change until repeat_count reached."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=3)
        
        # First interaction
        info = engine.handle_interaction()
        assert info['item'].name == 'Red'
        assert info['repeat_number'] == 2
        
        # Second interaction
        info = engine.handle_interaction()
        assert info['item'].name == 'Red'
        assert info['repeat_number'] == 3
    
    def test_advances_after_completing_repeats(self):
        """Test that engine advances to next item after repeat_count."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        
        # Complete repeats for first item
        engine.handle_interaction()  # Red, repeat 2
        info = engine.handle_interaction()  # Should advance to Blue
        
        assert info['item'].name == 'Blue'
        assert info['repeat_number'] == 1
        assert info['item_index'] == 1
    
    def test_interaction_count_increments(self):
        """Test that total interactions are tracked correctly."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        
        engine.handle_interaction()
        assert engine.state.total_interactions == 1
        
        engine.handle_interaction()
        assert engine.state.total_interactions == 2
        
        engine.handle_interaction()
        assert engine.state.total_interactions == 3


class TestWrapAroundBehavior:
    """Test suite for end-of-list wrap-around."""
    
    def test_wraps_to_beginning_after_last_item(self):
        """Test that engine loops back to first item after reaching end."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        
        # Go through all items: 3 items × 2 repeats = 6 interactions
        for _ in range(6):
            info = engine.handle_interaction()
        
        # Should be back at first item
        current_item = engine.get_current_item()
        assert current_item.name == 'Red'
        assert engine.state.current_item_index == 0
    
    def test_multiple_loops(self):
        """Test that engine can loop through items multiple times."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=1)
        
        # First loop
        for expected_name in ['Red', 'Blue', 'Green']:
            info = engine.handle_interaction()
            # After interaction, we're on next item
        
        # Second loop should start back at Red
        current_item = engine.get_current_item()
        assert current_item.name == 'Red'


class TestSessionManagement:
    """Test suite for session state and summary."""
    
    def test_session_summary_structure(self):
        """Test that session summary contains all metrics."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        engine.handle_interaction()
        engine.handle_interaction()
        
        summary = engine.get_session_summary()
        
        assert 'total_interactions' in summary
        assert 'items_completed' in summary
        assert 'current_item_index' in summary
        assert 'session_duration_seconds' in summary
        assert 'total_items' in summary
        assert 'repeat_count' in summary
    
    def test_session_summary_values(self):
        """Test that session summary reports correct values."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        
        # Complete first item (2 repeats)
        engine.handle_interaction()
        engine.handle_interaction()
        
        summary = engine.get_session_summary()
        
        assert summary['total_interactions'] == 2
        assert summary['items_completed'] == 1
        assert summary['current_item_index'] == 1
        assert summary['total_items'] == 3
        assert summary['repeat_count'] == 2
    
    def test_reset_functionality(self):
        """Test that reset returns engine to initial state."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        
        # Make some progress
        engine.handle_interaction()
        engine.handle_interaction()
        engine.handle_interaction()
        
        # Reset
        engine.reset()
        
        assert engine.state.current_item_index == 0
        assert engine.state.current_repeat_count == 0
        assert engine.state.total_interactions == 0
        assert engine.get_current_item().name == 'Red'


class TestProgressCalculation:
    """Test suite for progress percentage calculation."""
    
    def test_progress_at_start(self):
        """Test progress percentage at session start."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=3)
        info = engine.get_progress_info()
        
        # At start: repeat 1 of 3 = 33.33%
        assert info['progress_percentage'] == pytest.approx(33.33, rel=0.01)
    
    def test_progress_at_midpoint(self):
        """Test progress percentage in middle of repeats."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=3)
        
        engine.handle_interaction()  # Now on repeat 2 of 3
        info = engine.get_progress_info()
        
        assert info['progress_percentage'] == pytest.approx(66.67, rel=0.01)
    
    def test_progress_at_completion(self):
        """Test progress percentage at last repeat."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=3)
        
        engine.handle_interaction()  # Repeat 2
        engine.handle_interaction()  # Repeat 3
        info = engine.get_progress_info()
        
        assert info['progress_percentage'] == 100.0


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""
    
    def test_single_item_learning(self):
        """Test engine with only one item."""
        single_item = [{'name': 'OnlyRed', 'color': [255, 0, 0]}]
        engine = LearningEngine(single_item, repeat_count=2)
        
        engine.handle_interaction()
        info = engine.handle_interaction()
        
        # Should loop back to same (only) item
        assert info['item'].name == 'OnlyRed'
        assert info['item_index'] == 0
    
    def test_repeat_count_of_one(self):
        """Test engine with repeat_count=1 (advance every interaction)."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=1)
        
        # Each interaction should advance to next item
        info1 = engine.handle_interaction()
        assert info1['item'].name == 'Blue'
        
        info2 = engine.handle_interaction()
        assert info2['item'].name == 'Green'
        
        info3 = engine.handle_interaction()
        assert info3['item'].name == 'Red'  # Wrapped around
    
    def test_large_repeat_count(self):
        """Test engine with large repeat count."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=10)
        
        # Verify stays on first item for 10 repeats
        for i in range(9):
            info = engine.handle_interaction()
            assert info['item'].name == 'Red'
        
        # 10th interaction should advance
        info = engine.handle_interaction()
        assert info['item'].name == 'Blue'


class TestSessionState:
    """Test suite for SessionState dataclass."""
    
    def test_session_state_immutability(self):
        """Test that state methods return new instances."""
        state1 = SessionState()
        state2 = state1.with_interaction()
        
        assert state1.total_interactions == 0
        assert state2.total_interactions == 1
        assert state1 is not state2
    
    def test_session_state_chaining(self):
        """Test chaining state transformations."""
        state = (SessionState()
                .with_interaction()
                .with_repeat()
                .with_interaction())
        
        assert state.total_interactions == 2
        assert state.current_repeat_count == 1
    
    def test_session_duration_tracking(self):
        """Test that session duration is tracked."""
        state = SessionState()
        import time
        time.sleep(0.1)
        
        duration = state.get_session_duration()
        assert duration >= 0.1


# Integration test
class TestLearningFlowIntegration:
    """Integration tests for complete learning flows."""
    
    def test_complete_learning_cycle(self):
        """Test a complete cycle through all items."""
        engine = LearningEngine(SAMPLE_ITEMS, repeat_count=2)
        
        expected_sequence = [
            ('Red', 2), ('Red', 3),      # First item, 2 repeats (showing 2 and 3)
            ('Blue', 2), ('Blue', 3),    # Second item
            ('Green', 2), ('Green', 3),  # Third item
            ('Red', 2),                  # Loop back to first
        ]
        
        for expected_name, expected_repeat in expected_sequence:
            info = engine.handle_interaction()
            assert info['item'].name == expected_name
            assert info['repeat_number'] == expected_repeat


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
