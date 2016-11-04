import os
import click


@click.group()
def cli():
    pass

@cli.command
@click.argument('name')
@click.pass_context
def make(ctx, name):
	#scripts directory
	currentPath = sys.argv[0]
	ctx.invoked_subcommand