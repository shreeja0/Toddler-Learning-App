#!/usr/bin/env python3
"""
Toddler Learning App - Main Entry Point
Production-quality adaptive learning application with clean architecture.
"""

import sys
from pathlib import Path
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine import LearningEngine, SessionState
from app.ui import Screen


class ToddlerLearningApp:
    """
    Main application orchestrator.
    
    Coordinates all components:
    - Content loading from YAML
    - Learning engine initialization
    - UI rendering and event handling
    - Application lifecycle management
    
    Design Principles:
    - No global state
    - Clean separation of concerns
    - Testable components
    """
    
    def __init__(self, config_path: str = "app/content/colors.yaml"):
        """
        Initialize application with configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config: dict = {}
        self.engine: LearningEngine = None
        self.screen: Screen = None
        self.is_running = False
    
    def load_config(self) -> bool:
        """
        Load configuration from YAML file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.config_path.exists():
                print(f"Error: Config file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            print(f"✓ Loaded configuration from {self.config_path}")
            return True
            
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in config file: {e}")
            return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize all application components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load config
            if not self.load_config():
                return False
            
            # Extract configuration sections
            items = self.config.get('items', [])
            config_section = self.config.get('config', {})
            display_config = self.config.get('display', {})
            
            if not items:
                print("Error: No learning items found in configuration")
                return False
            
            # Initialize learning engine
            repeat_count = config_section.get('repeat_count', 3)
            self.engine = LearningEngine(items, repeat_count)
            print(f"✓ Initialized learning engine with {len(items)} items")
            
            # Initialize screen
            self.screen = Screen(display_config)
            self.screen.initialize()
            print("✓ Initialized display")
            
            return True
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self) -> int:
        """
        Run the main application loop.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Initialize
            if not self.initialize():
                return 1
            
            # Show welcome screen
            self.screen.render_welcome_screen()
            self._wait_for_start()
            
            if not self.is_running:
                return 0  # User quit from welcome screen
            
            # Main learning loop
            self._run_learning_loop()
            
            # Show summary
            summary = self.engine.get_session_summary()
            self.screen.render_summary_screen(summary)
            
            # Print session summary
            self._print_summary(summary)
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return 0
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.shutdown()
    
    def _wait_for_start(self) -> None:
        """Wait for user to click to begin learning."""
        self.is_running = True
        waiting = True
        
        def on_click():
            nonlocal waiting
            waiting = False
        
        def on_quit():
            nonlocal waiting
            waiting = False
            self.is_running = False
        
        while waiting and self.is_running:
            self.screen.handle_events(on_click, on_quit)
    
    def _run_learning_loop(self) -> None:
        """Execute main learning interaction loop."""
        # Get initial item
        progress_info = self.engine.get_progress_info()
        
        while self.is_running:
            # Render current item
            self.screen.render_learning_item(progress_info)
            
            # Handle events
            interaction_occurred = False
            
            def on_click():
                nonlocal interaction_occurred
                interaction_occurred = True
            
            def on_quit():
                self.is_running = False
            
            self.screen.handle_events(on_click, on_quit)
            
            # Process interaction
            if interaction_occurred:
                progress_info = self.engine.handle_interaction()
    
    def _print_summary(self, summary: dict) -> None:
        """Print session summary to console."""
        print("\n" + "=" * 50)
        print("SESSION SUMMARY")
        print("=" * 50)
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"Items Completed: {summary['items_completed']}")
        print(f"Duration: {summary['session_duration_seconds']:.1f} seconds")
        print(f"Total Items: {summary['total_items']}")
        print(f"Repeat Count: {summary['repeat_count']}")
        print("=" * 50)
    
    def shutdown(self) -> None:
        """Clean up resources."""
        if self.screen:
            self.screen.shutdown()
        print("\nGoodbye! 👋")


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code
    """
    print("=" * 50)
    print("TODDLER LEARNING APP")
    print("Production-Quality Adaptive Learning System")
    print("=" * 50)
    print()
    
    app = ToddlerLearningApp()
    return app.run()


if __name__ == '__main__':
    sys.exit(main())

