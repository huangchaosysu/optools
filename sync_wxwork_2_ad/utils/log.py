# @Time    : 18-9-12 上午11:45
# @Author  : Chao
# @File    : log.py
import logging
import os
from logging.handlers import RotatingFileHandler


class CLog():
    def __init__(self, logfile, logdir='./logs', level=logging.DEBUG, name="op_tools"):
        self._debug = False
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        logfile = os.path.join(logdir, logfile)
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        handler = RotatingFileHandler(
            logfile, backupCount=10, maxBytes=10*1024*1024, encoding="utf-8")
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __del__(self):
        for hdl in self.logger.handlers:
            hdl.close()
            self.logger.removeHandler(hdl)

    def info(self, *args):
        self.logger.info(*args)

    def error(self, *args):
        self.logger.error(*args)


logger = CLog('./tools.log')


if __name__ == '__main__':
    c = CLog('tools.log')
    c.logger.info('hello world')