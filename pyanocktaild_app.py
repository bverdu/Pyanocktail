# -*- coding: utf-8 -*-
'''
Created on 28 mai 2012

@author: babe
'''
#from pyanocktail.midi import sequencer, MidiThread
from pyanocktail.wsServer import SeqFactory
from pyanocktail.webServer import Dispatcher
from pyanocktail.midiservice import MidiService
from twisted.application import internet, service
from twisted.web.server import Site
from twisted.python import log
from pyanocktail.config import defaultConf
from multiprocessing import Queue
#from pyalsa.alsaseq import SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_CAP_READ, SEQ_PORT_CAP_SUBS_READ, SEQ_PORT_CAP_WRITE, SEQ_PORT_CAP_SUBS_WRITE, SEQ_PORT_TYPE_MIDI_GENERIC
from twisted.web.websockets import WebSocketsResource
import os

# Create a MultiService

def getSeqData(result_queue,status_queue):
        try:
                note = result_queue.get_nowait()
                log.msg('note: '+str(note))
                wsservice.sendmessage(note)
                                    
        except :    pass
        try:
            status = status_queue.get(timeout=0.1)
            log.msg('message :'+str(status))
            wsservice.sendmessage(status)
            if status == 'closed':
                return
#                    self.myreactor.stop()
#                    self.terminate()
#                midithread.stop()
#                del(seq)
            elif status == 'reload':
                midiservice.stopService(0)
                midiservice.startService(0)

        except Exception,err:
#                pass
            if len(err.message) > 1:
                log.msg(err.message)
            else:
                pass
#                log.msg(err.message)
            
try:
    dirname = os.path.expanduser("~/.pianocktail")
except:
    dirname = "/etc/pianocktail"
pyanocktailService = service.MultiService()
conf = defaultConf(dirname)
#conf.load(dirname)
debug = conf.debug
port = conf.httpport
theme = conf.theme
log.msg("Started...")
if debug:
    log.msg("Debug mode")

task_queue = Queue()
result_queue = Queue()
status_queue = Queue()
notein_queue = Queue()

midiservice = MidiService(conf,task_queue,result_queue,status_queue,notein_queue)
webresource = Dispatcher(debug,conf.installdir,task_queue,status_queue,conf)
webfactory = Site(webresource)
wsservice = SeqFactory(debug,task_queue,notein_queue)
wsresource = WebSocketsResource(wsservice)


web = webfactory
ws = Site(wsresource)
midiservice.setServiceParent(pyanocktailService)
internet.TCPServer(port, web).setServiceParent(pyanocktailService)
internet.TCPServer(port +1, ws).setServiceParent(pyanocktailService)
internet.TimerService(0,getSeqData,result_queue,status_queue).setServiceParent(pyanocktailService)


# Create an application as normal
application = service.Application("Pianocktail")

# Connect our MultiService to the application, just like a normal service.
pyanocktailService.setServiceParent(application)
