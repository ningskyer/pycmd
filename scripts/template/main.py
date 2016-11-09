import os
import click

@click.group()
def template():
    pass


@template.command()
@click.option('--path', default='default', help='where to save the template, "default" by default')
@click.argument('name')
@click.argument('source')
def add(path, name, source):
	#将name加入到template列表
	#dir拷贝到配置的templates
	pass

@template.command()
@click.argument('name')
def remove(name):
	pass
