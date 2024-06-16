import click
import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("message")
@click.option("--monitor", is_flag=True, help="Monitor the resource creation status")
def message(message, monitor):
    """Send a message to the FastAPI server and get a response"""
    response = requests.post(f"{BASE_URL}/message", json={"message": message})
    if response.status_code == 200:
        click.echo("Request submitted successfully.")
        formatted_response = json.dumps(response.json(), indent=4)
        click.echo(formatted_response)
        if monitor:
            request_token = response.json()["details"]["ProgressEvent"]["RequestToken"]
            click.echo(f"Monitoring status for request token: {request_token}")
            monitor_status(request_token)
    else:
        click.echo(f"Error: {response.status_code} - {response.json().get('detail')}")


def monitor_status(request_token):
    """Monitor the status of the resource creation"""
    click.echo("Checking resource creation status...")
    max_attempts = 10
    wait_time = 2  # Initial wait time in seconds
    max_wait_time = 60 * 15  # Maximum wait time in seconds

    for attempt in range(max_attempts):
        click.echo(request_token)
        response = requests.post(
            f"{BASE_URL}/resource-status", json={"request_token": request_token}
        )
        if response.status_code == 200:
            details = response.json().get("details", {})
            status = details.get("ProgressEvent", {}).get("OperationStatus")
            if status in ["SUCCESS", "FAILED"]:
                click.echo(f"Operation Status: {status}")
                formatted_details = json.dumps(details, indent=4)
                click.echo(formatted_details)
                break
            else:
                click.echo(
                    f"Current Status: {status}. Checking again in {wait_time} seconds..."
                )
        else:
            click.echo(
                f"Error: {response.status_code} - {response.json().get('detail')}"
            )

        # Exponential backoff with jitter
        time.sleep(wait_time)
        wait_time = min(max_wait_time, wait_time * 2 + random.uniform(0, 1))

    else:
        click.echo("Max attempts reached. Please check the status manually.")


@cli.command()
@click.argument("request_token")
def monitor(request_token):
    """Monitor the status of the resource creation using a request token"""
    monitor_status(request_token)


def hello():
    """Prints Hello World"""
    click.echo("Hello World")


if __name__ == "__main__":
    cli(prog_name="CloudySetup")
