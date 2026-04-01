"""
src/utils/animations.py

Terminal animations and spinners for smooth CLI interactions.
Used to create engaging, professional terminal UI with loading indicators.

Author : M-D (Mohamed Darwish)
"""

import sys
import time
from typing import Optional

from src.utils.colors import C, style


class Spinner:
    """
    Animated spinner for long-running operations.
    
    Example:
        with Spinner("Loading data..."):
            time.sleep(2)
    """
    
    FRAMES = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "dots2": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        "line": ["─", "\\", "|", "/"],
        "pulse": ["◍", "◎", "◍"],
        "bouncing": ["▖", "▘", "▝", "▗"],
    }

    def __init__(self, message: str = "", style_frames: str = "dots", interval: float = 0.1):
        """
        Initialize spinner.
        
        Args:
            message: Text to display while spinning
            style_frames: Animation style (dots, dots2, line, pulse, bouncing)
            interval: Delay between frames in seconds
        """
        self.message = message
        self.frames = self.FRAMES.get(style_frames, self.FRAMES["dots"])
        self.interval = interval
        self._frame = 0
        self._active = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self) -> None:
        """Start the spinner animation."""
        self._active = True
        self._animate()

    def stop(self) -> None:
        """Stop the spinner and clear the line."""
        self._active = False
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def _animate(self) -> None:
        """Internal animation loop."""
        self._frame = 0
        while self._active:
            frame = self.frames[self._frame % len(self.frames)]
            spinner_text = style(frame, C.BCYAN)
            text = f"\r{spinner_text}  {self.message}"
            sys.stdout.write(text)
            sys.stdout.flush()
            time.sleep(self.interval)
            self._frame += 1

    def update_message(self, new_message: str) -> None:
        """Update the spinner message without interrupting animation."""
        self.message = new_message


class TypeWriter:
    """
    Type-writer effect for text output.
    Creates engaging initial display.
    
    Example:
        TypeWriter("Welcome to the scraper!", speed=0.05).write()
    """

    def __init__(self, text: str, speed: float = 0.02, color_code: str = ""):
        """
        Initialize typewriter effect.
        
        Args:
            text: Text to display with typewriter effect
            speed: Delay between characters in seconds
            color_code: ANSI color code to apply
        """
        self.text = text
        self.speed = speed
        self.color_code = color_code

    def write(self) -> None:
        """Execute the typewriter effect."""
        for char in self.text:
            sys.stdout.write(self.color_code + char)
            sys.stdout.flush()
            time.sleep(self.speed)
        print(C.RESET)

    def write_line(self) -> None:
        """Write with typewriter effect and add a newline."""
        self.write()


class FadeIn:
    """
    Fade-in effect for section titles.
    Creates visual polish for major sections.
    
    Example:
        FadeIn("  MAIN MENU  ", duration=0.3).fade()
    """

    def __init__(self, text: str, duration: float = 0.2):
        """
        Initialize fade-in effect.
        
        Args:
            text: Text to fade in
            duration: Total animation duration in seconds
        """
        self.text = text
        self.duration = duration

    def fade(self) -> None:
        """Execute the fade-in effect with opacity levels."""
        opacity_levels = [30, 33, 37, 1]  # ANSI brightness levels
        step_duration = self.duration / len(opacity_levels)
        
        for opacity in opacity_levels:
            code = f"\033[{opacity}m" if opacity < 30 else f"\033[{opacity}m"
            line = f"\r{code}{self.text}\033[0m"
            sys.stdout.write(line)
            sys.stdout.flush()
            time.sleep(step_duration)
        
        sys.stdout.write(f"\r{self.text}\n")


class ProgressAnimation:
    """
    Animated progress meter with smooth transitions.
    Better than simple progress bar for visual appeal.
    
    Example:
        progress = ProgressAnimation(total=100, label="Scraping")
        for i in range(100):
            progress.step()
    """

    def __init__(self, total: int, label: str = "Progress", width: int = 40):
        """
        Initialize progress animation.
        
        Args:
            total: Total steps to complete
            label: Description of operation
            width: Width of progress bar in characters
        """
        self.total = max(total, 1)
        self.current = 0
        self.label = label
        self.width = width

    def step(self, amount: int = 1) -> None:
        """Advance progress by amount steps."""
        self.current = min(self.current + amount, self.total)
        self._render()

    def set_progress(self, current: int) -> None:
        """Set progress to specific value."""
        self.current = min(max(current, 0), self.total)
        self._render()

    def _render(self) -> None:
        """Render the animated progress bar."""
        percentage = self.current / self.total
        filled = int(self.width * percentage)
        empty = self.width - filled
        
        # Create bar with color gradient based on progress
        if percentage < 0.33:
            bar_color = C.BRED
        elif percentage < 0.66:
            bar_color = C.BYELLOW
        else:
            bar_color = C.BGREEN
        
        fill_part = style("█" * filled, bar_color, C.BOLD)
        empty_part = style("░" * empty, C.DIM)
        percent_text = style(f"{int(percentage * 100):>3}%", C.BOLD)
        
        output = f"\r{self.label:20} {fill_part}{empty_part} {percent_text}"
        sys.stdout.write(output)
        sys.stdout.flush()

    def finish(self, message: str = "Done") -> None:
        """Mark progress as complete and show message."""
        self.current = self.total
        self._render()
        print(f"  {style(message, C.BGREEN, C.BOLD)}")


def wait_animation(duration: float, message: str = "Please wait") -> None:
    """
    Show a simple wait animation for given duration.
    
    Args:
        duration: How long to animate in seconds
        message: Text to display during wait
    """
    frames = ["⠇", "⠋", "⠙", "⠸", "⠰", "⠠", "⠰", "⠸", "⠙", "⠋"]
    steps = int(duration / 0.1)
    
    for i in range(steps):
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r{style(frame, C.BCYAN)} {message}")
        sys.stdout.flush()
        time.sleep(0.1)
    
    sys.stdout.write("\r" + " " * (len(message) + 5) + "\r")
    sys.stdout.flush()
