import logging
from functools import wraps


def logg(mes=''):
    def log_decorator(fn):
        @wraps(fn)
        def wrapped(inst, *args, **kwargs):
            logger = logging.getLogger('calendoola_logger')
            try:
                res = fn(inst, *args, **kwargs)
            except Exception as ex:

                _log_error(fn, ex, str(ex.args), inst, logger)
            else:
                _log_info(fn, res, mes, inst, logger)
                return res

        return wrapped

    return log_decorator


def _log_error(fn, ex, err, inst, logger):
    logger.error('function: %s; exception: %s; %s; %s',
                 fn.__name__, ex.__class__.__name__, inst.__class__.__name__, err)
    raise ex


def _log_info(fn, res, mes, inst, logger):
    if hasattr(inst, 'id'):
        id = inst.id
    elif hasattr(inst, 'nickname'):
        id = inst.nickname
    else:
        id = None
    logger.info('function: %s; result: %s; %s; %s; %s',
                fn.__name__, res, inst.__class__.__name__, id, mes)
