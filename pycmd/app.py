#!/usr/bin/env python

import os
import sys
import importlib
from click import CommandCollection

#append scripts's path TODO 变量可配置
APP_NAME='pycmd'
SCRIPTS_PATH = os.path.dirname(__file__)+'/../scripts'

sys.path.append(SCRIPTS_PATH)


class App(CommandCollection):
	"""docstring for App"""

	def __init__(self):
		CommandCollection.__init__(self,APP_NAME)
		self.COMMAND_INTER = ':'
		self.COMMAND_FORMAT = 'COMMAND'+self.COMMAND_INTER+'SUBCOMMAND [ARGS]...'
		self.sources_dict = {}

	def load_scripts(self):
		#load scripts
		for command_name in os.listdir(SCRIPTS_PATH):
			if os.path.isdir(SCRIPTS_PATH+"/"+command_name):
				command_cls = command_name.capitalize()
				module_name = command_name+'.main'

				command_module = importlib.import_module(module_name)
				group_command = getattr(command_module, command_name)
				self.add_source(group_command)
				self.sources_dict.update({command_name : group_command})

	def format_commands(self, ctx, formatter):
		"""Extra format methods for multi methods that adds all the commands
        after the options.
        """
		with formatter.section('Commands'):
			for commands in self.list_commands(ctx):
				rows = []
				for subcommand in commands[1]:
					cmd = CommandCollection.get_command(self, ctx, subcommand)
					# What is this, the tool lied about a command.  Ignore it
					if cmd is None:
					    continue

					help = cmd.short_help or ''
					rows.append((subcommand, help))

				if rows:
				    with formatter.section(commands[0]):
				        formatter.write_dl(rows)

	def list_commands(self, ctx):
		cmds = {}
		for source in self.sources:
			cmds.update({source.name : source.list_commands(ctx)})
		return sorted([(k,v) for k, v in cmds.items()])

	def get_command(self, ctx, cmd_name):
		cmd_list = cmd_name.split(self.COMMAND_INTER, 1)

		if cmd_list[0] not in self.sources_dict:
			ctx.fail('No such father command "%s".' %cmds[0])

		if len(cmd_list) > 1:
			for source in self.sources:
				rv = source.get_command(ctx, cmd_list[1])
				if rv is not None:
				    if self.chain:
				        _check_multicommand(self, cmd_list[1], rv)
				    return rv
		else:
			return self.sources_dict[cmd_list[0]]

	def collect_usage_pieces(self, ctx):
		"""Returns all the pieces that go into the usage line and returns
		it as a list of strings.
		"""
		rv = [self.options_metavar, self.COMMAND_FORMAT]
		return rv

if __name__ == '__main__':
	app = App()
	app.load_scripts()

	app(prog_name=APP_NAME)
