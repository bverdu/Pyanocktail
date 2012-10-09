# ==== twisted/plugins/pyanocktail_plugin.py ====
# python modules
import os

# - Twisted modules -
from twisted.python import usage

# - pyanocktail modules -
from pyanocktail.config import defaultConf
from pyanocktail import pyanocktaild

class Options(usage.Options):
    try:
        dirname = os.path.expanduser("~/.pianocktail")
        conffile = open(os.path.join(dirname,"config"), 'r')
    except:
        dirname = "/etc/pianocktail"
    conf = defaultConf(dirname)
    config = dirname
    basedir = conf.installdir
    port = conf.httpport
    optParameters = [
    ['config', 'c', config, 'Configuration file path'],
    ['basedir', 'd', basedir, 'Base directory for HTML templates'],
    ['port', 'p', port, 'http port for the web console']
    ]
        
    
    
def makeService(config):
        return pyanocktaild.makeService(config)
