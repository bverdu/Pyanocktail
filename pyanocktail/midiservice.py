# -*- coding: utf-8 -*-
'''
Created on 31 mai 2012

@author: babe
'''
#from twisted.internet import protocol
from twisted.application import service
from pyalsa.alsaseq import SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_CAP_READ, SEQ_PORT_CAP_SUBS_READ, SEQ_PORT_CAP_WRITE, SEQ_PORT_CAP_SUBS_WRITE, SEQ_PORT_TYPE_MIDI_GENERIC
from pyanocktail.midi import sequencer, MidiThread
from twisted.python import log

#class MidiProtocol(protocol.Protocol):
#    def __init__(self):
#        pass
#    
#class MidiFactory(protocol.Factory):
#    protocol = MidiProtocol
#    def __init__(self):
#        self.debug = self.service.debug
#    def buildProtocol(self):
#        proto = protocol.Factory.buildProtocol(self)
#        log.msg('midi protocol ?')
#        return proto
    
class MidiService(service.Service):
    threads = []
    def __init__(self,conf,task_queue,result_queue,status_queue,notein_queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.status_queue = status_queue
        self.notein_queue = notein_queue
        self.conf = conf
        self.seq = sequencer("Pianocktail",conf.getseqparameters())
        self.seqId = self.seq.client_id
        self.inportId = self.seq.create_simple_port("pianocktail-in", SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC , SEQ_PORT_CAP_WRITE | SEQ_PORT_CAP_SUBS_WRITE)
        self.outportId = self.seq.create_simple_port("pianocktail-out", SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC , SEQ_PORT_CAP_READ | SEQ_PORT_CAP_SUBS_READ)
        self.queue = self.seq.create_queue("queue")
        self.seq.setqueue(self.queue)
        self.commandqueue = self.seq.create_queue("commandqueue")
        self.seq.setcommandqueue(self.commandqueue)
        self.debug = self.conf.debug
        if self.debug:
            log.msg("Sequencer created")
            
    def startService(self):
        service.Service.startService(self)
        conf = self.conf
        debug = self.conf.debug
        self.seq.reloadConf(conf.getseqparameters())
        print(str(conf.getseqparameters()))
        notes = conf.getnotes()
        self.seq.setnotes(notes)
        if debug:
            log.msg("Notes charged")
        tabpompes = conf.getpumps()
        self.seq.settabpompes(tabpompes)
        self.seq.tabpompesdb = conf.pumpsdb
        self.seq.tabrecipes = conf.recipesdb
        if debug:
            log.msg("Pumps charged")
        self.seq.dep = conf.getdep()
        self.seq.debug = debug
        self.seq.up = conf.getup()
        if debug:
            log.msg("Sequencer ready")
        
# Connexion midi automatique

        sysports = self.seq.findmidiport()
        conf.sysports = sysports
        sysInport = sysports[0]
        sysOutport = sysports[1]
        if debug:
            log.msg(sysports)
        if sysInport != (0, 0):
            self.seq.connect_ports(sysInport, (self.seqId, self.inportId), 0, 0, 1, 1)
        if sysOutport != (0, 0):
            self.seq.connect_ports((self.seqId, self.outportId), sysOutport)
    
# Lancement du thread midi

        conf.sysInport = sysInport
        conf.sysOutport = sysOutport
        midithread = MidiThread(self.seq,self.debug,self.task_queue,self.result_queue,self.status_queue,self.notein_queue)
        midithread.start()
        self.threads.append(midithread)
        if debug:
            log.msg('Midi engine started')
    
    def stopService(self,restart=9):
        self.task_queue.put(restart)
        log.msg("stopping Midiservice !")
        for thread in self.threads:
            thread.stop()
        log.msg("midi thread stopped")
#        del(self.seq)
        log.msg("sequencer destroyed")
        service.Service.stopService(self)


    