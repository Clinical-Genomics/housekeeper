"""Initialise HK db from CLI"""
import click


@click.command()
@click.option("--reset", is_flag=True, help="reset database before setting up tables")
@click.option("--force", is_flag=True, help="bypass manual confirmations")
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    store = context.obj["store"]
    existing_tables = store.engine.table_names()
    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg="yellow"), abort=True)
        store.drop_all()
    elif existing_tables:
        click.echo(click.style("Database already exists, use '--reset'", fg="red"))
        context.abort()

    store.create_all()
    message = f"Success! New tables: {', '.join(store.engine.table_names())}"
    click.echo(click.style(message, fg="green"))
