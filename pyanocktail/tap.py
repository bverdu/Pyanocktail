# ==== twisted/plugins/pyanocktail_plugin.py ====
# python modules
import os

# - Twisted modules -
from twisted.python import usage

# - pyanocktail modules -
from pyanocktail.config import mainConfig
from pyanocktail import pyanocktaild

class Options(usage.Options):
    port = 8888
    try:
        confDir = os.path.expanduser("~/.pianocktail")
#         print(confDir)
#         conffile = open(os.path.join(dirname,"config"), 'r')
    except Exception, err:
        confDir = "/etc/pianocktail"
#         print("erreur conf: % " % err)
    try:
        conf = mainConfig(confDir,'/usr/share/pianocktail',port,False)
        config = confDir
        basedir = conf.installdir
    except:
        config = None
        basedir = '/usr/share/pianocktail'
#     dev = False
    optParameters = [
    ['config', 'c', config, 'Configuration file path'],
    ['basedir', 'd', basedir, 'Base directory for HTML templates'],
    ['port', 'p', port, 'http port for the web console']]
    optFlags = [['dev', 'x', 'developper mode']]
        
    
    
def makeService(config):
#     print(config)
    return pyanocktaild.makeService(config)
