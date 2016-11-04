import os
import click


class Test(object):
	"""docstring for Test"""
	def __init__(self, arg):
		super(Test, self).__init__()
		self.arg = arg
		
	@click.command()
	@click.option('--abs', default=False, help='is absolute path or not,default in current path')
	def command():
		click.echo('shittttttttt')

if __name__ == '__main__':
    Test.command()