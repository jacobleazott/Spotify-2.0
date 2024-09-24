import logging
import functools
from typing import Union, Optional

FUNCTION_ARG_LOGGING_LEVEL = 15

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_file_logger(filename: str, log_level: Union[int, str]=logging.INFO, mode: str='w') -> logging.Logger:
    logger = logging.getLogger(filename)
    logger.setLevel(log_level)
    logger.addHandler(logging.FileHandler(filename, mode=mode))
    logger.handlers[0].setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d - %(message)s', 
        datefmt=f'%Y-%m-%d %H:%M:%S'))
    logger.propagate = False
    return logger


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def log_func(_func=None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger()
            # Log All Args/ Kwargs
            try:
                first_arg = next(iter(args), None)
                # does kwargs or args have any logger
                logger_params = [x for x in kwargs.values() if isinstance(x, logging.Logger)] + \
                    [x for x in args if isinstance(x, logging.Logger)]
                if hasattr(first_arg, "__dict__"):  # is first argument `self`
                    # does class (dict) members have any logger
                    logger_params += [x for x in first_arg.__dict__.values() if isinstance(x, logging.Logger)]
                    
                logger = next(iter(logger_params))  # get the first logger
                args_kwargs_sep = ", ".join([repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()])
                logger.log(FUNCTION_ARG_LOGGING_LEVEL, f"_function {func.__name__} called with {args_kwargs_sep}")
            except Exception:
                pass
            # Log Any Exceptions
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)
    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LogAllMethods:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in cls.__dict__.items():
            if callable(value):
                setattr(cls, attr, log_func(value))