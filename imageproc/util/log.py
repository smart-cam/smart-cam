'''
Created on Feb 28, 2014
@author: ssatpati
'''

import logging

def getLogger(name, level = logging.INFO):
    logging.basicConfig(format='%(asctime)s [%(levelname)s]:%(message)s')
    logging.info('Creating Logger')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger