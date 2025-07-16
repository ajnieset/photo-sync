import pathlib
import sys
import threading
import time

import click

from app.services.google_photos import PhotosServiceAsync
from server import start_server, value_holder


@click.group()
def cli():
    pass


@cli.command()
def login():
    """Login with Google Account"""

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    time.sleep(1)

    creds_file_location = pathlib.Path("cli-creds.json")
    click.echo("Logging in with Google")

    try:
        PhotosServiceAsync.login(creds_file_location)
    except Exception:
        click.secho("ERROR: Login Failed", fg="red", err=True)
        sys.exit(1)

    click.echo("Waiting for user to login .....")

    # Wait for 60 seconds polling every half second
    for _ in range(60 * 2):
        if value_holder["code"]:
            access_code = value_holder["code"]
            click.echo("Access code received")
            break

        time.sleep(0.5)
    click.echo("Getting Access Token")
    token = PhotosServiceAsync.get_token(creds_file_location, access_code)
    click.echo(token)
    click.echo("Successfully logged in")


@cli.command()
@click.argument("access_code", type=str)
def upload(access_code: str):
    """Upload file by FILENAME"""
    creds_file_location = pathlib.Path("cli-creds.json")

    click.echo(access_code)

    token = PhotosServiceAsync.get_token(creds_file_location, access_code)

    click.echo(token)


@cli.command()
@click.argument("folder", type=click.Path())
def sync(folder: click.Path):
    """Upload contents of folder"""
    click.echo(f"Uploading files from {folder}")


if __name__ == "__main__":
    cli()
