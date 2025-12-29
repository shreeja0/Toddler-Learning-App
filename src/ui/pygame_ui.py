"""
Pygame UI Layer
Handles all rendering and user input for the learning app.
"""

import pygame
import sys
from typing import Dict, Any, Callable, Optional, Tuple
from src.config_loader import ConfigLoader


class PygameUI:
    """
    UI layer using Pygame for rendering.
    
    Responsibilities:
    - Initialize display
    - Render learning content
    - Capture user interactions
    - Provide clean event handling
    """
    
    def __init__(self, config_loader: ConfigLoader):
        """
        Initialize Pygame UI.
        
        Args:
            config_loader: Configuration loader for UI settings
        """
        self.config_loader = config_loader
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.font_large: Optional[pygame.font.Font] = None
        self.font_medium: Optional[pygame.font.Font] = None
        self.font_small: Optional[pygame.font.Font] = None
        self.is_running = False
        
        # UI settings from config
        self.bg_color = config_loader.get_background_color()
        self.text_color = config_loader.get_text_color()
        self.font_size = config_loader.get_font_size()
    
    def initialize(self) -> None:
        """Initialize Pygame and create window."""
        pygame.init()
        
        # Setup display
        if self.config_loader.is_fullscreen():
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            width, height = self.config_loader.get_window_size()
            self.screen = pygame.display.set_mode((width, height))
        
        pygame.display.set_caption("Toddler Learning App")
        
        # Setup clock for frame rate control
        self.clock = pygame.time.Clock()
        
        # Setup fonts
        self.font_large = pygame.font.Font(None, self.font_size)
        self.font_medium = pygame.font.Font(None, self.font_size // 2)
        self.font_small = pygame.font.Font(None, self.font_size // 3)
        
        self.is_running = True
    
    def shutdown(self) -> None:
        """Cleanup and quit Pygame."""
        self.is_running = False
        pygame.quit()
    
    def handle_events(self, on_click: Callable[[], None], 
                      on_quit: Callable[[], None]) -> None:
        """
        Process pygame events.
        
        Args:
            on_click: Callback function to call on mouse click
            on_quit: Callback function to call on quit event
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_quit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    on_quit()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    on_click()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    on_click()
    
    def render_learning_item(self, item_data: Dict[str, Any]) -> None:
        """
        Render a learning item on screen.
        
        Args:
            item_data: Dictionary containing item information from learning engine
        """
        if not self.screen:
            raise RuntimeError("UI not initialized. Call initialize() first.")
        
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Get screen dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        item = item_data['item']
        item_name = item_data['item_name']
        repeat_number = item_data['repeat_number']
        total_repeats = item_data['total_repeats']
        module_name = item_data['module_name']
        
        # Render main content based on item type
        if 'color' in item:
            self._render_color_item(item, item_name, screen_width, screen_height)
        else:
            # Generic rendering for future module types
            self._render_generic_item(item, item_name, screen_width, screen_height)
        
        # Render progress indicator
        self._render_progress_indicator(
            repeat_number, 
            total_repeats, 
            screen_width, 
            screen_height
        )
        
        # Render module name (top of screen)
        self._render_module_name(module_name, screen_width)
        
        # Render instruction text
        instruction_text = self.font_small.render(
            "Click anywhere or press SPACE to continue",
            True,
            self.text_color
        )
        instruction_rect = instruction_text.get_rect(
            centerx=screen_width // 2,
            bottom=screen_height - 20
        )
        self.screen.blit(instruction_text, instruction_rect)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        if self.clock:
            self.clock.tick(60)
    
    def _render_color_item(self, item: Dict[str, Any], item_name: str,
                           screen_width: int, screen_height: int) -> None:
        """Render a color learning item."""
        color_rgb = tuple(item['color'])
        
        # Draw large colored circle in the center
        center_x = screen_width // 2
        center_y = screen_height // 2 - 50
        radius = min(screen_width, screen_height) // 4
        
        pygame.draw.circle(self.screen, color_rgb, (center_x, center_y), radius)
        
        # Add white border for better visibility
        pygame.draw.circle(self.screen, (255, 255, 255), 
                          (center_x, center_y), radius, 5)
        
        # Render color name below the circle
        name_text = self.font_large.render(item_name, True, self.text_color)
        name_rect = name_text.get_rect(
            centerx=center_x,
            top=center_y + radius + 40
        )
        self.screen.blit(name_text, name_rect)
    
    def _render_generic_item(self, item: Dict[str, Any], item_name: str,
                            screen_width: int, screen_height: int) -> None:
        """Render a generic learning item (fallback)."""
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Render item name
        name_text = self.font_large.render(item_name, True, self.text_color)
        name_rect = name_text.get_rect(center=(center_x, center_y))
        self.screen.blit(name_text, name_rect)
        
        # Render hint if available
        if 'audio_hint' in item:
            hint_text = self.font_medium.render(
                item['audio_hint'],
                True,
                self.text_color
            )
            hint_rect = hint_text.get_rect(
                centerx=center_x,
                top=center_y + 80
            )
            self.screen.blit(hint_text, hint_rect)
    
    def _render_progress_indicator(self, repeat_number: int, total_repeats: int,
                                   screen_width: int, screen_height: int) -> None:
        """Render progress dots to show repeat count."""
        dot_radius = 10
        dot_spacing = 30
        total_width = total_repeats * dot_spacing
        start_x = (screen_width - total_width) // 2 + dot_spacing // 2
        y_pos = screen_height - 80
        
        for i in range(total_repeats):
            x_pos = start_x + i * dot_spacing
            
            if i < repeat_number:
                # Filled dot (completed)
                pygame.draw.circle(self.screen, self.text_color, 
                                 (x_pos, y_pos), dot_radius)
            else:
                # Empty dot (not completed)
                pygame.draw.circle(self.screen, self.text_color,
                                 (x_pos, y_pos), dot_radius, 2)
    
    def _render_module_name(self, module_name: str, screen_width: int) -> None:
        """Render module name at top of screen."""
        module_text = self.font_medium.render(
            f"Learning: {module_name}",
            True,
            self.text_color
        )
        module_rect = module_text.get_rect(
            centerx=screen_width // 2,
            top=30
        )
        self.screen.blit(module_text, module_rect)
    
    def render_welcome_screen(self) -> None:
        """Render welcome/loading screen."""
        if not self.screen:
            raise RuntimeError("UI not initialized")
        
        self.screen.fill(self.bg_color)
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Render title
        title_text = self.font_large.render(
            "Toddler Learning App",
            True,
            self.text_color
        )
        title_rect = title_text.get_rect(
            centerx=screen_width // 2,
            centery=screen_height // 2 - 50
        )
        self.screen.blit(title_text, title_rect)
        
        # Render subtitle
        subtitle_text = self.font_medium.render(
            "Click to start learning!",
            True,
            self.text_color
        )
        subtitle_rect = subtitle_text.get_rect(
            centerx=screen_width // 2,
            centery=screen_height // 2 + 50
        )
        self.screen.blit(subtitle_text, subtitle_rect)
        
        pygame.display.flip()
    
    def render_goodbye_screen(self, session_summary: Dict[str, Any]) -> None:
        """
        Render goodbye screen with session summary.
        
        Args:
            session_summary: Dictionary with session statistics
        """
        if not self.screen:
            return
        
        self.screen.fill(self.bg_color)
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Render goodbye message
        goodbye_text = self.font_large.render(
            "Great Learning!",
            True,
            self.text_color
        )
        goodbye_rect = goodbye_text.get_rect(
            centerx=screen_width // 2,
            centery=screen_height // 2 - 100
        )
        self.screen.blit(goodbye_text, goodbye_rect)
        
        # Render session stats
        if session_summary:
            interactions = session_summary.get('total_interactions', 0)
            duration = session_summary.get('session_duration', 0)
            
            stats_text = self.font_medium.render(
                f"Interactions: {interactions} | Time: {int(duration)}s",
                True,
                self.text_color
            )
            stats_rect = stats_text.get_rect(
                centerx=screen_width // 2,
                centery=screen_height // 2
            )
            self.screen.blit(stats_text, stats_rect)
        
        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds

