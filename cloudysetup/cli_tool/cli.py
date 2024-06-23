import click
import requests
import json
import time
import random
import boto3
from dotenv import load_dotenv
import os
from rich.console import Console
from rich.progress import Progress

load_dotenv()
console = Console()

BASE_URL = os.getenv("BASE_URL")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("message")
@click.option("--monitor", is_flag=True, help="Monitor the resource creation status")
@click.option("--profile", default=None, help="AWS CLI profile to use")
def message(message, monitor, profile):
    """Send a message to the FastAPI server and get a response"""

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    credentials = session.get_credentials()
    headers = {
        "aws-access-key": credentials.access_key,
        "aws-secret-key": credentials.secret_key,
        "aws-session-token": credentials.token if credentials.token else "",
    }

    # TODO - Add progress bar
    # Refactor this to include a progress bar and handle crud operations
    console.print("[bold yellow]Do you want to proceed with the request?[/bold yellow]")
    confirm = click.confirm("Please confirm")
    if confirm:
        response = requests.post(
            f"{BASE_URL}/message", json={"message": message}, headers=headers
        )
        if response.status_code == 200:
            console.print("[bold green]Request submitted successfully.[/bold green]")
            formatted_response = json.dumps(response.json(), indent=4)
            console.print_json(formatted_response)
            if monitor:
                request_token = response.json()["details"]["ProgressEvent"][
                    "RequestToken"
                ]
                console.print(
                    f"Monitoring status for request token: [bold]{request_token}[/bold]"
                )
                monitor_status(request_token, headers)
        else:
            console.print(
                f"[bold red]Error: {response.status_code} - {response.json().get('detail')}[/bold red]"
            )
    else:
        console.print("[bold red]Request cancelled.[/bold red]")
        return


def monitor_status(request_token, headers):
    """Monitor the status of the resource creation"""
    console.print("[bold blue]Checking resource creation status...[/bold blue]")
    max_attempts = 10
    wait_time = 2  # Initial wait time in seconds
    max_wait_time = 60 * 15  # Maximum wait time in seconds

    for attempt in range(max_attempts):
        click.echo(request_token)
        response = requests.post(
            f"{BASE_URL}/resource-status",
            json={"request_token": request_token},
            headers=headers,
        )
        if response.status_code == 200:
            details = response.json().get("details", {})
            status = details.get("ProgressEvent", {}).get("OperationStatus")
            if status in ["SUCCESS", "FAILED"]:
                console.print(f"Operation Status: [bold]{status}[/bold]")
                formatted_details = json.dumps(details, indent=4)
                console.print_json(formatted_details)
                break
            else:
                console.print(
                    f"Current Status: [yellow]{status}[/yellow]. Checking again in {wait_time} seconds..."
                )
        else:
            console.print(
                f"[bold red]Error: {response.status_code} - {response.json().get('detail')}[/bold red]"
            )

        # Exponential backoff with jitter
        time.sleep(wait_time)
        wait_time = min(max_wait_time, wait_time * 2 + random.uniform(0, 1))

    else:
        console.print(
            "[bold red]Max attempts reached. Please check the status manually.[/bold red]"
        )


@cli.command()
@click.argument("request_token")
@click.option("--profile", default=None, help="AWS CLI profile to use")
def monitor(request_token, profile):
    """Monitor the status of the resource creation using a request token"""

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    credentials = session.get_credentials()
    headers = {
        "aws-access-key": credentials.access_key,
        "aws-secret-key": credentials.secret_key,
        "aws-session-token": credentials.token if credentials.token else "",
    }

    monitor_status(request_token, headers)


if __name__ == "__main__":
    cli(prog_name="CloudySetup")
