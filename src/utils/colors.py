"""
src/utils/colors.py

Terminal color and styling engine.
All output styling lives here — nothing is hardcoded elsewhere.

Author : M-D (Mohamed Darwish)
"""

import os
import sys
import shutil
import textwrap
from datetime import datetime


# Detect if the terminal supports color
def _supports_color() -> bool:
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        # Windows — enable ANSI if possible
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


USE_COLOR = _supports_color()


class C:
    """
    ANSI escape codes.
    Access via C.RED, C.BOLD, etc.
    All codes resolve to empty strings if color is disabled.
    """

    def _c(code: str) -> str:
        return f"\033[{code}m" if USE_COLOR else ""

    RESET   = _c("0")
    BOLD    = _c("1")
    DIM     = _c("2")
    ITALIC  = _c("3")

    # Foreground colors
    BLACK   = _c("30")
    RED     = _c("31")
    GREEN   = _c("32")
    YELLOW  = _c("33")
    BLUE    = _c("34")
    MAGENTA = _c("35")
    CYAN    = _c("36")
    WHITE   = _c("37")
    GRAY    = _c("90")

    # Bright variants
    BRED    = _c("91")
    BGREEN  = _c("92")
    BYELLOW = _c("93")
    BBLUE   = _c("94")
    BMAGENTA= _c("95")
    BCYAN   = _c("96")
    BWHITE  = _c("97")

    # Custom Colors (Claude Code style)
    PEACH   = "\033[38;5;209m" if USE_COLOR else ""
    
    # Background
    BG_BLACK  = _c("40")
    BG_BLUE   = _c("44")
    BG_CYAN   = _c("46")


def style(text: str, *codes: str) -> str:
    """Wrap text with ANSI codes and reset after."""
    if not USE_COLOR:
        return text
    prefix = "".join(codes)
    return f"{prefix}{text}{C.RESET}"


def terminal_width() -> int:
    """Get the current terminal width, with a safe fallback."""
    try:
        # Get the absolute width. We use the full width to fill the screen.
        return shutil.get_terminal_size((100, 24)).columns
    except Exception:
        return 80


# ---------------------------------------------------------------------------
# Print helpers
# ---------------------------------------------------------------------------

def print_header() -> None:
    """
    Print the branded M-D scraper header in Claude Code style.
    """
    w_term = terminal_width()
    box_w = 40
    indent = _get_menu_indent(box_w)
    
    # Claude-style ASCII (Blocky/Solid)
    logo_lines = [
        "  __  __      _____  ",
        " |  \/  |    |  __ \ ",
        " | \  / |    | |  | |",
        " | |\/| |    | |  | |",
        " | |  | |    | |__| |",
        " |_|  |_|    |_____/ "
    ]

    print()
    # 1. Welcome box
    welcome_text = " * Welcome to M-D "
    top_border = " " * 4 + "╭" + "─" * (len(welcome_text) + 2) + "╮"
    mid_text   = " " * 4 + "│ " + style(welcome_text, C.BOLD, C.BWHITE) + " │"
    bot_border = " " * 4 + "╰" + "─" * (len(welcome_text) + 2) + "╯"
    
    print(indent + top_border)
    print(indent + mid_text)
    print(indent + bot_border)
    print()

    # 2. Big Logo in Peach
    for line in logo_lines:
        print(indent + style(line, C.PEACH, C.BOLD))
    
    print()
    # 3. Footer hint
    print(indent + style(" Press ", C.DIM) + style("Enter", C.BOLD, C.BWHITE) + style(" to continue", C.DIM))
    print()


def print_section(title: str) -> None:
    """Print a simple, clean section title in Claude style."""
    indent = _get_menu_indent(60)
    print("\n" + indent + style(title, C.PEACH, C.BOLD) + "\n")


def ok(msg: str) -> None:
    """Print success message without emoji."""
    indent = _get_menu_indent(len(msg) + 4)
    print(indent + style("DONE", C.PEACH, C.BOLD) + " " + style(msg, C.WHITE))

def info(msg: str) -> None:
    """Print info message without emoji."""
    indent = _get_menu_indent(len(msg) + 4)
    print(indent + style("INFO", C.BCYAN, C.BOLD) + " " + style(msg, C.DIM))

def warn(msg: str) -> None:
    """Print warning message without emoji."""
    indent = _get_menu_indent(len(msg) + 4)
    print(indent + style("WARN", C.BYELLOW, C.BOLD) + " " + style(msg, C.BYELLOW))

def error(msg: str) -> None:
    """Print error message without emoji."""
    indent = _get_menu_indent(len(msg) + 4)
    print(indent + style("FAIL", C.BRED, C.BOLD) + " " + style(msg, C.BRED))


def dim(msg: str) -> None:
    indent = _get_menu_indent(60)
    print(indent + style("     " + msg, C.DIM))


def bold(msg: str) -> None:
    indent = _get_menu_indent(60)
    print(indent + style(msg, C.BOLD))


def label_value(label: str, value: str, label_width: int = 25) -> None:
    """Print a key: value line with consistent alignment and responsive indent."""
    indent = _get_menu_indent(60)
    l = style(f"{label}:", C.DIM, C.WHITE)
    # Align the label within a fixed width for the key part
    key_part = f"{l:<{label_width + 10}}" # +10 to account for ANSI codes in length calculation
    
    # We manually calculate padding because 'style' adds invisible characters
    label_plain = f"{label}:"
    padding = " " * max(0, label_width - len(label_plain))
    
    print(f"{indent}{style(label_plain, C.DIM, C.WHITE)}{padding} {style(str(value), C.BWHITE)}")


def print_table(
    headers: list[str],
    rows:    list[list[str]],
    col_widths: list[int] | None = None,
) -> None:
    """
    Print a simple ASCII table with colored headers.
    col_widths is auto-calculated if not provided.
    """
    if not rows:
        warn("No data to display.")
        return

    if col_widths is None:
        col_widths = [
            max(len(str(h)), max(len(str(r[i])) for r in rows)) + 2
            for i, h in enumerate(headers)
        ]

    table_width = sum(col_widths) + ((len(headers) - 1) * 2)
    indent = _get_menu_indent(table_width)

    sep = indent + style("  ".join("─" * w for w in col_widths), C.DIM)
    header_row = indent + "  ".join(
        style(str(h).ljust(col_widths[i]), C.BOLD, C.CYAN)
        for i, h in enumerate(headers)
    )

    print(sep)
    print(header_row)
    print(sep)

    for row in rows:
        line = indent + "  ".join(
            str(row[i]).ljust(col_widths[i]) if i < len(row) else " " * col_widths[i]
            for i in range(len(headers))
        )
        print(line)

    print(sep)


def _get_menu_indent(content_width: int = 60) -> str:
    """
    Calculate indent to center content. 
    Adjusts dynamically to terminal width for a responsive feel.
    """
    w = terminal_width()
    # On very small screens, use minimal padding
    if w < 60:
        return " " * 2
    # On medium/large screens, center the content but keep a reasonable width
    pad = max(2, (w - content_width) // 2)
    return " " * pad


def prompt_choice(
    question:  str,
    choices:   list[str],
    default:   int | None = None,
    show_back: bool = False,
) -> int:
    """
    Interactive numbered menu. Returns the selected index (0-based).
    Index -1 indicates 'Back' selection.
    """
    longest_choice = max(len(c) for c in choices)
    menu_width = max(len(question), longest_choice + 12)
    indent = _get_menu_indent(menu_width)

    print()
    print(indent + style(f"{question}", C.BOLD, C.BWHITE))
    print()

    for i, choice in enumerate(choices, start=1):
        num  = style(f"[{i}]", C.PEACH) # Use peach for numbers too
        text = style(f"  {choice}", C.WHITE)
        star = style(" (default)", C.DIM) if default is not None and i - 1 == default else ""
        print(f"{indent}{num}{text}{star}")

    back_idx = len(choices) + 1
    if show_back:
        print(indent + style(f"[{back_idx}]", C.BYELLOW) + style("  Back", C.WHITE))

    print()
    default_hint = f" [{default + 1}]" if default is not None else ""
    prompt = indent + style(f"Enter choice{default_hint}: ", C.PEACH)

    while True:
        try:
            raw = input(prompt).strip()
            if raw == "" and default is not None:
                return default
            val = int(raw)
            if 1 <= val <= len(choices):
                return val - 1
            if show_back and val == back_idx:
                return -1
            max_val = back_idx if show_back else len(choices)
            error(f"Enter a number between 1 and {max_val}.")
        except (ValueError, EOFError):
            error("Invalid input.")
        except KeyboardInterrupt:
            print()
            raise


def prompt_multi_choice(
    question: str,
    choices:  list[str],
    show_back: bool = False,
) -> list[int]:
    """
    Interactive multi-select menu.
    User enters comma-separated numbers or 'all'.
    """
    longest_choice = max(len(c) for c in choices)
    menu_width = max(len(question), longest_choice + 12)
    indent = _get_menu_indent(menu_width)

    print()
    print(indent + style(f"{question}", C.BOLD, C.BWHITE))
    print(indent + style("Comma-separated numbers, or 'all'", C.DIM))
    print()

    for i, choice in enumerate(choices, start=1):
        num  = style(f"[{i}]", C.PEACH)
        text = style(f"  {choice}", C.WHITE)
        print(indent + num + text)

    back_idx = len(choices) + 1
    if show_back:
        print(indent + style(f"[{back_idx}]", C.BYELLOW) + style("  Back", C.WHITE))
    
    print()
    prompt = indent + style("Enter choices: ", C.PEACH)

    while True:
        try:
            raw = input(prompt).strip().lower()
            if raw == "all":
                return list(range(len(choices)))
            if show_back and raw == str(back_idx):
                return []
            
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            indices = []
            for p in parts:
                val = int(p)
                if 1 <= val <= len(choices):
                    indices.append(val - 1)
                else:
                    raise ValueError()
            if not indices:
                raise ValueError()
            return sorted(list(set(indices)))
        except (ValueError, EOFError):
            max_val = back_idx if show_back else len(choices)
            error(f"Invalid selection. Use 1-{max_val} or 'all'.")
        except KeyboardInterrupt:
            print()
            raise


def prompt_text(
    question:     str,
    default:      str  = "",
    allow_empty:  bool = False,
) -> str:
    """Prompt for free-text input with an optional default."""
    indent = _get_menu_indent(50)
    default_hint = style(f" [{default}]", C.DIM) if default else ""
    prompt = indent + style(f"{question}{default_hint}: ", C.PEACH)
    print()
    while True:
        try:
            raw = input(prompt).strip()
            if raw == "" and default:
                return default
            if raw or allow_empty:
                return raw
            error("This field cannot be empty.")
        except (EOFError, KeyboardInterrupt):
            print()
            raise


def prompt_int(
    question: str,
    default:  int,
    min_val:  int = 1,
    max_val:  int = 9999,
) -> int:
    """Prompt for an integer within a range."""
    indent = _get_menu_indent(50)
    prompt = indent + style(f"{question} [{default}]: ", C.PEACH)
    print()
    while True:
        try:
            raw = input(prompt).strip()
            if raw == "":
                return default
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            error(f"Enter a number between {min_val} and {max_val}.")
        except ValueError:
            error("Enter a valid number.")
        except (EOFError, KeyboardInterrupt):
            print()
            raise


def confirm(question: str, default: bool = True) -> bool:
    """Y/N confirmation prompt."""
    indent = _get_menu_indent(50)
    hint   = style("[Y/n]" if default else "[y/N]", C.DIM)
    prompt = indent + style(f"{question} ", C.PEACH) + hint + " "
    print()
    while True:
        try:
            raw = input(prompt).strip().lower()
            if raw == "":
                return default
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            error("Enter y or n.")
        except (EOFError, KeyboardInterrupt):
            print()
            raise
