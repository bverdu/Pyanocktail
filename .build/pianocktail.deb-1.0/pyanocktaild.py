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
        except Exception,err:
#                pass
            if len(err.message) > 1:
                log.msg(err.message)
            else:
                pass
#                log.msg(err.message)
            
 
dirname = os.path.expanduser("~/.pianocktail")
pyanocktailService = service.MultiService()
conf = defaultConf(dirname)
#conf.load(dirname)
debug = conf.debug
port = conf.httpport
theme = conf.theme
log.msg("Started...")
if debug:
    log.msg("Debug mode")


# création du séquenceur
#seqparameters = conf.getseqparameters()
#seq = sequencer("Pianocktail",seqparameters)
#                seq.clientname = "Pianocktail"
#seqId = seq.client_id
#inportId = seq.create_simple_port("pianocktail-in", SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC , SEQ_PORT_CAP_WRITE | SEQ_PORT_CAP_SUBS_WRITE)
#outportId = seq.create_simple_port("pianocktail-out", SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC , SEQ_PORT_CAP_READ | SEQ_PORT_CAP_SUBS_READ)
#queue = seq.create_queue("queue")
#seq.setqueue(queue)
#commandqueue = seq.create_queue("commandqueue")
#seq.setcommandqueue(commandqueue)
#if debug:
#    log.msg("Sequencer created")
#notes = conf.getnotes()
#seq.setnotes(notes)
#if debug:
#    log.msg("Notes charged")
#tabpompes = conf.getpumps()
#if debug:
#    log.msg("Pumps charged")
#seq.settabpompes(tabpompes)
#if debug:
#    log.msg("Pumps configured")
#seq.dep = conf.getdep()
#seq.debug = debug
#seq.up = conf.getup()
#seq.start_queue(queue)
#seq.start_queue(commandqueue)
#if debug:
#    log.msg("Sequencer ready")
#
## Connexion midi automatique
#
#sysports = seq.findmidiport()
#conf.sysports = sysports
#sysInport = sysports[0]
#sysOutport = sysports[1]
#if debug:
#    log.msg(sysports)
#if sysInport == (0, 0):
#    pass
#else:
#    seq.connect_ports(sysInport, (seqId, inportId), 0, 0, 1, 1)
#if sysOutport == (0, 0):
#    pass
#else:
#    seq.connect_ports((seqId, outportId), sysOutport)
#    
## Lancement du thread midi
#conf.sysInport = sysInport
#conf.sysOutport = sysOutport
task_queue = Queue()
result_queue = Queue()
status_queue = Queue()
notein_queue = Queue()
#                task_queue = Pipe()
#                result_queue = Pipe()
#                status_queue = Pipe()
#                notein_queue = Pipe()
#if conf.perf == 1:
#    perf = True
#else:
#    perf = False
#midithread = MidiThread(seq,debug,task_queue,result_queue,status_queue,notein_queue)
#midithread.start()
#if debug:
#    log.msg('Midi engine started')
midiservice = MidiService(debug,conf,task_queue,result_queue,status_queue,notein_queue)
webresource = Dispatcher(debug,conf.installdir,task_queue,status_queue,conf)
webfactory = Site(webresource)
wsservice = SeqFactory(debug,task_queue,notein_queue)
wsresource = WebSocketsResource(wsservice)

#myreactor = reactor
#myreactor.listenTCP(port, factory)
#myreactor.listenTCP(self.port + 1,Site(self.wsresource))
#myreactor.callLater(0,self.getSeqData,result_queue,status_queue)


web = webfactory
ws = Site(wsresource)
midiservice.setServiceParent(pyanocktailService)
internet.TCPServer(port, web).setServiceParent(pyanocktailService)
wsFactory = Site(wsresource)
internet.TCPServer(port +1, ws).setServiceParent(pyanocktailService)
internet.TimerService(0,getSeqData,result_queue,status_queue).setServiceParent(pyanocktailService)


# Create an application as normal
application = service.Application("Pianocktail")

# Connect our MultiService to the application, just like a normal service.
pyanocktailService.setServiceParent(application)
