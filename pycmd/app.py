#!/usr/bin/env python

import os
import sys

from core.commandCollection import CommandCollection

#append scripts's path
APP_NAME='Pycmd'
SCRIPTS_PATH = os.path.dirname(__file__)+'/../scripts'

sys.path.append(SCRIPTS_PATH)



class App(CommandCollection):
	"""docstring for App"""
	def __init__(self):
		CommandCollection.__init__(self,APP_NAME)

		
	def run(name=None, **attrs):
		'''list command scripts, invoke then
		'''
		for command_name in os.listdir(SCRIPTS_PATH):
			command_module = __import__(command_name+".main")
			print(command_module)
			command_cls = command_name.capitalize()
			group = getattr(command_module, command_cls)
			self.add_source(group)

		if name is None:
			pass
		print(self.sources)

if __name__ == '__main__':
	app = App()
	app.run()