import os
import sys
import time
import math
import re
import threading
import subprocess
import urllib.request
import json
import socket
import platform
import shutil
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

VERSION = "1.0.0"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/398001/C3l0.cc-Tools/main/C3l0.cc%20Tools.py"

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    ascii_art = pyfiglet.figlet_format("C3l0.cc Tools", font="slant")
    console.print(Align.center(f"[bold white]{ascii_art}[/bold white]"))
    console.print(Align.center(f"[dim white]v{VERSION} | System & Network Utility Suite[/dim white]\n"))

def parse_version(v_str):
    try:
        return tuple(int(x) for x in v_str.strip().split("."))
    except ValueError:
        return (0, 0, 0)

def extract_remote_version(source_code):
    match = re.search(r'^VERSION\s*=\s*["\']([^"\']+)["\']', source_code, re.MULTILINE)
    if match:
        return match.group(1)
    return None

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

def render_loading_frame(progress_pct, tick, status_str="INITIALISIERE C3L0.CC ENVIRONMENT..."):
    width = console.size.width
    height = console.size.height - 1

    ascii_banner = pyfiglet.figlet_format("C3l0.cc Tools", font="slant").splitlines()
    banner_height = len(ascii_banner)
    banner_width = max(len(line) for line in ascii_banner)

    bar_width = 44
    filled = int((progress_pct / 100) * bar_width)
    bar_str = f"[{'█' * filled}{'░' * (bar_width - filled)}] {progress_pct:3.0f}%"

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
SUBTITLE_STR = f"v{VERSION} | System & Network Utility Suite"

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
    state = {
        "target_progress": 10,
        "status": "INITIALISIERE C3L0.CC ENVIRONMENT...",
        "needs_update": False,
        "done": False
    }

    def updater_worker():
        script_path = os.path.abspath(__file__)
        if not os.path.exists(script_path):
            state["status"] = "LOKALE DATEI NICHT GEFUNDEN..."
            state["target_progress"] = 100
            time.sleep(0.4)
            state["done"] = True
            return

        state["target_progress"] = 25
        state["status"] = "VERBINDE MIT GITHUB REPOSITORY..."

        try:
            cache_buster_url = f"{GITHUB_RAW_URL}?t={int(time.time())}"
            req = urllib.request.Request(
                cache_buster_url,
                headers={
                    "User-Agent": "C3l0-Updater",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                }
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                state["target_progress"] = 45
                state["status"] = "LADE VERSIONSINFORMATIONEN..."

                total_size = int(response.headers.get("Content-Length", 0))
                chunks = []
                downloaded = 0

                while True:
                    chunk = response.read(1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        dl_pct = min(25, int((downloaded / total_size) * 25))
                        state["target_progress"] = 45 + dl_pct

                remote_source = b"".join(chunks).decode("utf-8")
                state["target_progress"] = 70
                state["status"] = "VERGLEICHE VERSIONEN..."

                remote_version = extract_remote_version(remote_source)
                if remote_version and parse_version(remote_version) > parse_version(VERSION):
                    state["status"] = f"UPDATE GEFUNDEN (v{VERSION} -> v{remote_version})..."
                    state["target_progress"] = 85

                    with open(script_path, "w", encoding="utf-8", newline="\n") as f:
                        f.write(remote_source)
                        f.flush()
                        os.fsync(f.fileno())

                    state["needs_update"] = True
                    state["target_progress"] = 100
                    state["status"] = f"UPDATE AUF v{remote_version} ABGESCHLOSSEN! STARTE NEU..."
                else:
                    state["target_progress"] = 90
                    state["status"] = f"VERSION AKTUELL (LOKAL v{VERSION} | GITHUB v{remote_version or '?'})"
                    time.sleep(0.6)
                    state["target_progress"] = 100
                    state["status"] = "BEREIT."

        except Exception as e:
            state["target_progress"] = 90
            state["status"] = f"UPDATE-FEHLER: {type(e).__name__}"
            time.sleep(0.8)
            state["target_progress"] = 100
            state["status"] = "BEREIT."

        time.sleep(0.35)
        state["done"] = True

    worker = threading.Thread(target=updater_worker, daemon=True)
    worker.start()

    displayed_progress = 0

    with Live(render_loading_frame(0, tick, state["status"]), console=console, refresh_per_second=25, screen=True) as live:
        while not state["done"] or displayed_progress < 100:
            if displayed_progress < state["target_progress"]:
                step = max(1, (state["target_progress"] - displayed_progress) // 3)
                displayed_progress = min(state["target_progress"], displayed_progress + step)

            live.update(render_loading_frame(displayed_progress, tick, state["status"]))
            tick += 1
            time.sleep(0.04)

    if state["needs_update"]:
        clear_screen()
        if os.name == 'nt':
            subprocess.Popen([sys.executable, os.path.abspath(__file__)])
            sys.exit(0)
        else:
            os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)])

    return tick

def module_ip_lookup():
    print_banner()
    console.print(Align.center(Panel("[bold white]IP LOOKUP MODULE[/bold white]", border_style="dim white", width=60)))
    target = Prompt.ask("\n[bold white]Ziel-IP / Domain (Enter für eigene IP)[/bold white]", default="")
    
    url = f"https://ipinfo.io/{target.strip()}/json" if target.strip() else "https://ipinfo.io/json"
    
    with console.status("[bold white]Frage IP-Informationen ab...[/bold white]", spinner="dots"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "C3l0-Tool"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            data = {"error": str(e)}

    table = Table(show_header=False, border_style="dim white", width=60)
    table.add_column("Key", style="bold white")
    table.add_column("Value", style="white")

    if "error" in data:
        table.add_row("Status", f"[bold white]Fehler: {data['error']}[/bold white]")
    else:
        table.add_row("IP-Adresse", data.get("ip", "N/A"))
        table.add_row("Stadt", data.get("city", "N/A"))
        table.add_row("Region", data.get("region", "N/A"))
        table.add_row("Land", data.get("country", "N/A"))
        table.add_row("Standort", data.get("loc", "N/A"))
        table.add_row("Organisation", data.get("org", "N/A"))
        table.add_row("Hostname", data.get("hostname", "N/A"))

    console.print()
    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_port_scanner():
    print_banner()
    console.print(Align.center(Panel("[bold white]PORT SCANNER MODULE[/bold white]", border_style="dim white", width=60)))
    target = Prompt.ask("\n[bold white]Ziel-Host (IP oder Domain)[/bold white]", default="127.0.0.1")
    
    common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]
    port_names = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 
        80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 443: "HTTPS", 
        445: "SMB", 3306: "MySQL", 3389: "RDP", 8080: "HTTP-Proxy"
    }

    table = Table(show_header=True, header_style="bold white", border_style="dim white", width=60)
    table.add_column("Port", style="bold white", justify="center", width=10)
    table.add_column("Dienst", style="white", width=25)
    table.add_column("Status", style="dim white", justify="center")

    console.print()
    with console.status(f"[bold white]Scanne {target}...[/bold white]", spinner="dots"):
        results = []
        for port in common_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.4)
                result = s.connect_ex((target, port))
                s.close()
                status = "OFFEN" if result == 0 else "GESCHLOSSEN"
                results.append((port, port_names.get(port, "Unbekannt"), status))
            except Exception:
                results.append((port, port_names.get(port, "Unbekannt"), "FEHLER"))

    for port, service, status in results:
        status_display = "[bold white]OFFEN[/bold white]" if status == "OFFEN" else "[dim white]GESCHLOSSEN[/dim white]"
        table.add_row(str(port), service, status_display)

    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_system_info():
    print_banner()
    console.print(Align.center(Panel("[bold white]SYSTEM INFO MODULE[/bold white]", border_style="dim white", width=60)))
    
    table = Table(show_header=False, border_style="dim white", width=60)
    table.add_column("Eigenschaft", style="bold white")
    table.add_column("Wert", style="white")

    table.add_row("Betriebssystem", f"{platform.system()} {platform.release()}")
    table.add_row("OS Version", platform.version())
    table.add_row("Architektur", platform.machine())
    table.add_row("Computername", platform.node())
    table.add_row("Python Version", platform.python_version())
    table.add_row("Prozessor", platform.processor() or "N/A")
    table.add_row("CPU Kerne (Logical)", str(os.cpu_count()))

    try:
        total, used, free = shutil.disk_usage("/")
        table.add_row("Speicher (Gesamt)", f"{total // (2**30)} GB")
        table.add_row("Speicher (Frei)", f"{free // (2**30)} GB")
    except Exception:
        pass

    console.print()
    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_webhook_sender():
    print_banner()
    console.print(Align.center(Panel("[bold white]DISCORD WEBHOOK SENDER[/bold white]", border_style="dim white", width=60)))
    
    webhook_url = Prompt.ask("\n[bold white]Webhook URL[/bold white]")
    message = Prompt.ask("[bold white]Nachrichtentext[/bold white]")
    
    if not webhook_url.startswith("http"):
        console.print(Align.center("\n[bold white]Fehler: Ungültige Webhook URL![/bold white]"))
        Prompt.ask("\n[dim white]Drücke Enter um fortzufahren[/dim white]")
        return

    payload = json.dumps({"content": message}).encode("utf-8")
    
    with console.status("[bold white]Sende Nachricht...[/bold white]", spinner="dots"):
        try:
            req = urllib.request.Request(
                webhook_url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "C3l0-Tool"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in [200, 204]:
                    console.print(Align.center("\n[bold white]Nachricht erfolgreich gesendet![/bold white]"))
                else:
                    console.print(Align.center(f"\n[bold white]Fehler: HTTP Status {response.status}[/bold white]"))
        except Exception as e:
            console.print(Align.center(f"\n[bold white]Fehler beim Senden: {e}[/bold white]"))

    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def main():
    tick = boot_sequence()
    while True:
        choice, tick = interactive_menu(tick)

        if choice in ["01", "1"]:
            module_ip_lookup()
        elif choice in ["02", "2"]:
            module_port_scanner()
        elif choice in ["03", "3"]:
            module_system_info()
        elif choice in ["04", "4"]:
            module_webhook_sender()
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
