#!/usr/bin/env python3
"""
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill
ALL RIGHTS RESERVED.

PROPRIETARY AND CONFIDENTIAL
This is commercial software. Unauthorized copying, modification,
distribution, or use is strictly prohibited.
"""

"""
DNA-Key Authentication System - User-Friendly CLI Tool

Easy-to-use command-line interface for all DNA-Key operations.
"""

import json
import os
import sys

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

console = Console()

# Default API URL
API_URL = os.getenv("DNAKEY_API_URL", "http://localhost:8000")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🔷 DNA-Key Authentication System CLI

    User-friendly command-line interface for DNA-Key operations.

    Examples:
        dnakey enroll user@example.com
        dnakey auth dna-abc123
        dnakey list
        dnakey revoke dna-abc123
    """
    pass


@cli.command()
@click.argument("subject_id")
@click.option(
    "--level",
    "-l",
    default="enhanced",
    type=click.Choice(["standard", "enhanced", "maximum", "government"]),
    help="Security level",
)
@click.option("--type", "-t", default="human", type=click.Choice(["human", "device", "service"]), help="Subject type")
@click.option("--mfa/--no-mfa", default=True, help="Require MFA")
@click.option("--biometric/--no-biometric", default=False, help="Require biometric")
@click.option("--days", "-d", default=365, help="Validity in days")
def enroll(subject_id, level, type, mfa, biometric, days):
    """
    Enroll a new DNA key.

    Creates a unique DNA authentication key with specified security level.

    Examples:
        dnakey enroll user@example.com
        dnakey enroll device-001 --type device --level maximum
        dnakey enroll admin@company.com --level government --mfa --biometric
    """
    console.print("\n[bold cyan]🔷 DNA Key Enrollment[/bold cyan]\n")

    # Show configuration
    config_table = Table(show_header=False, box=None)
    config_table.add_row("[cyan]Subject ID:[/cyan]", subject_id)
    config_table.add_row("[cyan]Type:[/cyan]", type)
    config_table.add_row("[cyan]Security Level:[/cyan]", level.upper())
    config_table.add_row("[cyan]MFA Required:[/cyan]", "✓ Yes" if mfa else "✗ No")
    config_table.add_row("[cyan]Biometric:[/cyan]", "✓ Yes" if biometric else "✗ No")
    config_table.add_row("[cyan]Validity:[/cyan]", f"{days} days")
    console.print(config_table)

    if not Confirm.ask("\n[yellow]Proceed with enrollment?[/yellow]"):
        console.print("[red]Enrollment cancelled.[/red]")
        return

    # Enroll
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("[cyan]Generating DNA key...", total=None)

        try:
            response = requests.post(
                f"{API_URL}/api/v1/enroll",
                json={
                    "subject_id": subject_id,
                    "subject_type": type,
                    "security_level": level,
                    "validity_days": days,
                    "mfa_required": mfa,
                    "biometric_required": biometric,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    progress.update(task, completed=True)
                    console.print("\n[bold green]✓ Enrollment Successful![/bold green]\n")

                    # Display results
                    result_panel = Panel(
                        f"[cyan]Key ID:[/cyan] {data['key_id']}\n"
                        f"[cyan]Created:[/cyan] {data['created_at']}\n"
                        f"[cyan]Expires:[/cyan] {data['expires_at']}\n"
                        f"[cyan]Visual Seed:[/cyan] {data['visual_seed'][:32]}...",
                        title="[bold]DNA Key Generated[/bold]",
                        border_style="green",
                    )
                    console.print(result_panel)

                    # Save to file
                    filename = f"{subject_id.replace('@', '_').replace('.', '_')}_dna_key.json"
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=2)

                    console.print(f"\n[dim]Key saved to: {filename}[/dim]")
                    console.print("[dim]View in 3D: http://localhost:3000[/dim]\n")
                else:
                    console.print(f"[bold red]✗ Error:[/bold red] {data.get('error_message')}")
            else:
                console.print(f"[bold red]✗ HTTP Error:[/bold red] {response.status_code}")
        except requests.exceptions.ConnectionError:
            console.print("[bold red]✗ Connection Error:[/bold red] Is the API server running?")
            console.print("[dim]Start with: python -m server.api.main[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("key_id")
def auth(key_id):
    """
    Authenticate with DNA key.

    Performs challenge-response authentication.

    Examples:
        dnakey auth dna-abc123
        dnakey auth $(cat my_key.json | jq -r .key_id)
    """
    console.print("\n[bold cyan]🔐 DNA Key Authentication[/bold cyan]\n")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        # Step 1: Get challenge
        task = progress.add_task("[cyan]Requesting challenge...", total=None)

        try:
            response = requests.post(f"{API_URL}/api/v1/challenge", json={"key_id": key_id})

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    progress.update(task, description="[green]Challenge received")

                    console.print("\n[bold green]✓ Challenge Generated[/bold green]")
                    console.print(f"[dim]Challenge ID: {data['challenge_id']}[/dim]")
                    console.print(f"[dim]Expires: {data['expires_at']}[/dim]\n")

                    console.print("[yellow]In production, you would:[/yellow]")
                    console.print("  1. Sign the challenge with your DNA key")
                    console.print("  2. Submit signature to /api/v1/authenticate")
                    console.print("  3. Receive session token\n")

                    console.print(f"[cyan]Challenge:[/cyan] {data['challenge'][:64]}...\n")

                    # Save challenge for manual signing
                    with open("challenge.json", "w") as f:
                        json.dump(data, f, indent=2)
                    console.print("[dim]Challenge saved to: challenge.json[/dim]\n")
                else:
                    console.print(f"[bold red]✗ Error:[/bold red] {data.get('error_message')}")
            else:
                console.print(f"[bold red]✗ HTTP Error:[/bold red] {response.status_code}")
        except Exception as e:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")


@cli.command()
@click.option("--all", "-a", is_flag=True, help="Show all keys including revoked")
def list(all):
    """
    List enrolled DNA keys.

    Shows all enrolled keys with their status.

    Examples:
        dnakey list
        dnakey list --all
    """
    console.print("\n[bold cyan]📋 Enrolled DNA Keys[/bold cyan]\n")

    try:
        # Note: This would require admin auth in production
        response = requests.get(f"{API_URL}/api/v1/admin/keys", headers={"Authorization": "Bearer demo-token"})

        if response.status_code == 200:
            data = response.json()
            keys = data.get("keys", [])

            if not keys:
                console.print("[yellow]No keys found.[/yellow]\n")
                return

            # Filter revoked if needed
            if not all:
                keys = [k for k in keys if not k.get("is_revoked")]

            # Create table
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Key ID", style="cyan")
            table.add_column("Type")
            table.add_column("Created")
            table.add_column("Expires")
            table.add_column("Segments", justify="right")
            table.add_column("Status")

            for key in keys:
                status = "[red]REVOKED[/red]" if key.get("is_revoked") else "[green]ACTIVE[/green]"
                table.add_row(
                    key["key_id"][:20] + "...",
                    key.get("subject_type", "N/A"),
                    key["created"][:10] if key.get("created") else "N/A",
                    key["expires"][:10] if key.get("expires") else "N/A",
                    str(key.get("segment_count", 0)),
                    status,
                )

            console.print(table)
            console.print(f"\n[dim]Total: {len(keys)} keys[/dim]\n")
        else:
            console.print("[yellow]Admin endpoint requires authentication.[/yellow]")
            console.print("[dim]Login to admin dashboard first.[/dim]\n")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("key_id")
@click.option(
    "--reason",
    "-r",
    default="unspecified",
    type=click.Choice(
        [
            "key_compromise",
            "affiliation_changed",
            "superseded",
            "cessation_of_operation",
            "privilege_withdrawn",
            "unspecified",
        ]
    ),
    help="Revocation reason",
)
@click.option("--notes", "-n", help="Additional notes")
def revoke(key_id, reason, notes):
    """
    Revoke a DNA key.

    Immediately invalidates a DNA key.

    Examples:
        dnakey revoke dna-abc123
        dnakey revoke dna-abc123 --reason key_compromise --notes "Suspected breach"
    """
    console.print("\n[bold red]⚠️  DNA Key Revocation[/bold red]\n")

    console.print(f"[yellow]Key ID:[/yellow] {key_id}")
    console.print(f"[yellow]Reason:[/yellow] {reason}")
    if notes:
        console.print(f"[yellow]Notes:[/yellow] {notes}")

    if not Confirm.ask("\n[bold red]Are you sure you want to revoke this key?[/bold red]"):
        console.print("[green]Revocation cancelled.[/green]")
        return

    try:
        response = requests.post(
            f"{API_URL}/api/v1/admin/revoke",
            headers={"Authorization": "Bearer demo-token"},
            json={"key_id": key_id, "reason": reason, "revoked_by": "cli-user", "notes": notes},
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                console.print("\n[bold green]✓ Key Revoked Successfully[/bold green]")
                console.print(f"[dim]Revoked at: {data.get('revoked_at')}[/dim]\n")
            else:
                console.print(f"[bold red]✗ Error:[/bold red] {data.get('error_message')}")
        else:
            console.print(f"[bold red]✗ HTTP Error:[/bold red] {response.status_code}")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("key_id")
def view(key_id):
    """
    View DNA key in 3D.

    Opens web browser to view the DNA key visualization.

    Examples:
        dnakey view dna-abc123
    """
    import webbrowser

    console.print("\n[bold cyan]🌀 Opening 3D Viewer...[/bold cyan]\n")
    url = f"http://localhost:3000?key_id={key_id}"

    console.print(f"[cyan]URL:[/cyan] {url}")

    if Confirm.ask("[yellow]Open in browser?[/yellow]", default=True):
        webbrowser.open(url)
        console.print("[green]✓ Browser opened[/green]\n")
    else:
        console.print("[dim]Copy the URL above to view manually.[/dim]\n")


@cli.command()
def stats():
    """
    Show system statistics.

    Displays enrollment, authentication, and revocation statistics.

    Examples:
        dnakey stats
    """
    console.print("\n[bold cyan]📊 System Statistics[/bold cyan]\n")

    try:
        response = requests.get(f"{API_URL}/api/v1/admin/stats", headers={"Authorization": "Bearer demo-token"})

        if response.status_code == 200:
            data = response.json()

            # Create stats table
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column(style="cyan bold", justify="right")
            table.add_column()

            table.add_row("Enrolled Keys:", str(data.get("enrolled_keys", 0)))
            table.add_row("Active Challenges:", str(data.get("active_challenges", 0)))
            table.add_row("Revoked Keys:", str(data.get("revoked_keys", 0)))
            table.add_row("CRL Version:", str(data.get("crl_version", 0)))

            panel = Panel(table, title="[bold]DNA-Key System Stats[/bold]", border_style="cyan")
            console.print(panel)
            console.print()
        else:
            console.print("[yellow]Admin endpoint requires authentication.[/yellow]\n")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")


@cli.command()
def health():
    """
    Check system health.

    Verifies API server is running and operational.

    Examples:
        dnakey health
    """
    console.print("\n[bold cyan]🏥 System Health Check[/bold cyan]\n")

    try:
        response = requests.get(f"{API_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()

            console.print("[bold green]✓ System Operational[/bold green]")
            console.print(f"[dim]Version: {data.get('version')}[/dim]")
            console.print(f"[dim]Timestamp: {data.get('timestamp')}[/dim]\n")

            # Services status
            services = data.get("services", {})
            table = Table(show_header=True, header_style="bold")
            table.add_column("Service")
            table.add_column("Status")

            for service, status in services.items():
                status_text = "[green]●[/green] Online" if status == "online" else "[red]●[/red] Offline"
                table.add_row(service.title(), status_text)

            console.print(table)
            console.print()
        else:
            console.print(f"[bold red]✗ System Unhealthy[/bold red] (HTTP {response.status_code})\n")
    except requests.exceptions.ConnectionError:
        console.print("[bold red]✗ Cannot Connect to API Server[/bold red]")
        console.print("[yellow]Is the server running?[/yellow]")
        console.print("[dim]Start with: python -m server.api.main[/dim]\n")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {str(e)}\n")


@cli.command()
def start():
    """
    Start DNA-Key system (backend and frontend).

    Launches both API server and web interface.

    Examples:
        dnakey start
    """
    console.print("\n[bold cyan]🚀 Starting DNA-Key System...[/bold cyan]\n")

    import subprocess
    import time

    # Start backend
    console.print("[cyan]Starting backend API server...[/cyan]")
    backend = subprocess.Popen(
        [sys.executable, "-m", "server.api.main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    time.sleep(2)

    # Check if backend started
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            console.print("[green]✓ Backend started successfully[/green]\n")
        else:
            console.print("[red]✗ Backend failed to start[/red]\n")
            return
    except Exception:
        console.print("[red]✗ Backend not responding[/red]\n")
        return

    # Start frontend
    console.print("[cyan]Starting frontend web server...[/cyan]")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"], cwd="web/frontend", stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    time.sleep(3)

    console.print("[green]✓ Frontend starting...[/green]\n")

    # Show URLs
    panel = Panel(
        "[bold]DNA-Key System Started![/bold]\n\n"
        "[cyan]Backend API:[/cyan] http://localhost:8000\n"
        "[cyan]API Docs:[/cyan] http://localhost:8000/api/docs\n"
        "[cyan]Web Interface:[/cyan] http://localhost:3000\n"
        "[cyan]Admin Dashboard:[/cyan] http://localhost:3000/admin\n\n"
        "[dim]Press Ctrl+C to stop[/dim]",
        border_style="green",
    )
    console.print(panel)

    try:
        backend.wait()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping services...[/yellow]")
        backend.terminate()
        frontend.terminate()
        console.print("[green]✓ Stopped[/green]\n")


@cli.command()
@click.option("--api", default="http://localhost:8000", help="API URL")
def config(api):
    """
    Configure CLI settings.

    Set API URL and other configuration options.

    Examples:
        dnakey config --api http://localhost:8000
        dnakey config --api https://api.example.com
    """
    console.print("\n[bold cyan]⚙️  Configuration[/bold cyan]\n")

    # Save to environment or config file
    console.print(f"[cyan]API URL:[/cyan] {api}")

    # Create config file
    config_data = {"api_url": api}
    with open(os.path.expanduser("~/.dnakey_config.json"), "w") as f:
        json.dump(config_data, f, indent=2)

    console.print("[green]✓ Configuration saved[/green]\n")
    console.print(f"[dim]Set in shell: export DNAKEY_API_URL={api}[/dim]\n")


@cli.command()
def version():
    """Show version information."""
    console.print("\n[bold cyan]DNA-Key Authentication System[/bold cyan]")
    console.print("[dim]Version 1.0.0[/dim]")
    console.print("[dim]Built with ❤️  using Tron-inspired design[/dim]\n")


if __name__ == "__main__":
    cli()
