"""
Screen Module
Pygame-based rendering and interaction handling.
"""

import pygame
from typing import Dict, Any, Callable, Optional, Tuple


class Screen:
    """
    Minimal, clean pygame UI for toddler learning.
    
    Responsibilities:
    - Initialize and manage pygame display
    - Render learning content
    - Handle user input (clicks, keyboard)
    - Provide clean event loop integration
    
    Design Principles:
    - No internal state beyond pygame objects
    - Callback-based event handling
    - Configurable through display settings
    """
    
    def __init__(self, display_config: Dict[str, Any]):
        """
        Initialize screen with display configuration.
        
        Args:
            display_config: Display settings from YAML config
        """
        self.config = display_config
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.is_initialized = False
        
        # Extract settings with defaults
        self.bg_color = tuple(self.config.get('background_color', [245, 245, 245]))
        self.text_color = tuple(self.config.get('text_color', [50, 50, 50]))
        self.fullscreen = self.config.get('fullscreen', False)
        self.width = self.config.get('window_width', 1024)
        self.height = self.config.get('window_height', 768)
    
    def initialize(self) -> None:
        """Initialize pygame and create display."""
        pygame.init()
        
        # Create display
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
        
        pygame.display.set_caption("Toddler Learning App")
        
        # Create clock for frame rate control
        self.clock = pygame.time.Clock()
        self.is_initialized = True
    
    def shutdown(self) -> None:
        """Clean up pygame resources."""
        if self.is_initialized:
            pygame.quit()
            self.is_initialized = False
    
    def handle_events(self, 
                     on_click: Callable[[], None],
                     on_quit: Callable[[], None]) -> None:
        """
        Process pygame events and trigger callbacks.
        
        Args:
            on_click: Called when user clicks or presses space/enter
            on_quit: Called when user wants to quit (ESC, Q, or window close)
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_quit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    on_quit()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    on_click()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    on_click()
    
    def render_learning_item(self, progress_info: Dict[str, Any]) -> None:
        """
        Render current learning item with progress indicators.
        
        Args:
            progress_info: Dictionary from LearningEngine.get_progress_info()
        """
        if not self.is_initialized or not self.screen:
            raise RuntimeError("Screen not initialized. Call initialize() first.")
        
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Get screen dimensions
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # Extract progress data
        item = progress_info['item']
        repeat_num = progress_info['repeat_number']
        total_repeats = progress_info['total_repeats']
        
        # Render based on item type
        if 'color' in item.properties:
            self._render_color_item(item, width, height)
        else:
            self._render_generic_item(item, width, height)
        
        # Render progress dots
        self._render_progress_dots(repeat_num, total_repeats, width, height)
        
        # Render instruction text
        self._render_instruction_text(width, height)
        
        # Update display
        pygame.display.flip()
        
        # Maintain frame rate
        if self.clock:
            self.clock.tick(60)
    
    def _render_color_item(self, item: Any, width: int, height: int) -> None:
        """Render a color learning item."""
        color_rgb = tuple(item.properties['color'])
        
        # Calculate circle position and size
        center_x = width // 2
        center_y = height // 2 - 50
        radius = min(width, height) // 5
        
        # Draw colored circle
        pygame.draw.circle(self.screen, color_rgb, (center_x, center_y), radius)
        
        # Draw white border for visibility
        border_width = self.config.get('circle_border_width', 5)
        pygame.draw.circle(
            self.screen, 
            (255, 255, 255),
            (center_x, center_y),
            radius,
            border_width
        )
        
        # Render color name
        font_large = pygame.font.Font(None, 96)
        text = font_large.render(item.name, True, self.text_color)
        text_rect = text.get_rect(centerx=center_x, top=center_y + radius + 40)
        self.screen.blit(text, text_rect)
        
        # Render description if available
        if 'description' in item.properties:
            font_medium = pygame.font.Font(None, 48)
            desc_text = font_medium.render(
                item.properties['description'],
                True,
                self.text_color
            )
            desc_rect = desc_text.get_rect(
                centerx=center_x,
                top=text_rect.bottom + 20
            )
            self.screen.blit(desc_text, desc_rect)
    
    def _render_generic_item(self, item: Any, width: int, height: int) -> None:
        """Fallback rendering for non-color items."""
        center_x = width // 2
        center_y = height // 2
        
        font_large = pygame.font.Font(None, 96)
        text = font_large.render(item.name, True, self.text_color)
        text_rect = text.get_rect(center=(center_x, center_y))
        self.screen.blit(text, text_rect)
    
    def _render_progress_dots(self, 
                              repeat_num: int,
                              total_repeats: int,
                              width: int,
                              height: int) -> None:
        """Render progress indicator dots."""
        dot_radius = 12
        dot_spacing = 35
        total_width = total_repeats * dot_spacing
        start_x = (width - total_width) // 2 + dot_spacing // 2
        y_pos = height - 100
        
        for i in range(total_repeats):
            x_pos = start_x + i * dot_spacing
            
            if i < repeat_num:
                # Filled dot (completed)
                pygame.draw.circle(
                    self.screen,
                    self.text_color,
                    (x_pos, y_pos),
                    dot_radius
                )
            else:
                # Hollow dot (pending)
                pygame.draw.circle(
                    self.screen,
                    self.text_color,
                    (x_pos, y_pos),
                    dot_radius,
                    3
                )
    
    def _render_instruction_text(self, width: int, height: int) -> None:
        """Render instruction text at bottom of screen."""
        font_small = pygame.font.Font(None, 32)
        text = font_small.render(
            "Click anywhere or press SPACE to continue • Press ESC to quit",
            True,
            self.text_color
        )
        text_rect = text.get_rect(centerx=width // 2, bottom=height - 30)
        self.screen.blit(text, text_rect)
    
    def render_welcome_screen(self) -> None:
        """Render welcome screen."""
        if not self.is_initialized or not self.screen:
            raise RuntimeError("Screen not initialized")
        
        self.screen.fill(self.bg_color)
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # Title
        font_large = pygame.font.Font(None, 96)
        title = font_large.render("Toddler Learning", True, self.text_color)
        title_rect = title.get_rect(centerx=width // 2, centery=height // 2 - 60)
        self.screen.blit(title, title_rect)
        
        # Subtitle
        font_medium = pygame.font.Font(None, 56)
        subtitle = font_medium.render(
            "Click to start!",
            True,
            self.text_color
        )
        subtitle_rect = subtitle.get_rect(centerx=width // 2, centery=height // 2 + 60)
        self.screen.blit(subtitle, subtitle_rect)
        
        pygame.display.flip()
    
    def render_summary_screen(self, summary: Dict[str, Any]) -> None:
        """
        Render session summary screen.
        
        Args:
            summary: Session summary from LearningEngine
        """
        if not self.is_initialized or not self.screen:
            return
        
        self.screen.fill(self.bg_color)
        width = self.screen.get_width()
        height = self.screen.get_height()
        
        # Title
        font_large = pygame.font.Font(None, 96)
        title = font_large.render("Great Learning!", True, self.text_color)
        title_rect = title.get_rect(centerx=width // 2, centery=height // 2 - 100)
        self.screen.blit(title, title_rect)
        
        # Statistics
        font_medium = pygame.font.Font(None, 48)
        stats_lines = [
            f"Interactions: {summary.get('total_interactions', 0)}",
            f"Items Completed: {summary.get('items_completed', 0)}",
            f"Time: {summary.get('session_duration_seconds', 0):.0f} seconds"
        ]
        
        y_offset = height // 2
        for line in stats_lines:
            text = font_medium.render(line, True, self.text_color)
            text_rect = text.get_rect(centerx=width // 2, centery=y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 60
        
        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds

