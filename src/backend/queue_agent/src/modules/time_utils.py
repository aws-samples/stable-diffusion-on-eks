import logging
from time import perf_counter

logger = logging.getLogger("queue-agent")

def get_time(f):
    def inner(*arg, **kwarg):
        s_time = perf_counter()
        res = f(*arg, **kwarg)
        e_time = perf_counter()
        logger.info('Used: {:.4f} seconds on api: {}.'.format(e_time - s_time, arg[0]))
        return res
    return inner