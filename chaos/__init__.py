import logging as log
import sys
import config

log.basicConfig(stream=sys.stderr,level=config.LOG_LEVEL,format='%(message)s')
