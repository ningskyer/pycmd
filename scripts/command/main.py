import os
import click

@click.group()
def command():
    pass

@command.command()
@click.argument('package')
def register(package):
	'''register a package to pycmd's scripts
	'''
	path = path.strip()
    # get rid of '\' in header
	path = path.rstrip("\\")
    #  get rid of '\' in footer
	if abs:
        # determin whether the path exists
		isExists = os.path.exists(path)
		if not isExists:
			os.makedirs(path)
	else:
		os.makedirs(os.getcwd() + '/' + path)
