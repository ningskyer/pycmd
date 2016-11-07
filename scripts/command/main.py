import os
import sys
#TODO install pycmd 
FRAMEWORK_PATH = os.path.dirname(os.path.abspath(__file__))+'/../..'

sys.path.append(FRAMEWORK_PATH)
from core import Group
from decorators import command, argument,fuck_command


class Command(Group):
	"""docstring for Command"""
	
	@fuck_command()
	def make(self):
		#scripts directory
		currentPath = sys.argv[0]
		print('in command makeeeeeeeeeeeeeee')

# if __name__ == '__main__':
# 	cmd = Command()

# 	cmd()