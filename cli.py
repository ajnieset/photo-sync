import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("file", type=click.File("r"))
def upload(file: click.File):
    """Upload file by FILENAME"""
    click.echo(f"Uploading {file.name} ....")


@cli.command()
@click.argument("folder", type=click.Path())
def sync(folder: click.Path):
    """Upload contents of folder"""
    click.echo(f"Uploading files from {folder}")


if __name__ == "__main__":
    cli()
