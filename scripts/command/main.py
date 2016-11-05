import os
import sys
#TODO install pycmd 
FRAMEWORK_PATH = os.path.dirname(__file__)+'/../..'
sys.path.append(FRAMEWORK_PATH)

from pycmd.app import App
from pycmd.utils import *
from pycmd.decorators import *

class Command(App):
	"""docstring for Command"""
	def __init__(self, arg):
		super(Command, self).__init__()
		self.arg = arg
	
	@command()
	@argument('name')
	def make(ctx, name):
		#scripts directory
		currentPath = sys.argv[0]	
		print('in command makeeeeeeeeeeeeeee')

