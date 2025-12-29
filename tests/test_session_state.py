"""
Unit tests for SessionState and SessionStateManager
"""

import pytest
from src.session_state import SessionState, SessionStateManager


def test_session_state_creation():
    """Test creating a session state."""
    state = SessionState(module_name='colors')
    assert state.module_name == 'colors'
    assert state.current_item_index == 0
    assert state.current_repeat_count == 0
    assert state.total_interactions == 0


def test_increment_interaction():
    """Test incrementing interaction count."""
    state = SessionState(module_name='colors')
    state.increment_interaction()
    assert state.total_interactions == 1
    state.increment_interaction()
    assert state.total_interactions == 2


def test_increment_repeat():
    """Test incrementing repeat count."""
    state = SessionState(module_name='colors')
    state.increment_repeat()
    assert state.current_repeat_count == 1


def test_advance_to_next_item():
    """Test advancing to next item."""
    state = SessionState(module_name='colors')
    state.current_repeat_count = 3
    state.advance_to_next_item()
    assert state.current_item_index == 1
    assert state.current_repeat_count == 0


def test_session_state_to_dict():
    """Test converting session state to dictionary."""
    state = SessionState(module_name='colors')
    state.increment_interaction()
    data = state.to_dict()
    
    assert data['module_name'] == 'colors'
    assert data['total_interactions'] == 1
    assert 'session_duration_seconds' in data


def test_session_state_from_dict():
    """Test creating session state from dictionary."""
    data = {
        'module_name': 'colors',
        'current_item_index': 2,
        'current_repeat_count': 1,
        'total_interactions': 5
    }
    state = SessionState.from_dict(data)
    
    assert state.module_name == 'colors'
    assert state.current_item_index == 2
    assert state.current_repeat_count == 1
    assert state.total_interactions == 5


def test_session_manager_start_session():
    """Test starting a session."""
    manager = SessionStateManager()
    session = manager.start_session('colors')
    
    assert session is not None
    assert session.module_name == 'colors'
    assert manager.has_active_session()


def test_session_manager_end_session():
    """Test ending a session."""
    manager = SessionStateManager()
    manager.start_session('colors')
    summary = manager.end_session()
    
    assert summary is not None
    assert summary['module_name'] == 'colors'
    assert not manager.has_active_session()

