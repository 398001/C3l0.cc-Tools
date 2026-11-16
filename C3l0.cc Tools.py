import os
import sys
import time
import math
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.text import Text

if os.name == 'nt':
    import msvcrt
else:
    import select
    import tty
    import termios

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    ascii_art = pyfiglet.figlet_format("C3l0.cc Tools", font="slant")
    console.print(Align.center(f"[bold white]{ascii_art}[/bold white]"))
    console.print(Align.center("[dim white]v1.0.0 | System & Network Utility Suite[/dim white]\n"))

def get_wave_char(x, y, tick):
    t = tick * 0.045
    w1 = math.sin(x * 0.08 + t) * 3.0 + math.cos(y * 0.15 - t * 0.7) * 2.0
    w2 = math.sin((x - y) * 0.06 - t * 1.2) * 2.5
    
    val = (w1 + w2) % 6.0
    
    if val < 0.35:
        slope = math.cos(x * 0.08 + t)
        if slope > 0.35:
            return "/"
        elif slope < -0.35:
            return "\\"
        return "-"
    elif 2.8 < val < 3.1:
        return "~"
    return " "

def build_bg_segment(start_x, length, y, tick):
    return "".join(get_wave_char(start_x + i, y, tick) for i in range(length))

def render_loading_frame(progress_pct, tick):
    width = console.size.width
    height = console.size.height - 1

    ascii_banner = pyfiglet.figlet_format("C3l0.cc Tools", font="slant").splitlines()
    banner_height = len(ascii_banner)
    banner_width = max(len(line) for line in ascii_banner)

    bar_width = 44
    filled = int((progress_pct / 100) * bar_width)
    bar_str = f"[{'█' * filled}{'░' * (bar_width - filled)}] {progress_pct:3.0f}%"
    status_str = "INITIALISIERE C3L0.CC ENVIRONMENT..."

    box_height = banner_height + 4
    start_y = max(0, (height - box_height) // 2)
    banner_start_x = max(0, (width - banner_width) // 2)
    bar_start_x = max(0, (width - len(bar_str)) // 2)
    status_start_x = max(0, (width - len(status_str)) // 2)

    frame = Text()

    for y in range(height):
        line = Text()
        if start_y <= y < start_y + banner_height:
            b_line = ascii_banner[y - start_y].ljust(banner_width)
            left_bg = build_bg_segment(0, banner_start_x, y, tick)
            right_start = banner_start_x + banner_width
            right_len = max(0, width - right_start)
            right_bg = build_bg_segment(right_start, right_len, y, tick)
            
            line.append(left_bg, style="grey27")
            line.append(b_line, style="bold white")
            line.append(right_bg, style="grey27")

        elif y == start_y + banner_height + 1:
            left_bg = build_bg_segment(0, status_start_x, y, tick)
            right_start = status_start_x + len(status_str)
            right_len = max(0, width - right_start)
            right_bg = build_bg_segment(right_start, right_len, y, tick)
            
            line.append(left_bg, style="grey27")
            line.append(status_str, style="dim white")
            line.append(right_bg, style="grey27")

        elif y == start_y + banner_height + 2:
            left_bg = build_bg_segment(0, bar_start_x, y, tick)
            right_start = bar_start_x + len(bar_str)
            right_len = max(0, width - right_start)
            right_bg = build_bg_segment(right_start, right_len, y, tick)
            
            line.append(left_bg, style="grey27")
            line.append(bar_str, style="bold white")
            line.append(right_bg, style="grey27")

        else:
            bg_line = build_bg_segment(0, width, y, tick)
            line.append(bg_line, style="grey27")

        frame.append(line)
        if y < height - 1:
            frame.append("\n")

    return frame

def build_menu_lines():
    table = Table(show_header=True, header_style="bold white", border_style="dim white", width=60)
    table.add_column("ID", style="bold white", justify="center", width=6)
    table.add_column("Modul", style="white")
    table.add_column("Beschreibung", style="dim white")

    table.add_row("01", "IP Lookup", "Öffentliche IP-Informationen abrufen")
    table.add_row("02", "Port Scanner", "Zielhost auf offene Ports prüfen")
    table.add_row("03", "System Info", "Lokale Hardware- & OS-Daten anzeigen")
    table.add_row("04", "Webhook Sender", "Nachrichten an Discord-Webhooks senden")
    table.add_row("00", "Beenden", "Tool schließen")

    temp_console = Console(width=62, record=True)
    temp_console.print(table)
    return temp_console.export_text().splitlines()

MENU_TABLE_LINES = build_menu_lines()
BANNER_LINES = pyfiglet.figlet_format("C3l0.cc Tools", font="slant").splitlines()
SUBTITLE_STR = "v1.0.0 | System & Network Utility Suite"

def render_menu_frame(tick, input_buffer, error_msg=""):
    width = console.size.width
    height = console.size.height - 1

    banner_height = len(BANNER_LINES)
    banner_width = max(len(line) for line in BANNER_LINES)
    table_height = len(MENU_TABLE_LINES)
    table_width = max(len(line) for line in MENU_TABLE_LINES)

    total_height = banner_height + 2 + table_height + 3
    start_y = max(1, (height - total_height) // 2)

    banner_x = max(0, (width - banner_width) // 2)
    subtitle_x = max(0, (width - len(SUBTITLE_STR)) // 2)
    table_x = max(0, (width - table_width) // 2)

    prompt_prefix = "C3l0.cc > "
    prompt_display = f"{prompt_prefix}{input_buffer}_"
    if error_msg:
        prompt_display += f"  ({error_msg})"
    prompt_x = max(0, (width - table_width) // 2)

    frame = Text()

    for y in range(height):
        line = Text()
        if start_y <= y < start_y + banner_height:
            b_line = BANNER_LINES[y - start_y].ljust(banner_width)
            left_bg = build_bg_segment(0, banner_x, y, tick)
            right_start = banner_x + banner_width
            right_bg = build_bg_segment(right_start, max(0, width - right_start), y, tick)
            line.append(left_bg, style="grey27")
            line.append(b_line, style="bold white")
            line.append(right_bg, style="grey27")

        elif y == start_y + banner_height:
            left_bg = build_bg_segment(0, subtitle_x, y, tick)
            right_start = subtitle_x + len(SUBTITLE_STR)
            right_bg = build_bg_segment(right_start, max(0, width - right_start), y, tick)
            line.append(left_bg, style="grey27")
            line.append(SUBTITLE_STR, style="dim white")
            line.append(right_bg, style="grey27")

        elif start_y + banner_height + 2 <= y < start_y + banner_height + 2 + table_height:
            t_idx = y - (start_y + banner_height + 2)
            t_line = MENU_TABLE_LINES[t_idx].ljust(table_width)
            left_bg = build_bg_segment(0, table_x, y, tick)
            right_start = table_x + table_width
            right_bg = build_bg_segment(right_start, max(0, width - right_start), y, tick)
            line.append(left_bg, style="grey27")
            line.append(t_line, style="white")
            line.append(right_bg, style="grey27")

        elif y == start_y + banner_height + 2 + table_height + 1:
            left_bg = build_bg_segment(0, prompt_x, y, tick)
            right_start = prompt_x + len(prompt_display)
            right_bg = build_bg_segment(right_start, max(0, width - right_start), y, tick)
            line.append(left_bg, style="grey27")
            line.append(prompt_prefix, style="bold white")
            line.append(f"{input_buffer}_", style="white")
            if error_msg:
                line.append(f"  ({error_msg})", style="dim white")
            line.append(right_bg, style="grey27")

        else:
            line.append(build_bg_segment(0, width, y, tick), style="grey27")

        frame.append(line)
        if y < height - 1:
            frame.append("\n")

    return frame

def read_key_nonblocking():
    if os.name == 'nt':
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):
                msvcrt.getwch()
                return None
            return ch
        return None
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None

def interactive_menu(start_tick):
    tick = start_tick
    input_buffer = ""
    error_msg = ""
    valid_choices = {"01", "1", "02", "2", "03", "3", "04", "4", "00", "0"}

    old_settings = None
    if os.name != 'nt':
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    try:
        with Live(render_menu_frame(tick, input_buffer, error_msg), console=console, refresh_per_second=20, screen=True) as live:
            while True:
                key = read_key_nonblocking()
                if key is not None:
                    if key == '\x03':
                        raise KeyboardInterrupt
                    elif key in ('\r', '\n'):
                        if input_buffer in valid_choices:
                            return input_buffer, tick
                        else:
                            error_msg = "Ungültige ID"
                            input_buffer = ""
                    elif key in ('\x08', '\x7f'):
                        input_buffer = input_buffer[:-1]
                        error_msg = ""
                    elif key.isprintable() and len(input_buffer) < 4:
                        input_buffer += key
                        error_msg = ""

                live.update(render_menu_frame(tick, input_buffer, error_msg))
                tick += 1
                time.sleep(0.05)
    finally:
        if old_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def boot_sequence():
    clear_screen()
    tick = 0
    with Live(render_loading_frame(0, tick), console=console, refresh_per_second=20, screen=True) as live:
        for step in range(101):
            live.update(render_loading_frame(step, tick))
            tick += 1
            time.sleep(0.04)
    return tick

def run_placeholder_module(name):
    print_banner()
    with console.status(f"[bold white]Starte {name}...[/bold white]", spinner="dots"):
        time.sleep(1.5)
    
    console.print(Align.center(Panel(
        f"[white]Modul [bold]{name}[/bold] wurde erfolgreich geladen.\nHier kommt deine Logik rein.[/white]",
        border_style="white",
        width=60
    )))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def main():
    tick = boot_sequence()
    while True:
        choice, tick = interactive_menu(tick)

        if choice in ["01", "1"]:
            run_placeholder_module("IP Lookup")
        elif choice in ["02", "2"]:
            run_placeholder_module("Port Scanner")
        elif choice in ["03", "3"]:
            run_placeholder_module("System Info")
        elif choice in ["04", "4"]:
            run_placeholder_module("Webhook Sender")
        elif choice in ["00", "0"]:
            clear_screen()
            console.print("[dim white]Session beendet.[/dim white]")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        sys.exit(0)