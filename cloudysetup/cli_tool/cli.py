import click
import requests
import json
import time
import random
import boto3
from dotenv import load_dotenv
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn
from rich.table import Table
from datetime import datetime

load_dotenv()
console = Console()


BASE_URL = os.getenv("BASE_URL")


def find_project_root():
    current_dir = os.path.abspath(os.getcwd())
    while True:
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if current_dir == parent_dir:
            return os.getcwd()
        current_dir = parent_dir


# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = find_project_root()
RESOURCES_DIR = os.path.join(ROOT_DIR, "resources")
STATE_FILE = os.path.join(os.path.expanduser("~"), ".cloudysetup_state.json")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("action", required=False)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to JSON configuration file",
)
@click.option("--profile", default=None, help="AWS CLI profile to use")
def generate(action, profile, config_file):
    """Generate resource configuration and save it to a file."""

    if not action:
        action = click.prompt(
            "Enter the action to perform (e.g. create an S3 bucket, create a DynamoDB table)"
        )

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    credentials = session.get_credentials()
    headers = {
        "aws-access-key": credentials.access_key,
        "aws-secret-key": credentials.secret_key,
        "aws-session-token": credentials.token if credentials.token else "",
    }
    data = {
        "prompt": f"""
            Generate a JSON configuration for AWS Cloud Control API for the operation '{action}'.
            
            - If the operation is 'create', the JSON should include the 'TypeName' and 'Properties' fields.
            - If the operation is 'read', the JSON should include the 'TypeName' and 'Identifier' fields.
            - If the operation is 'update', the JSON should include the 'TypeName', 'Identifier', and 'Properties' fields.
            - If the operation is 'delete', the JSON should include the 'TypeName' and 'Identifier' fields.
            - If the operation is 'list', the JSON should include the 'TypeName' field only.
            
            Additionally, include a 'Metadata' field at the end of the JSON object that specifies the operation type (e.g., create, read, update, list, delete).
            
            After generating the JSON, provide a list of suggestions indicating which placeholder values in the generated fields should be replaced with real values.
        """
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("Generating template..."),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("waiting", total=None)
        response = requests.post(
            f"{BASE_URL}/generate-template", json=data, headers=headers
        )
        progress.update(task, advance=1)

    if response.status_code == 200:
        console.print("[bold green]Configuration generated successfully.[/bold green]")
        generated_template = response.json()["request_data"]
        suggestions = response.json().get("suggestions", [])
        if suggestions:
            console.print("[bold yellow]GenAI suggestions:[/bold yellow]")
            for suggestion in suggestions:
                console.print(f"  - {suggestion}")

        if not os.path.exists(RESOURCES_DIR):
            os.makedirs(RESOURCES_DIR)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        description = action[:25].replace(" ", "_").lower()

        unique_filename = os.path.join(RESOURCES_DIR, f"{description}_{timestamp}.json")
        with open(unique_filename, "w") as f:
            json.dump(generated_template, f, indent=4)

        console.print(
            f"[bold blue]Configuration saved to {os.path.relpath(unique_filename)}[/bold blue]"
        )

    else:
        console.print(
            f"[bold red]Error: {response.status_code} - {response.json().get('detail')}[/bold red]"
        )


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--monitor", is_flag=True, help="Monitor the resource creation status")
@click.option("--profile", default=None, help="AWS CLI profile to use")
def apply(config_file, monitor, profile):
    """Apply the resource configuration to AWS based on the given config file"""

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    credentials = session.get_credentials()
    headers = {
        "aws-access-key": credentials.access_key,
        "aws-secret-key": credentials.secret_key,
        "aws-session-token": credentials.token if credentials.token else "",
    }
    with open(config_file, "r") as f:
        generated_template = json.load(f)

    operation = generated_template.get("Metadata", {}).get("Operation", "").lower()

    # Delete the Metadata field before sending the request
    if "Metadata" in generated_template:
        del generated_template["Metadata"]

    operations = {
        "create": "create-resource",
        "read": "read-resource",
        "update": "update-resource",
        "delete": "delete-resource",
        "list": "list-resource",
    }

    if operation not in operations:
        console.print(
            f"[bold red]Error: Invalid operation type. Supported operations: {', '.join(operations.keys())}[/bold red]"
        )
        return

    operation_endpoint = operations[operation]
    console.print(
        f"[bold yellow]Do you want to proceed with applying the configuration with {operation} operation...?[/bold yellow]"
    )
    confirm = click.confirm("Please confirm")
    if confirm:
        with Progress(
            SpinnerColumn(),
            TextColumn(f"{operation.capitalize()} operation in progress..."),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("waiting", total=None)
            response = requests.post(
                f"{BASE_URL}/{operation_endpoint}",
                json=generated_template,
                headers=headers,
            )
            progress.update(task, advance=1)
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
                monitor_status(request_token, headers, operation)
        else:
            console.print(
                f"[bold red]Error: {response.status_code} - {response.json().get('detail')}[/bold red]"
            )
    else:
        console.print("[bold red]Request cancelled.[/bold red]")
        return


# Refactor this code..
@cli.command()
@click.argument("action", required=False)
@click.option("--interactive", is_flag=True, help="Enter configuration interactively")
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to JSON configuration file",
)
@click.option("--monitor", is_flag=True, help="Monitor the resource creation status")
@click.option("--profile", default=None, help="AWS CLI profile to use")
def resource(action, monitor, profile, interactive, config_file):
    """Handle CRUD operations on resources"""

    if not action:
        action = click.prompt(
            "Enter the action to perform (e.g. create an S3 bucket, create a DynamoDB table)"
        )

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    credentials = session.get_credentials()
    headers = {
        "aws-access-key": credentials.access_key,
        "aws-secret-key": credentials.secret_key,
        "aws-session-token": credentials.token if credentials.token else "",
    }

    # Generate initial configuration from bedrock model
    data = {
        # "prompt": f"{action.capitalize()} configuration in JSON format that is compatible with AWS Cloud Control API. The JSON should include the TypeName and Properties fields"
        "prompt": "Create an SNS topic resource configuration in JSON format that is compatible with AWS Cloud Control API. The JSON should include the TypeName and Properties fields."
    }
    # Add call to the /generate-template path
    response = requests.post(
        f"{BASE_URL}/generate-template", json=data, headers=headers
    )
    formatted_response = json.dumps(response.json(), indent=4)
    console.print_json(formatted_response)
    if response.status_code == 200:
        console.print("[bold green]Configuration generated successfully.[/bold green]")
        generated_template = response.json()["request_data"]
        suggestions = response.json().get("suggestions", [])
        if suggestions:
            console.print("[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in suggestions:
                console.print(f"  - {suggestion}")

        if interactive:
            for key, value in generated_template["Properties"].items():
                user_input = click.prompt(f"{key} [{value}]", default=value)
                generated_template["Properties"][key] = user_input

        # elif condition to accept config file as input as well
    else:
        console.print(
            f"[bold red]Error: {response.status_code} - {response.json().get('detail')}[/bold red]"
        )
        return

    # TODO - Add progress bar
    # Refactor this to include a progress bar and handle crud operations
    console.print("[bold yellow]Do you want to proceed with the request?[/bold yellow]")
    confirm = click.confirm("Please confirm")
    if confirm:
        response = requests.post(
            f"{BASE_URL}/message", json=generated_template, headers=headers
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


def monitor_status(request_token, headers, operation):
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
                display_resource_details(details, operation)
                if status == "FAILED":
                    status_message = details.get("ProgressEvent", {}).get(
                        "StatusMessage"
                    )
                    console.print(
                        f"[bold red]Failure Reason: {status_message}[/bold red]"
                    )
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


def display_resource_details(details, operation):

    table = Table(title="Resource Details")
    table.add_column("Resource ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Resource Type", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Operation", style="blue")

    progress_event = details.get("ProgressEvent", {})
    resource_id = progress_event.get("Identifier", "N/A")
    resource_type = progress_event.get("TypeName", "N/A")
    status = progress_event.get("OperationStatus", "N/A")

    table.add_row(resource_id, resource_type, status, operation)
    console.print(table)


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
