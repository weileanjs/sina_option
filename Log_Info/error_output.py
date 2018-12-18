# coding=utf-8
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
# rq = time.strftime('%Y%m%d', time.localtime(time.time()))
handler = logging.FileHandler("THS_PLATES.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def logError(*args):
    logger.error(args)


def logWarning(*arg):
    logger.warning(arg)


def error_deco(func):
    def wrapper(*args):
        try:
            func(*args)
        except Exception as e:
            logError('{} ERROR :{}'.format(func.__name__,str(e)))
    return wrapper
