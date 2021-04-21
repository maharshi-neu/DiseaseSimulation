import os, logging
from .util import *
from .Config import *

cfg = Config()

CWD = os.getcwd()
logp = os.path.join(CWD, 'log')

if not os.path.exists(logp):
    os.makedirs(logp)

logfile = os.path.join(logp, 'sim.log')
logging.FileHandler(
        logfile, mode="w", encoding=None, delay=False)

logging.basicConfig(
        filename=logfile, format='%(levelname)s:%(message)s', level=logging.INFO)

from .Particle import *
from .Simulator import *

