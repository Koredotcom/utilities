""" pyhton decorators for KnowledgeGraph project"""
import requests
import logging
import traceback
from time import time
from functools import wraps
logger = logging.getLogger(__name__)

def timing(f_parameter):
    """ print the execuition time of a fucntion """

    @wraps(f_parameter)
    def wrap(*args, **kw):
        """ wrapper fucntion """

        color_reset = "\033[0;0m"
        color_yellow = "\033[0;32m"
        time_start = time()
        result = f_parameter(*args, **kw)
        time_end = time()
        print color_yellow + 'EXECUTION_TIME: %2.4f   \t%r' % \
            ((time_end - time_start) * 1000, f_parameter.__name__) + \
            color_reset
        return result
    return wrap
    
    
def exception_handling(f_parameter):
    """ exception_handling """

    @wraps(f_parameter)
    def wrap(*args, **kw):
        """ wrapper fucntion """
        try:
            result = f_parameter(*args, **kw)
            return result
        except requests.ConnectionError:
            logger.critical("!!!Gremlin server is not reachable")
        except:
            logger.debug(traceback.format_exc())
        return False
    return wrap
