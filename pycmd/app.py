#!/usr/bin/env python

import os
import sys
import importlib
from core import CommandCollection, Command, Group

#append scripts's path TODO 变量可配置
APP_NAME='Pycmd'
SCRIPTS_PATH = os.path.dirname(__file__)+'/../scripts'

sys.path.append(SCRIPTS_PATH)


class App(CommandCollection):
	"""docstring for App"""
	def __init__(self):
		CommandCollection.__init__(self,APP_NAME)

	def load_scripts(self):
		#load scripts
		for command_name in os.listdir(SCRIPTS_PATH):
			if os.path.isdir(SCRIPTS_PATH+"/"+command_name):
				command_module = importlib.import_module(command_name+".main")
				command_cls = command_name.capitalize()
				group_command = getattr(command_module, command_cls)
				self.add_source(group_command(getattr(group_command, '__name__')))

if __name__ == '__main__':
	app = App()
	app.load_scripts()
	# print(app.sources)

	# for source in app.sources:
		# source.handle()
		# print(source.handle())
		# 
	app()
