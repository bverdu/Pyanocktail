# -*- coding: utf-8 -*-
'''
Created on 30 mai 2012

@author: babe
'''
from twisted.internet import protocol,defer
from twisted.internet.protocol import ServerFactory
from twisted.python import log

Com = dict()
Com['record']=1
Com['stop']=2
Com['play']=7
Com['status']=6
Com['reload']=5
Com['cocktail']=3
Com['panic']=4
Com['close']=9
Com['config']=6

class PyanoTCP(protocol.Protocol):
    
    def connectionMade(self):
        self.factory.clients.append(self)
        if self.factory.debug:
            log.msg("New Connection from: "+str(self.transport.getHost()))
    def dataReceived(self, data):
#        if self.factory.debug:
        log.msg('data from ws: '+data)
        d = self.factory.wsReceived(data)
        
        def onError(err):
            if self.factory.debug:
                log.msg('string: '+data)
            return 'Internal error in server'
        d.addErrback(onError)
        
        def writeResponse(message):
            if message is not None:
                self.transport.write(message)
#            self.transport.loseConnection()
        d.addCallback(writeResponse)
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        if self.factory.debug:
            log.msg("ws connection lost\n")
    def send(self,data,debug=False):
        if self.connected:
            self.transport.write(data.encode('utf-8'))
#            if debug:
#                log.msg ("Sent to Websocket: "+data)
        elif debug :
            log.msg("Sent failed: not connected")
        
class SeqFactory(ServerFactory):
    protocol = PyanoTCP
    def __init__(self,debug,task_queue,notein_queue):
        self.task = task_queue
        self.notein = notein_queue
        self.debug = debug
        self.clients = []
    def buildProtocol(self, addr):
        proto = ServerFactory.buildProtocol(self, addr)
        log.msg('websocket service started')
        return proto
    def sendmessage(self,message):
        try :
            for client in self.clients :
                client.send(message,self.debug)
        except Exception,err:
            if self.debug:
                log.msg("sendmessage error: "+err.message)
    def wsReceived(self,data):
        if data.isdigit() or data.startswith("-"):
            return defer.Deferred(self.putnote(data))
            if self.debug:
                log.msg('digit: '+data)
        else:
            return defer.Deferred(self.putstat(Com[data]))
            if self.debug:
                log.msg('string: '+data)
    def appendNote(self,note):
        return defer.Deferred(self.putnote(note))
    def setStatus(self,command):
        return defer.Deferred(self.putstat(Com[command]))
    def putnote(self,note):
        try:
            self.notein.put_nowait(note)
#            return "0"
        except:
#            return "1"
            log.msg("ws to midi queue fail")                
    def putstat(self,comint):
        try:
            log.msg("command from ws : "+str(comint))
            self.task.put(comint)
#            return "0"
        except:
#            return "1"
            log.msg("ws to task queue fail")

