import logging

# Choose where to output your logs
logtoconsole = True
logtojournal = True
logtofile = True

"""
Set the threshold for this logger to lvl. Logging messages which are less
severe than lvl will be ignored. Choose one of these levels:
* CRITICAL
* ERROR
* WARNING
* INFO
* DEBUG
* NOTSET
"""
level = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(level)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s\t- %(module)s::%(funcName)s - %(message)s')

if logtojournal:
    from systemd.journal import JournalHandler
    logger.setLevel(level)
    logger.addHandler(JournalHandler())

if logtofile:
    fh = logging.FileHandler('example.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

if logtoconsole:
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
