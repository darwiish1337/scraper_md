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
    return shutil.get_terminal_size((100, 24)).columns


# ---------------------------------------------------------------------------
# Print helpers
# ---------------------------------------------------------------------------

def print_header() -> None:
    """
    Print the branded M-D scraper header with ASCII art.
    Shown once at startup.
    """
    w     = min(terminal_width(), 80)
    bar   = "─" * w

    logo_lines = [
        " ███╗   ███╗      ██████╗ ",
        " ████╗ ████║      ██╔══██╗",
        " ██╔████╔██║      ██║  ██║",
        " ██║╚██╔╝██║      ██║  ██║",
        " ██║ ╚═╝ ██║      ██████╔╝",
        " ╚═╝     ╚═╝      ╚═════╝ "
    ]

    print()
    for line in logo_lines:
        print(style(line.center(w), C.BRED, C.BOLD))
    
    print()
    print(style(" M-D E-Commerce Scraper ".center(w), C.BOLD, C.BWHITE))
    print(style("E-Commerce Data Collection & Intelligence Tool".center(w), C.CYAN))
    print(style("by Mohamed Darwish".center(w), C.DIM, C.WHITE))
    print(style(bar, C.CYAN, C.DIM))
    print()


def print_section(title: str) -> None:
    """Print a section separator with a label."""
    w   = min(terminal_width(), 80)
    pad = max(0, (w - len(title) - 4) // 2)
    print(
        "\n" +
        style(" " * pad + "  " + title + "  " + " " * pad, C.BOLD, C.BBLUE) +
        "\n"
    )


def ok(msg: str) -> None:
    print(style("  ✓  ", C.BGREEN) + msg)


def info(msg: str) -> None:
    print(style("  →  ", C.CYAN) + msg)


def warn(msg: str) -> None:
    print(style("  !  ", C.BYELLOW) + msg)


def error(msg: str) -> None:
    print(style("  ✗  ", C.BRED) + msg)


def dim(msg: str) -> None:
    print(style("     " + msg, C.DIM))


def bold(msg: str) -> None:
    print(style(msg, C.BOLD))


def label_value(label: str, value: str, label_width: int = 22) -> None:
    """Print a key: value line with consistent alignment."""
    l = style(f"  {label:<{label_width}}", C.DIM, C.WHITE)
    v = style(str(value), C.BWHITE)
    print(l + v)


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

    sep = style("  " + "  ".join("─" * w for w in col_widths), C.DIM)
    header_row = "  " + "  ".join(
        style(str(h).ljust(col_widths[i]), C.BOLD, C.CYAN)
        for i, h in enumerate(headers)
    )

    print(sep)
    print(header_row)
    print(sep)

    for row in rows:
        line = "  " + "  ".join(
            str(row[i]).ljust(col_widths[i]) if i < len(row) else " " * col_widths[i]
            for i in range(len(headers))
        )
        print(line)

    print(sep)


class ProgressBar:
    """
    Simple terminal progress bar.

    Usage:
        bar = ProgressBar(total=100, label="Scraping")
        for i in range(100):
            bar.update(i + 1)
        bar.done()
    """

    def __init__(self, total: int, label: str = "Progress", width: int = 40):
        self.total  = max(total, 1)
        self.label  = label
        self.width  = width
        self._last  = -1

    def update(self, current: int, suffix: str = "") -> None:
        pct   = min(current / self.total, 1.0)
        filled = int(self.width * pct)
        pct_int = int(pct * 100)

        if pct_int == self._last and not suffix:
            return
        self._last = pct_int

        bar_fill  = style("█" * filled,            C.BGREEN)
        bar_empty = style("░" * (self.width - filled), C.DIM)
        label_str = style(f"  {self.label:<18}", C.DIM, C.WHITE)
        pct_str   = style(f" {pct_int:>3}%", C.BYELLOW)
        sfx       = style(f"  {suffix}", C.DIM) if suffix else ""

        line = f"\r{label_str} {bar_fill}{bar_empty}{pct_str}{sfx}"
        sys.stdout.write(line)
        sys.stdout.flush()

    def done(self, msg: str = "done") -> None:
        self.update(self.total)
        print(style(f"  {msg}", C.BGREEN))


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
    print()
    print(style(f"  {question}", C.BOLD, C.BWHITE))
    print()

    for i, choice in enumerate(choices, start=1):
        num  = style(f"  [{i}]", C.BBLUE)
        text = style(f"  {choice}", C.WHITE)
        star = style(" (default)", C.DIM) if default is not None and i - 1 == default else ""
        print(f"{num}{text}{star}")

    back_idx = len(choices) + 1
    if show_back:
        print(style(f"  [{back_idx}]", C.BYELLOW) + style("  Back", C.WHITE))

    print()
    default_hint = f" [{default + 1}]" if default is not None else ""
    prompt = style(f"  Enter choice{default_hint}: ", C.CYAN)

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
    Returns a list of selected indices (0-based).
    Empty list if 'Back' is selected.
    """
    print()
    print(style(f"  {question}", C.BOLD, C.BWHITE))
    dim("  Comma-separated numbers, or 'all'")
    print()

    for i, choice in enumerate(choices, start=1):
        print(style(f"  [{i}]", C.BBLUE) + style(f"  {choice}", C.WHITE))

    back_idx = len(choices) + 1
    if show_back:
        print(style(f"  [{back_idx}]", C.BYELLOW) + style("  Back", C.WHITE))
    
    print()
    prompt = style("  Enter choices: ", C.CYAN)

    while True:
        try:
            raw = input(prompt).strip().lower()
            if raw == "all":
                return list(range(len(choices)))
            
            if show_back and raw == str(back_idx):
                return [] # Empty means back

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

    print()
    prompt = style("  Selection: ", C.CYAN)

    while True:
        try:
            raw = input(prompt).strip().lower()
            if raw == "all":
                return list(range(len(choices)))
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            indices = []
            valid = True
            for p in parts:
                try:
                    v = int(p)
                    if 1 <= v <= len(choices):
                        indices.append(v - 1)
                    else:
                        error(f"{v} is out of range.")
                        valid = False
                        break
                except ValueError:
                    error(f"'{p}' is not a number.")
                    valid = False
                    break
            if valid and indices:
                return indices
            if valid:
                error("Select at least one option.")
        except (EOFError, KeyboardInterrupt):
            print()
            raise


def prompt_text(
    question:     str,
    default:      str  = "",
    allow_empty:  bool = False,
) -> str:
    """Prompt for free-text input with an optional default."""
    default_hint = style(f" [{default}]", C.DIM) if default else ""
    prompt = style(f"  {question}{default_hint}: ", C.CYAN)
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
    prompt = style(f"  {question} [{default}]: ", C.CYAN)
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
    hint   = style("[Y/n]" if default else "[y/N]", C.DIM)
    prompt = style(f"  {question} ", C.CYAN) + hint + " "
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
