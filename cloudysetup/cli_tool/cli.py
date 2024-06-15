import click


@click.group()
def cli():
    pass


@cli.command()
def hello():
    """Prints Hello World"""
    click.echo("Hello World")


if __name__ == "__main__":
    cli(prog_name="CloudySetup")
