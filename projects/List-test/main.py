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

help(list)
myList = [0,1,2,3,4,5,6,7,8,9]
myStr = "C:\_WORK\PYTHON\CELULAR_AUTOMAT-2D\RNDCA2D9-sequence\interesting\ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\IHJKRN8MQ4ROUG8MJ871LMWY3KOBI4OZRWM953MEKTMJAN8XMVZLTIHJKRN8MQ4ROUG8MJ871LMWY3KOBI4OZRWM953MEKTMJAN8XMVZLT/"
myListStr = [v for i,v in enumerate(myStr)]
for i, v in enumerate(myStr):
    pass
mySliceList = range(0,len(myStr),10)
print "len(myStr) = {0}".format(len(myStr))
print mySliceList
print myListStr
for i, v in enumerate(mySliceList):
    myListStr.pop(v+1-i)
print myListStr