#!/usr/bin/env python3
"""
Toddler Learning App - Main Entry Point

A clean architecture demonstration of a toddler learning application.
Features config-driven content, modular design, and clean separation of concerns.

Usage:
    python main.py [--module MODULE_NAME]

Examples:
    python main.py              # Start with default module (colors)
    python main.py --module colors
"""

import sys
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import ConfigLoader, ConfigurationError
from src.session_state import SessionStateManager
from src.learning_engine import LearningEngine
from src.ui.pygame_ui import PygameUI


class ToddlerLearningApp:
    """
    Main application class.
    
    Orchestrates all components and manages the application lifecycle.
    """
    
    def __init__(self, config_path: str = "config/learning_content.yaml"):
        """
        Initialize the application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        
        # Initialize components
        self.config_loader: ConfigLoader = None
        self.session_manager: SessionStateManager = None
        self.learning_engine: LearningEngine = None
        self.ui: PygameUI = None
        
        self._is_running = False
        self._welcome_shown = False
    
    def initialize(self) -> bool:
        """
        Initialize all application components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load configuration
            print(f"Loading configuration from {self.config_path}...")
            self.config_loader = ConfigLoader(str(self.config_path))
            
            # Initialize session manager
            self.session_manager = SessionStateManager()
            
            # Initialize learning engine
            self.learning_engine = LearningEngine(
                self.config_loader,
                self.session_manager
            )
            
            # Initialize UI
            print("Initializing UI...")
            self.ui = PygameUI(self.config_loader)
            self.ui.initialize()
            
            print("Initialization complete!")
            return True
            
        except ConfigurationError as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Initialization error: {e}", file=sys.stderr)
            return False
    
    def start(self, module_name: str = None) -> None:
        """
        Start the application.
        
        Args:
            module_name: Optional module name to start with
        """
        if not self.ui or not self.learning_engine:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        self._is_running = True
        
        # Show welcome screen
        self.ui.render_welcome_screen()
        self._welcome_shown = True
        
        # Wait for user to click to start
        self._wait_for_start()
        
        # Start learning session
        print(f"Starting learning session...")
        current_item = self.learning_engine.start(module_name)
        
        # Main application loop
        self._run_learning_loop(current_item)
    
    def _wait_for_start(self) -> None:
        """Wait for user to click to start the session."""
        waiting = True
        
        def on_click():
            nonlocal waiting
            waiting = False
        
        def on_quit():
            nonlocal waiting
            waiting = False
            self._is_running = False
        
        while waiting and self._is_running:
            self.ui.handle_events(on_click, on_quit)
    
    def _run_learning_loop(self, current_item: dict) -> None:
        """
        Main learning loop.
        
        Args:
            current_item: Initial item to display
        """
        while self._is_running and self.ui.is_running:
            # Render current learning item
            self.ui.render_learning_item(current_item)
            
            # Handle events
            interaction_occurred = False
            
            def on_click():
                nonlocal interaction_occurred
                interaction_occurred = True
            
            def on_quit():
                self._is_running = False
            
            self.ui.handle_events(on_click, on_quit)
            
            # Process interaction if occurred
            if interaction_occurred:
                current_item = self.learning_engine.handle_interaction()
    
    def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        print("\nShutting down...")
        
        # Get session summary
        if self.learning_engine and self.learning_engine.is_active():
            summary = self.learning_engine.stop()
            
            if summary:
                print("\n=== Session Summary ===")
                print(f"Module: {summary.get('module', 'N/A')}")
                print(f"Total Interactions: {summary.get('total_interactions', 0)}")
                print(f"Duration: {summary.get('session_duration', 0):.1f} seconds")
                print(f"Items Completed: {summary.get('items_completed', 0)}")
                
                # Show goodbye screen
                if self.ui and self.ui.is_running:
                    self.ui.render_goodbye_screen(summary)
        
        # Shutdown UI
        if self.ui:
            self.ui.shutdown()
        
        print("Goodbye!")
    
    def run(self, module_name: str = None) -> int:
        """
        Run the complete application lifecycle.
        
        Args:
            module_name: Optional module name to start with
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Initialize
            if not self.initialize():
                return 1
            
            # Start and run
            self.start(module_name)
            
            # Shutdown
            self.shutdown()
            
            return 0
            
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            self.shutdown()
            return 0
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Adaptive Toddler Learning App",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Start with default module
  %(prog)s --module colors    Start with colors module
  %(prog)s --config custom.yaml  Use custom config file
        """
    )
    
    parser.add_argument(
        '--module',
        type=str,
        default=None,
        help='Learning module to start with (default: from config)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/learning_content.yaml',
        help='Path to configuration file (default: config/learning_content.yaml)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Toddler Learning App 1.0.0'
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Create and run application
    app = ToddlerLearningApp(config_path=args.config)
    return app.run(module_name=args.module)


if __name__ == '__main__':
    sys.exit(main())

