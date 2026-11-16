import os
import sys
import time
import math
import json
import socket
import platform
import hashlib
import secrets
import string
import msvcrt
import urllib.request
import urllib.error
import pyfiglet
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.text import Text

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def print_banner():
    clear_screen()
    ascii_art = pyfiglet.figlet_format("C3l0.cc Tools", font="slant")
    console.print(Align.center(f"[bold white]{ascii_art}[/bold white]"))
    console.print(Align.center("[dim white]v1.2.0 | Advanced System & Network Utility Suite[/dim white]\n"))

def get_wave_char(x, y, tick):
    t = tick * 0.04
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

def boot_sequence():
    clear_screen()
    with Live(render_loading_frame(0, 0), console=console, refresh_per_second=20, screen=True) as live:
        for step in range(101):
            live.update(render_loading_frame(step, step))
            time.sleep(0.03)

def build_menu_renderable(selected, options, subtitle="v1.2.0 | Advanced System & Network Utility Suite"):
    ascii_art = pyfiglet.figlet_format("C3l0.cc Tools", font="slant")
    
    table = Table(show_header=True, header_style="bold white", border_style="dim white", width=65)
    table.add_column("ID", style="bold white", justify="center", width=6)
    table.add_column("Modul", style="white")
    table.add_column("Beschreibung", style="dim white")

    for idx, (m_id, m_name, m_desc) in enumerate(options):
        if idx == selected:
            table.add_row(
                f"[reverse bold white] {m_id} [/reverse bold white]",
                f"[reverse bold white] {m_name} [/reverse bold white]",
                f"[reverse bold white] {m_desc} [/reverse bold white]"
            )
        else:
            table.add_row(m_id, m_name, m_desc)

    content = Group(
        Align.center(f"[bold white]{ascii_art}[/bold white]"),
        Align.center(f"[dim white]{subtitle}[/dim white]\n"),
        Align.center(table),
        Align.center("\n[dim white][↑/↓] Navigieren  |  [Enter] Auswählen  |  [Ziffer] Direktwahl[/dim white]")
    )
    return content

def interactive_menu():
    options = [
        ("01", "IP Lookup", "Öffentliche IP- & Geo-Informationen abrufen"),
        ("02", "Port Scanner", "Zielhost auf Standard-Ports prüfen"),
        ("03", "System Info", "Lokale Hardware- & OS-Daten anzeigen"),
        ("04", "Discord Tools", "Webhook Sender & Server Destroyer"),
        ("05", "Hash Generator", "Text in MD5, SHA-256 etc. verschlüsseln"),
        ("06", "Passwort Generator", "Sichere Zufallsschlüssel generieren"),
        ("00", "Beenden", "Tool schließen")
    ]
    selected = 0

    with Live(build_menu_renderable(selected, options), console=console, refresh_per_second=30, screen=True) as live:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':
                    arrow = msvcrt.getch()
                    if arrow == b'H':
                        selected = (selected - 1) % len(options)
                    elif arrow == b'P':
                        selected = (selected + 1) % len(options)
                elif key == b'\r':
                    return options[selected][0]
                elif key in b'1234560':
                    char = key.decode()
                    if char == '0':
                        return "00"
                    for idx, opt in enumerate(options):
                        if opt[0].endswith(char):
                            return opt[0]
                
                live.update(build_menu_renderable(selected, options))
            time.sleep(0.01)

def interactive_discord_menu():
    options = [
        ("01", "Webhook Sender", "Nachrichten an Discord-Webhooks senden"),
        ("02", "Server Destroyer", "Bot-gesteuerte Kanal- & Spam-Operation"),
        ("00", "Zurück", "Zum Hauptmenü zurückkehren")
    ]
    selected = 0

    with Live(build_menu_renderable(selected, options, subtitle="v1.2.0 | Discord Utility Sub-Suite"), console=console, refresh_per_second=30, screen=True) as live:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':
                    arrow = msvcrt.getch()
                    if arrow == b'H':
                        selected = (selected - 1) % len(options)
                    elif arrow == b'P':
                        selected = (selected + 1) % len(options)
                elif key == b'\r':
                    return options[selected][0]
                elif key in b'120':
                    char = key.decode()
                    if char == '0':
                        return "00"
                    for idx, opt in enumerate(options):
                        if opt[0].endswith(char):
                            return opt[0]
                
                live.update(build_menu_renderable(selected, options, subtitle="v1.2.0 | Discord Utility Sub-Suite"))
            time.sleep(0.01)

def module_ip_lookup():
    clear_screen()
    console.print(Align.center(Panel("[bold white]IP Lookup & Geo Intelligence[/bold white]", border_style="dim white", width=65)))
    try:
        with console.status("[bold white]Frage IP-Registry ab...[/bold white]", spinner="dots"):
            req = urllib.request.urlopen("https://ipapi.co/json/", timeout=5)
            data = json.loads(req.read().decode())
        
        table = Table(show_header=False, border_style="dim white", width=65)
        table.add_column("Key", style="bold white")
        table.add_column("Value", style="white")
        
        table.add_row("IP-Adresse", data.get("ip", "N/A"))
        table.add_row("Stadt", data.get("city", "N/A"))
        table.add_row("Region", data.get("region", "N/A"))
        table.add_row("Land", data.get("country_name", "N/A"))
        table.add_row("Postleitzahl", data.get("postal", "N/A"))
        table.add_row("Netzwerk / ISP", data.get("org", "N/A"))
        table.add_row("ASN", data.get("asn", "N/A"))
        table.add_row("Zeitzone", data.get("timezone", "N/A"))
        
        console.print(Align.center(table))
    except Exception as e:
        console.print(Align.center(f"[red]Fehler beim Abrufen der IP-Daten: {e}[/red]"))
    
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_port_scanner():
    clear_screen()
    console.print(Align.center(Panel("[bold white]TCP Port Scanner[/bold white]", border_style="dim white", width=65)))
    target = Prompt.ask("[bold white]Ziel-IP oder Hostname eingeben[/bold white]")
    ports = [21, 22, 23, 25, 53, 80, 110, 135, 443, 445, 3306, 3389, 8080, 25565]
    
    table = Table(show_header=True, header_style="bold white", border_style="dim white", width=65)
    table.add_column("Port", style="bold white", justify="center")
    table.add_column("Dienst", style="white")
    table.add_column("Status", style="bold white", justify="center")
    
    with console.status(f"[bold white]Scanne {target}...[/bold white]", spinner="dots"):
        results = []
        for p in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                res = s.connect_ex((target, p))
                s.close()
                status = "OFFEN" if res == 0 else "GESCHLOSSEN"
                results.append((p, status))
            except:
                results.append((p, "FEHLER"))
    
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 
        80: "HTTP", 110: "POP3", 135: "RPC", 443: "HTTPS", 445: "SMB", 
        3306: "MySQL", 3389: "RDP", 8080: "HTTP-Proxy", 25565: "Minecraft"
    }
    for p, status in results:
        style = "bold white" if status == "OFFEN" else "dim white"
        table.add_row(str(p), services.get(p, "Unbekannt"), f"[{style}]{status}[/{style}]")
    
    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_system_info():
    clear_screen()
    console.print(Align.center(Panel("[bold white]Local System Diagnostics[/bold white]", border_style="dim white", width=65)))
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Property", style="bold white")
    table.add_column("Value", style="white")
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        hostname = "Unbekannt"
        local_ip = "Unbekannt"

    table.add_row("Betriebssystem", f"{platform.system()} {platform.release()}")
    table.add_row("Build / Version", platform.version())
    table.add_row("Architektur", platform.architecture()[0])
    table.add_row("Prozessor", platform.processor() or "Unbekannt")
    table.add_row("Hostname", hostname)
    table.add_row("Lokale IP", local_ip)
    table.add_row("Python Version", platform.python_version())
    
    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_webhook_sender():
    clear_screen()
    console.print(Align.center(Panel("[bold white]Discord Webhook Dispatcher[/bold white]", border_style="dim white", width=65)))
    url = Prompt.ask("[bold white]Webhook URL[/bold white]")
    message = Prompt.ask("[bold white]Nachricht[/bold white]")
    
    try:
        payload = json.dumps({"content": message}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 204]:
                console.print(Align.center("\n[bold white]Nachricht erfolgreich versendet.[/bold white]"))
            else:
                console.print(Align.center(f"\n[yellow]Server antwortete mit Status Code: {response.status}[/yellow]"))
    except Exception as e:
        console.print(Align.center(f"\n[red]Fehler beim Senden: {e}[/red]"))
    
    Prompt.ask("\n[dim white]Drücke Enter um zum Menü zurückzukehren[/dim white]")

def module_server_destroyer():
    clear_screen()
    console.print(Align.center(Panel("[bold white]Discord Server Destroyer[/bold white]", border_style="dim white", width=65)))
    token = Prompt.ask("[bold white]Bot Token eingeben[/bold white]")
    guild_id = Prompt.ask("[bold white]Ziel Server ID (Guild ID) eingeben[/bold white]")
    channel_prefix = Prompt.ask("[bold white]Kanal-Namen Präfix[/bold white]", default="c3l0-raid")
    message = Prompt.ask("[bold white]Nachricht für die Kanäle[/bold white]")
    try:
        count = int(Prompt.ask("[bold white]Anzahl der Kanäle[/bold white]", default="20"))
    except:
        count = 20
    
    table = Table(show_header=True, header_style="bold white", border_style="dim white", width=65)
    table.add_column("Aktion", style="bold white")
    table.add_column("Details", style="white")
    table.add_column("Status", style="bold white", justify="center")
    
    headers = {
        "Authorization": f"Bot {token.strip()}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    created_channels = 0
    sent_messages = 0
    
    with console.status("[bold white]Erstelle Kanäle und sende Nachrichten...[/bold white]", spinner="dots"):
        for i in range(1, count + 1):
            try:
                chan_payload = json.dumps({"name": f"{channel_prefix}-{i}", "type": 0}).encode("utf-8")
                req_chan = urllib.request.Request(
                    f"https://discord.com/api/v10/guilds/{guild_id}/channels",
                    data=chan_payload,
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req_chan, timeout=5) as resp:
                    chan_data = json.loads(resp.read().decode())
                    channel_id = chan_data.get("id")
                    created_channels += 1
                    
                    if channel_id and message:
                        msg_payload = json.dumps({"content": message}).encode("utf-8")
                        req_msg = urllib.request.Request(
                            f"https://discord.com/api/v10/channels/{channel_id}/messages",
                            data=msg_payload,
                            headers=headers,
                            method="POST"
                        )
                        with urllib.request.urlopen(req_msg, timeout=5) as msg_resp:
                            if msg_resp.status in [200, 201]:
                                sent_messages += 1
            except Exception:
                pass
            time.sleep(0.1)
            
        table.add_row("Kanal Erstellung", f"{created_channels}/{count} erstellt", "[bold green]ERFOLGREICH[/bold green]")
        table.add_row("Nachrichten Spam", f"{sent_messages} gesendet", "[bold green]ERFOLGREICH[/bold green]")

    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Menü zurückzukehren[/dim white]")

def module_hash_generator():
    clear_screen()
    console.print(Align.center(Panel("[bold white]Cryptographic Hash Generator[/bold white]", border_style="dim white", width=65)))
    text = Prompt.ask("[bold white]Text eingeben[/bold white]")
    
    md5_val = hashlib.md5(text.encode()).hexdigest()
    sha256_val = hashlib.sha256(text.encode()).hexdigest()
    sha512_val = hashlib.sha512(text.encode()).hexdigest()
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Algorithmus", style="bold white")
    table.add_column("Hash", style="white")
    
    table.add_row("MD5", md5_val)
    table.add_row("SHA-256", sha256_val)
    table.add_row("SHA-512", sha512_val)
    
    console.print(Align.center(table))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def module_pass_generator():
    clear_screen()
    console.print(Align.center(Panel("[bold white]Secure Key Generator[/bold white]", border_style="dim white", width=65)))
    
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(24))
    
    console.print(Align.center(Panel(f"[bold white]{password}[/bold white]", title="Generierter Schlüssel", border_style="dim white", width=65)))
    Prompt.ask("\n[dim white]Drücke Enter um zum Hauptmenü zurückzukehren[/dim white]")

def discord_tools_menu():
    while True:
        choice = interactive_discord_menu()
        if choice in ["01", "1"]:
            module_webhook_sender()
        elif choice in ["02", "2"]:
            module_server_destroyer()
        elif choice in ["00", "0"]:
            break

def main():
    hide_cursor()
    try:
        boot_sequence()
        while True:
            choice = interactive_menu()

            if choice in ["01", "1"]:
                module_ip_lookup()
            elif choice in ["02", "2"]:
                module_port_scanner()
            elif choice in ["03", "3"]:
                module_system_info()
            elif choice in ["04", "4"]:
                discord_tools_menu()
            elif choice in ["05", "5"]:
                module_hash_generator()
            elif choice in ["06", "6"]:
                module_pass_generator()
            elif choice in ["00", "0"]:
                clear_screen()
                console.print("[dim white]Session beendet.[/dim white]")
                show_cursor()
                sys.exit(0)
    finally:
        show_cursor()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        show_cursor()
        sys.exit(0)
