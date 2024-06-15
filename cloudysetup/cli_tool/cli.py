import click
import requests

BASE_URL = "http://127.0.0.1:8000"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("message")
def message(message):
    """Send a message to the FastAPI server and get a response"""
    response = requests.post(f"{BASE_URL}/message", json={"message": message})
    if response.status_code == 200:
        click.echo(response.json()["message"])
    else:
        click.echo("Error sending message")


if __name__ == "__main__":
    cli(prog_name="CloudySetup")
