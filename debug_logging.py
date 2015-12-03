#DEBUG		Detailed information, typically of interest only when diagnosing problems.
#INFO		Confirmation that things are working as expected.
#WARNING	An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
#ERROR		Due to a more serious problem, the software has not been able to perform some function.
#CRITICAL	A serious error, indicating that the program itself may be unable to continue running.

import colorama
from colorama import Fore

import logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

#FORMAT = Fore.GREEN + "%(levelname)-8s %(filename)-42s:%(lineno)4s - %(funcName)-32s : %(message)s" #http://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file
##FORMAT = "%(levelname)-8s %(filename)-42s:%(lineno)4s - %(funcName)-32s : %(message)s" #http://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file
#FORMAT = Fore.GREEN + "%(levelname)-7s %(lineno)4s %(filename)-20s:%(funcName)-16s : %(message)s" #http://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file

DEBUG_LEVELV_NUM = 9	#http://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/13638084#13638084
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")
def debugv(self, message, *args, **kws):
	# Yes, logger takes its '*args' as 'args'.
	if self.isEnabledFor(DEBUG_LEVELV_NUM):
		self._log(DEBUG_LEVELV_NUM, message, args, **kws) 

logging.Logger.debugv = debugv


ALWAYS_LEVEL_NUM = 100	#http://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/13638084#13638084
logging.addLevelName(ALWAYS_LEVEL_NUM, "ALWAYS")
def always(self, message, *args, **kws):
	# Yes, logger takes its '*args' as 'args'.
	if self.isEnabledFor(ALWAYS_LEVEL_NUM):
		self._log(ALWAYS_LEVEL_NUM, message, args, **kws) 

logging.Logger.always = always




logger = logging.getLogger(__name__)

FORMAT = "%(levelname)-7s %(lineno)4s %(filename)-41s:%(funcName)-23s : %(message)s" + Fore.RESET #http://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file

#http://docs.python.org/3/howto/logging.html
level = ALWAYS_LEVEL_NUM
level = logging.CRITICAL
level = logging.ERROR
level = logging.WARNING #python default level
level = logging.INFO
level = logging.DEBUG
#level = DEBUG_LEVELV_NUM	#debugv



#Level	Numeric value
#ALWAYS		100
#CRITICAL	50
#ERROR		40
#WARNING	30
#INFO		20
#DEBUG		10
#DEBUGV		9
#NOTSET		0

#Logger.setLevel() specifies the lowest-severity log message a logger will handle, where debug is the lowest built-in severity level and critical is the highest built-in severity. 
#For example, if the severity level is INFO, the logger will handle only INFO, WARNING, ERROR, and CRITICAL messages and will ignore DEBUG messages.
#Logger.exception() creates a log message similar to Logger.error(). The difference is that Logger.exception() dumps a stack trace along with it. Call this method only from an exception handler.
#Logger.log() takes a log level as an explicit argument. This is a little more verbose for logging messages than using the log level convenience methods listed above, but this is how to log at custom log levels.

logging.basicConfig(format=FORMAT, level=level)

from functools import wraps
from functools import partial

import sys
import pprint
import traceback
import inspect


def get_parent_function():
#	print(inspect.stack())
	return inspect.stack()[2][3]


def print_traceback():
	ex_type, ex, tb = sys.exc_info()
	traceback.print_tb(tb)
	del tb


def log_prefix(func=None, *, prefix='', return_status='', log_level='DEBUG'):
	if func is None:
		return partial(log_prefix, prefix=prefix, return_status=return_status, log_level=log_level)
	msg = prefix + '[' + func.__qualname__ + '()]'
	@wraps(func)
	def FUNCTION_CALL(*args, **kwargs):
		parent = get_parent_function()

		args_list = []
		for arg in args:
			if isinstance(arg, bytes):
#				arg = arg.encode(encoding='UTF-8') #AttributeError: 'bytes' object has no attribute 'encode'
				arg = arg.decode(encoding='UTF-8') #AttributeError: 'bytes' object has no attribute 'encode'
				args_list.append(arg)

			elif isinstance(arg, str): #unicode
				args_list.append(arg)

			else:
				try:
					args_list.append(pprint.pformat(arg))
				except:
					args_list.append("Unconvertable_Thing_type:" + str(type(arg)))

		args_output_string = ' '.join(pprint.pformat(args_list).split("\n"))

		kwargs_output_string = ' '.join(pprint.pformat(kwargs).split("\n"))


		output_string = msg + ' caller: ' + parent + '()' + ' args:' + args_output_string + kwargs_output_string

#		output_string = ' '.join(output_string.split('\n'))
#		print('output_string:', output_string)

		#Fore.BLACK    Fore.BLUE     Fore.CYAN     Fore.GREEN    Fore.MAGENTA  Fore.RED      Fore.RESET    Fore.WHITE    Fore.YELLOW 

		if log_level == 'DEBUGV':
			logger.debugv(Fore.GREEN + output_string)

		if log_level == 'DEBUG':
			logger.debug(Fore.GREEN + output_string)

		if log_level == 'INFO':
			logger.info(Fore.WHITE + output_string)

		if log_level == 'WARNING':
			logger.warning(Fore.YELLOW + output_string)

		if log_level == 'ERROR':
			logger.error(Fore.RED + output_string)

		if log_level == 'CRITICAL':
			logger.critical(Fore.RED + output_string)

		answer = func(*args, **kwargs)

		if answer == False:
			logger.debugv(Fore.RED + func.__name__ + " returned False")
		else:
			if return_status == True:
				logger.debugv(Fore.YELLOW + func.__name__ + " OK")

		return answer
#		return func(*args, **kwargs)

	return FUNCTION_CALL


