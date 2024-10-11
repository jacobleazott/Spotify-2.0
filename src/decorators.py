# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    LOGGERS AND DECORATORS                   CREATED: 2024-09-20          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file simply contains function decorators, and log helpers.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import functools
import logging
from typing import Union, Optional

from Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Crates a simple Logger object with our desired format and returns it.
INPUT: filename - name of logfile.
       log_level - int or str for logging level.
       mode - write ('w') or append ('a') mode for the logger.
OUTPUT: Logger Object
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_file_logger(filename: str, log_level: Union[int, str]=logging.INFO, mode: str='w', 
                    console: bool=False) -> logging.Logger:
    logger = logging.getLogger(filename)
    logger.setLevel(log_level)
    file_handler = logging.FileHandler(filename, mode=mode)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d - %(message)s', 
        datefmt=f'%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(filename)s:%(lineno)d - %(message)s'))
        logger.addHandler(console_handler)
    
    return logger


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Decorator that can auto detect a logger passed in to a function (args or kwargs) or is a member of that 
                functions class. It uses a default logger if neither are present. It then logs all input args for that
                function at 'FUNCTION_ARG_LOGGING_LEVEL'. Additionally, it catches any exceptions raised to make sure
                they make it into the log and also provide us with a mini 'stack trace' if the caller functions also
                used this decorator through the re-raise.
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
                logger.log(Settings.FUNCTION_ARG_LOGGING_LEVEL, f"_function {func.__name__} " \
                                                                f"called with {args_kwargs_sep}")
            except Exception:
                pass
            # Log Any Exceptions
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Exception raised in {func.__name__}. exception: {str(e)}", exc_info=True)
                raise e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)
    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Applies 'log_func' decorator to every single function in a class.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LogAllMethods:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in cls.__dict__.items():
            if callable(value):
                setattr(cls, attr, log_func(value))


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════