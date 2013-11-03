# -*- coding: utf-8 -*-
'''

Pyanocktail main module, initialise midi and web services
Created on 28 mai 2012

@author: babe
'''
import os
from pyanocktail.webServer import WebService
#from pyanocktail.midiservice import MidiService
from twisted.application import service
from twisted.python import log
from pyanocktail.config import mainConfig


def makeService(config):
    
    ''' Main service initialization
    '''
    
#     def getSeqData(result_queue,status_queue):
#         ''' utility function to synchronize queues 
#         '''
#         try:
#                 note = result_queue.get_nowait()
#                 log.msg('note: '+str(note))
#                 webservice.wsfactory.sendmessage(note)
#                                     
#         except :    pass
#         try:
#             status = status_queue.get(timeout=0.1)
#             log.msg('message :'+str(status))
#             if isinstance(status, str):
#                 webservice.wsfactory.sendmessage(status)
#                 if status == 'closed':
#                     return
#                 elif status == 'reload':
#                     midiservice.stopService(0)
#                     midiservice.startService(0)
#             elif isinstance(status, int):
#                 webservice.wsfactory.got_midipid(status)
#         except Exception,err:
#             if len(err.message) > 1:
#                 log.msg(err.message)
#             else:
#                 pass
# #                log.msg(err.message)

    pyanocktailService = service.MultiService()
    if config['config'] is not None:
        dirname = config['config']
        installdir = config['basedir']
        if config['dev'] == True:
            installdir = os.path.abspath(os.path.curdir)
            log.msg("installdir=%s" % installdir)
            dirname = os.path.expanduser('~/.pianocktail')
    elif config['dev'] == True:
        installdir = os.path.abspath(os.path.curdir)
        dirname = os.path.expanduser('~/.pianocktail')
    else:
        dirname = "/etc/pianocktail"
        installdir = "/usr/share/pianocktail"
    port = config['port']
    conf = mainConfig(dirname,installdir,port,True)
#     if config['basedir'] is not None:
#         basedir = config['basedir']
#     else:
#         basedir = conf.installdir
    debug = conf.debug
    #theme = conf.theme
    log.msg("Pianocktail main service started...")
    if debug:
        log.msg("Debug mode")
    
    #midiservice = MidiService(conf,task_queue,result_queue,status_queue,notein_queue)
    webservice = WebService(debug,installdir,conf)
    #midiservice.setServiceParent(pyanocktailService)
    webservice.setServiceParent(pyanocktailService)
    ''' queues sync '''
#     internet.TimerService(0,getSeqData,result_queue,status_queue).setServiceParent(pyanocktailService)
    
    return pyanocktailService
