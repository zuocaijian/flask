# -*- coding:utf-8 -*-

"""
author:zcj
create:2017.11.23
fun:
"""

import logging
from logging import Formatter, getLogger
from logging.handlers import SMTPHandler

from app import app

mail_handler = SMTPHandler('smtp.163.com', 'cj_zuo@163.com', app.config['EMAIL'], 'logging from my flask app',
                           credentials=('cj_zuo@163.com', 'zcj19901202'), secure=())
mail_handler.setLevel(logging.WARNING)
mail_handler.setFormatter(Formatter('''
Message type:               %(levelname)s
Location:                   %(pathname)s:%(lineno)d
Module:                     %(modules)s
Function:                   %(funcName)s
Time:                       %(asctime)s
Message:

%(message)s
'''))

loggers = [app.logger, getLogger('sqlalchemy'), getLogger('otherlibrary')]
for logger in loggers:
    logger.addHandler(mail_handler)
