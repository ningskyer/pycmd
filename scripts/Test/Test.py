import os
from decorator import *
# from pycmd.core import Group

class Test():
	
	def __init__(self, *arg):
		super(Test, self).__init__()
		self.arg = arg
		cmds = get_commands(self)
		print('get_commandsssssssssssss')
		print(cmds)

	@group()
	def foo():
		pass

	@foo.command()
	def cmd_fuck():
		print('cmd_fuckkkkkkkkkkkkkkkkkkk')

	@foo.command()
	@option("--f", default=False help="forceeeeeeeeeeeee")
	def cmd_fuck2():
		print('cmd_fuckkkkkkkkkkkkkkkkkkk2')

	# @argument('path', help="pathhhhhhhhhhh")
def get_commands(instance):
	members = dir(instance)
	cmds = []
	for member in members:
		if member.startswith('cmd_'):
			cmds.append(member)

	return cmds




if __name__ == '__main__':
    test =  Test()
    print('all memberssssssssss')
    print(dir(test))
    print(type(test.foo))
    print(test.foo.list_commands())
    print('holyyyyyyyyyyyyyyyy')
    comand = test.foo.get_command('cmd_fuck2')
    print('to invokeeeeeeeeeee')
    print(comand.invoke())
    # test.command()
    # print(locals())
    # print('----------')
    # print(dir(test))
    # print('=============')
    # print(vars(test))
