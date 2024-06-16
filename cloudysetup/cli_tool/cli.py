import click
import requests
import json

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
            # monitor_status(request_token)
    else:
        click.echo(f"Error: {response.status_code} - {response.json().get('detail')}")


def monitor_status(request_token):
    click.echo("Checking resource creation status...")
    while True:
        click.echo(request_token)


def hello():
    """Prints Hello World"""
    click.echo("Hello World")


if __name__ == "__main__":
    cli(prog_name="CloudySetup")
