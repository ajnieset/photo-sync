import pathlib
import sys
import threading
import time
import json
import datetime

import click

from app.services.google_photos import PhotosService
from server import start_server, value_holder

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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
        PhotosService.login(creds_file_location)
    except Exception:
        click.secho("ERROR: Login Failed", fg="red", err=True)
        sys.exit(1)

    click.echo("Waiting for user to login.....\n")

    # Wait for 60 seconds polling every half second
    for _ in range(60 * 2):
        if value_holder["code"]:
            access_code = value_holder["code"]
            click.echo("Access Code received\n")
            break

        time.sleep(0.5)
    click.echo("Getting Access Token....\n")

    token = PhotosService.get_token(creds_file_location, access_code)

    click.echo("Successfully logged in")

    token = json.loads(token)
    token["created_at"] = datetime.datetime.now().strftime(DATETIME_FORMAT)

    with open(".access_token.json", "w+") as f:
        f.write(json.dumps(token))


@cli.command()
@click.argument("filepath", type=str)
@click.argument("filename", type=str)
def upload(filepath: str, filename: str):
    """Upload file by FILENAME"""
    start_time = datetime.datetime.now()

    with open(".access_token.json", "r") as f:
        access_token = json.loads(f.read())

    created_time = datetime.datetime.strptime(
        access_token["created_at"], DATETIME_FORMAT
    )
    print(created_time)
    expire_time = created_time + datetime.timedelta(seconds=access_token["expires_in"])
    if expire_time < start_time:
        click.echo("Access Code expired checking refresh token")
        return  # TODO: remove after refresh token impl

    refresh_expire_time = created_time + datetime.timedelta(
        seconds=access_token["refresh_token_expires_in"]
    )
    if refresh_expire_time < start_time:
        click.echo("Refresh token expired, please login again")
        return

    # TODO: refresh access token with refresh token

    auth_token = f"{access_token['token_type']} {access_token['access_token']}"

    service = PhotosService(token=auth_token)

    with open(filepath, "rb") as photo:
        upload_code = service.upload_photos(photo.read())

    response = service.create_all(filename, upload_code.decode())
    click.echo(response)

    service.close()


@cli.command()
@click.argument("folder", type=click.Path())
def sync(folder: click.Path):
    """Upload contents of folder"""
    click.echo(f"Uploading files from {folder}")


if __name__ == "__main__":
    cli()
