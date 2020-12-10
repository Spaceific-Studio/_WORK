import logging
import sys
import traceback

#logging.basicConfig(filename='C:\example.log',level=logging.DEBUG)
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')


exception_logger = []

# def log_traceback(ex, ex_traceback=None):
#     if ex_traceback is None:
#         ex_traceback = ex.__traceback__
#     tb_lines = [ line.rstrip('\n') for line in
#                  traceback.format_exception(ex.__class__, ex, ex_traceback)]
#     exception_logger.log(tb_lines)


# def get_number():
#     return int('foo')
    
# try:
#     1/0
# except Exception as ex:
# 	#logging.log_traceback("Something wrong with division")
# 	pass

pritn help(sys)

