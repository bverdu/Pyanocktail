# -*- coding: utf-8 -*-
#! /usr/bin/python2
#  This module is the midi controller, running in its own process
#
# Bertrand Verdu  08/08
from pyalsa.alsaseq import Sequencer, SeqEvent, SEQ_TIME_STAMP_REAL, SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT,  SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_CAP_SUBS_WRITE, SEQ_PORT_CAP_WRITE, SEQ_PORT_CAP_SUBS_READ, SEQ_PORT_CAP_READ, SEQ_EVENT_NOTEON, SEQ_EVENT_ECHO, SEQ_EVENT_NOTEOFF
import time
from multiprocessing import Process
import os
from songAnalysis2 import MathEngine

notesFile = os.path.join(os.path.expanduser("~/.pianocktail/scripts/"), "current.pckt")

def listOutports():
    outports = []
    sq = Sequencer()
    for connection in sq.connection_list():
        cname, cid, ports = connection
        if cname == 'Midi Through':
                continue
        for port in ports:
            pid = port[1]
            pinfo = sq.get_port_info(pid, cid)
            miditype = pinfo['type']
            caps = pinfo['capability']
            if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT, SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_TYPE_PORT | SEQ_PORT_TYPE_HARDWARE | SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC) and caps in (SEQ_PORT_CAP_SUBS_WRITE | SEQ_PORT_CAP_WRITE, 127):
                outports.append([cid,pid,cname])
    return outports

def listInports():
    inports = []
    sq = Sequencer()
    for connection in sq.connection_list():
        cname, cid, ports = connection
        if cname == 'Midi Through':
                continue
        for port in ports:
            pid = port[1]
            pinfo = sq.get_port_info(pid, cid)
            miditype = pinfo['type']
            caps = pinfo['capability']
            if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT, SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_TYPE_PORT | SEQ_PORT_TYPE_HARDWARE | SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC) and caps in (SEQ_PORT_CAP_SUBS_READ | SEQ_PORT_CAP_READ, 127):
                inports.append([cid,pid,cname])
    return inports

def savenotestofile(notes,path=notesFile):

    dump = open(os.path.join(path,"current.pckt"), 'w+')
    for i in range(len(notes)):
        if notes[i][1] == 1:
            dump.write(str(notes[i][0]) + " " + "1" + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        elif notes[i][1] == 0:
            dump.write(str(notes[i][0]) + " " + "0" + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        elif notes[i][1] == 2:
            dump.write(str(notes[i][0]) + " " + "5" + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        else :
            dump.write(str(notes[i][0]) + " " + str(notes[i][1]) + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
    dump.close
    

class MidiThread(Process):
    
    def __init__(self, seq, debug, task_queue, result_queue, status_queue, notein_queue):
        Process.__init__(self)
        self.seq = seq
        self.debug = debug
        if seq.perf == 1:
            self.perf = True
        else : self.perf = False
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.status_queue = status_queue
        self.notein_queue = notein_queue
        self.running = True
        
    def run(self):
        seq = self.seq
        debug = self.debug
        perf = self.perf
        save = False
        analysed = False
        status = 'Initialized'
        command = 0
        notes = []
        seq.service(seq.readyled, SEQ_EVENT_NOTEON)
        triggerStop = 0
        event = SeqEvent(SEQ_EVENT_ECHO)
        if debug:
            print("midi pid for debug: "+str(self.pid)+"\n")
        while self.running:
            try :
                next_task = self.task_queue.get_nowait()
                command = next_task
            except :
                pass
            try:
                notein = int(self.notein_queue.get_nowait())
                moment = (time.time() - seq.startime)*1.000
                if save:
                    if notes == []:
                        begin = moment
                    if notein >= 0:
                        notes.append([(moment - begin)*1000, 1, notein, 64])
#                        if debug:
#                            print("note "+str(notein)+" recorded at "+str(moment - begin)+" seconds")
                    else:
                        notes.append([(moment - begin)*1000.000, 0, abs(notein), 64])
            except: 
                pass
            if isinstance(command,int):
                if command == 0:
                    try:
                        for event in seq.receive_events(timeout=100, maxevents=4):
                            if debug:
                                print(str(event) + " received")
                            if event.is_note_type:
                                note = event.get_data()['note.note']
                                if note == seq.startevent:
                                    if event.type == SEQ_EVENT_NOTEON:
                                        if save == True:
                                            pass
                                        else:
                                            command = 1
                                    else :
                                        pass
                                elif note == seq.stopevent:
                                    if event.type == SEQ_EVENT_NOTEON:
                                        if triggerStop < 2:
                                            triggerStop = triggerStop + 1
                                            command = 2
                                        else :
                                            command = 4
                                    else:
                                        pass
                                elif note == seq.cocktailevent:
                                    if event.type == SEQ_EVENT_NOTEON:
                                        command = 3
                                    else: pass
                                elif note == seq.panicevent:
                                    if event.type == SEQ_EVENT_NOTEON:
                                        command = 4
                                    else :
                                        command = 0
                                elif note == seq.reloadevent:
                                    command = 5
                                elif note == seq.upevent:
                                    command = 7
                                elif note == seq.downevent:
                                    command = 8
                                elif save == True:
                                    triggerStop = 0
                                    if notes == []:
                                        begin = event.time
                                    if event.type == SEQ_EVENT_NOTEON:
    #                                    notes.append([int((timestamp - begin) * 1000.000), 1, note, int(event.get_data()['note.velocity'])])
                                        notes.append([((event.time - begin)* 1000.000), 1, note, int(event.get_data()['note.velocity'])])
                                        if perf:
                                            self.result_queue.put_nowait(str(note))
                                    else :
    #                                    notes.append([int((timestamp - begin) * 1000.000), 0, note, int(event.get_data()['note.velocity'])])
                                        notes.append([((event.time - begin)* 1000.000), 0, note, int(event.get_data()['note.velocity'])])
                                        if perf:
                                            self.result_queue.put_nowait("-"+str(note))
                                else:
                                    triggerStop = 0
                                                                
                               
                            elif event.is_control_type:
                                if save == True:
                                    if notes == []:
                                        begin = event.time
    #                                notes.append([int((timestamp - begin) * 1000.000), 2, int(event.get_data()['control.param']), int(event.get_data()['control.value'])])
                                    notes.append([((event.time - begin) * 1000.000), 2, int(event.get_data()['control.param']), int(event.get_data()['control.value'])])
                                    if perf:
                                        self.result_queue.put_nowait(event.get_data()['control.param'])
                    except Exception, err: 
                        
                        print("midi error: "+err.message)
        #            
                elif command == 1:
                    save = True
                    if debug:
                        print "command record received"
    #                        seq.status = "recording"
                    if debug:
                        print "notes purged"
                    notes = []
                    analysed = False
    #                begin = timestamp
                    if debug:
                        print "Recording..."
                    status = "Recording"
                    self.status_queue.put(status)
                    seq.service(seq.readyled, SEQ_EVENT_NOTEOFF)
                    seq.service(seq.recordled, SEQ_EVENT_NOTEON)
                    command = 0
                        
                elif command == 2:
                    if debug:
                        print "command stop received"
                    if save:
                        save = False
                        seq.service(seq.readyled, SEQ_EVENT_NOTEON)
                        seq.service(seq.recordled, SEQ_EVENT_NOTEOFF)
                        if debug:
                            print "stopped"
                            print "Analyse requested..."
    #                        seq.status = "Analyse requested..."
                        if len(notes) < 5:
                            if debug:
                                print "notes = empty"
                            status = "Not enough played to drink !"
                            self.status_queue.put(status)
                            print "Ready"
                        else :
                            if debug:
                                print "notes OK"
                                print "Analysing..."
                            status = "Analysing"
                            self.seq.notes = notes
                            self.status_queue.put(status)
                            analyse = seq.analyse(notes)
                            seq.service(seq.cocktailled, SEQ_EVENT_NOTEON)
                            for line in analyse[1]:
                                    self.result_queue.put(line)
    #                                if debug:
    #                                    print("ws debug " + line)
                            if debug:
                                print "Analyse finished"
                            status = "Analyse finished"
                            time.sleep(1)
                            self.status_queue.put(status)
                    elif analysed == False:
                        if save:
                            save = False
                            if debug:
                                print "Analyse requested..."
                            status = "Analysing"
                            self.status_queue.put(status)
                            seq.service(seq.recordled, SEQ_EVENT_NOTEOFF)
                            if len(notes) < 5 :
                                if debug:
                                    print "notes = empty"
                                    print "ready to record"
                                status = "Not enough played to drink !"
                                self.status_queue.put(seq.status)
                                seq.service(seq.recordled, SEQ_EVENT_NOTEOFF)
                                seq.service(seq.readyled, SEQ_EVENT_NOTEON)
                                seq.service(seq.cocktailled, SEQ_EVENT_NOTEOFF)
                            else :
                                if debug:
                                    print "notes OK"
                                    print "Analysing..."
                                status = "Analysing"
                                self.status_queue.put(status)
                                analyse = seq.analyse(notes)
                                if debug:
                                    print "Analyse finished"
                                    print("alors: "+analyse[1])
                                status = "Analyse finished"
                                for line in analyse[1]:
                                    self.result_queue.put(str(line))
                                    print("ws debug" + line)
                                self.status_queue.put(status)
                                seq.service(seq.recordled, SEQ_EVENT_NOTEOFF)
                                seq.service(seq.readyled, SEQ_EVENT_NOTEON)
                                seq.service(seq.cocktailled, SEQ_EVENT_NOTEOFF)
                        else:
                            self.status_queue.put(status)
                            
                    
                    else:
                        self.status_queue.put(status)
                    command = 0
                
                elif command == 3:
                    if debug:
                            print("Cocktail command received")
                    if save:
                        save = False
                        if len(notes) > 4:
                            print("Analysing and serving...")
                            status =("Analyse et service en cours")
                            self.status_queue.put(status)
                            analyse = seq.analyse(notes)
                            for line in analyse[1]:
                                self.result_queue.put_nowait(line)
                            self.status_queue.put(seq.cocktailyse(analyse[0]))
                        else:
                            if debug:
                                print("Nothing to analyse :(")
                    
                        if debug:
                            print "Service terminé"
                        command = 0                
                    else:
                        if len(notes) > 4:
                            status = "Service en cours"
                            self.status_queue.put(status)
                            self.status_queue.put(seq.cocktailyse(analyse[0]))
                            if debug:
                                print "ready to record..."
                            status = "Ready"
    #                        self.status_queue.put(status)
                            seq.service(seq.recordled, SEQ_EVENT_NOTEOFF)
                            seq.service(seq.readyled, SEQ_EVENT_NOTEON)
                            seq.service(seq.cocktailled, SEQ_EVENT_NOTEOFF)
                        else: pass
                        command = 0
                
                elif command == 4:
                    if debug:
                        print "panique !!!"
                    for i in range(255):
                        seq.service(i, 7)
                    command = 0
                    triggerStop = 0
                
                elif command == 5:
                    if debug:
                        print "midi reload request"
                    self.running = False
                    self.status_queue.put('reload')
                    command = 0
                elif command == 6:
                    if debug:
                        print(status)
                    self.status_queue.put(status)
                    command = 0
                elif command == 7:
                    if event.type == SEQ_EVENT_NOTEON:
                        seq.service(seq.up, SEQ_EVENT_NOTEON)
                    elif event.type == SEQ_EVENT_NOTEOFF:
                        seq.service(seq.up, SEQ_EVENT_NOTEOFF)
                    command = 0
                elif command == 8:
                    seq.sansalcool = not seq.sansalcool
                    command = 0
                elif command == 9:
                    if debug:
                        print("command: 9")
                    status = 'closed'
                    self.running = False
                    seq.status = 'closed'
                    self.status_queue.put('closed')
            else:
                print("string command")
                if command[0] == 'b':
                    self.seq.service(self.seq.dep+int(command[1:]),SEQ_EVENT_NOTEON)
                elif command[0] == 's':
                    self.seq.service(self.seq.dep+int(command[1:]),SEQ_EVENT_NOTEOFF)
                command = 0

    def stop(self):
        self.running = False
        self.join()
        
class sequencer(Sequencer):
    
    def __init__(self,name,parameters):
        Sequencer.__init__(self)
        self.clientname = name
        self.dep = parameters['dep']
        self.alc = parameters['alc']
        self.startevent = parameters['start']
        self.stopevent = parameters['stop']
        self.cocktailevent = parameters['cocktail']
        self.panicevent = parameters['panic']
        self.reloadevent = parameters['reload']
        self.upevent = parameters['up']
        self.downevent = parameters['down']
        self.readyled = parameters['readylight']
        self.recordled = parameters['recordlight']
        self.cocktailled = parameters['analyselight']
        self.perf = parameters['perf']
        self.scriptpath = parameters['scriptpath']
        try:
            if parameters['old'] == 1:
                self.old = True
            else:
                self.old = False
        except:
            self.old = True
        self.complexind = 0.5
        self.tristind = 1
        self.nervind = 1
        self.notes = []
        self.tabpompes = []
        self.tabpompesdb = []
        self.tabrecipes = []
        self.command = 0
        self.outClientId = 0
        self.outPortId = 0
        self.inClientId = 0
        self.inPortId = 0
        self.tempo = 0
        self.ppq = 0
        self.status = "Ready"
        self.debug = False
        self.analysed = False
        self.up = 0
        self.down = 0
        self.sansalcool = False
        self.startime = time.time()
    def connect_ports(self, srcaddr, dstaddr, queue=0, exclusive=0, time_update=0, time_real=0):
        Sequencer.connect_ports(self, srcaddr, dstaddr, queue, exclusive, time_update, time_real)
        self.startime = time.time()
    def reloadConf(self,parameters):
        self.dep = parameters['dep']
        self.alc = parameters['alc']
        self.startevent = parameters['start']
        self.stopevent = parameters['stop']
        self.cocktailevent = parameters['cocktail']
        self.panicevent = parameters['panic']
        self.reloadevent = parameters['reload']
        self.upevent = parameters['up']
        self.downevent = parameters['down']
        self.readyled = parameters['readylight']
        self.recordled = parameters['recordlight']
        self.cocktailled = parameters['analyselight']
        self.perf = parameters['perf']
        self.scriptpath = parameters['scriptpath']
        try:
            if parameters['old'] == 1:
                self.old = True
            else:
                self.old = False
        except:
            self.old = True
        self.complexind = 0.5
        self.tristind = 1
        self.nervind = 1
        self.notes = []
        self.tabpompes = []
        self.status = "Reloaded"
    def setqueue(self, queue):
        self.queue = queue
    def setcommandqueue(self, queue):
        self.commandqueue = queue
    def setnotes(self, notes):
        self.notes = notes
        if self.debug:
            print str(self.notes) + " received"
    def getnotes(self):
        return self.notes
    def settabpompes(self, tabpompes=[]):
        self.tabpompes = tabpompes
    def gettabpompes(self):
        return self.tabpompes
    def getstatus(self):
        return self.status
    def setstatus(self,action,cli=False):
        if action == 'close':
            self.command = 9 
            self.status = 'closed'
            return 'closed'
        elif action == 'status':
            return self.status
        elif action == 'stop':
            self.command = 2
        elif action =='play':
            self.command = 4
        elif action == 'record':
            self.command = 1
        elif action == 'reload':
            self.command = 5
        elif action == 'cocktail' :
            self.command = 3
        elif action == 'panic' :
            self.command = 4
        else: 
            raise Exception()
        evt=SeqEvent(SEQ_EVENT_ECHO)
        evt.dest = (self.client_id, self.inPortId)
        evt.queue = self.commandqueue
        self.output_event(evt)
        self.drain_output()
        self.sync_output_queue()
        if cli:
            time.sleep(0.1)
            return self.status
        else:
            return None
    def putNote(self,note):
        try:
            if note >= 0:
                put = SeqEvent(SEQ_EVENT_NOTEON)
                put.dest = (self.client_id, self.inPortId)
                put.timestamp = SEQ_TIME_STAMP_REAL
                put.time = (time.time() - self.startime)*1.000
                put.set_data({'note.note' : note, 'note.velocity' : 64})
                put.queue = self.commandqueue
                print("output event")
                self.output_event(put)
                print("drain output")
                self.drain_output()
                print("sync output queue")
#                self.sync_output_queue()
            else :
                put = SeqEvent(SEQ_EVENT_NOTEOFF)
                put.dest = (self.client_id, self.inPortId)
                put.timestamp = SEQ_TIME_STAMP_REAL
                put.time = (time.time() - self.startime)*1.000
                put.set_data({'note.note' : abs(note), 'note.velocity' : 64})
                put.queue = self.commandqueue
                self.output_event(put)
                self.drain_output()
#                self.sync_output_queue()
        except Exception,err:
            if self.debug:
                print("putNote Error: "+err.message)
            return "1"
            
    def getcommand(self):
        return self.command
    def setdep(self, dep=0):
        self.dep = dep
    def analyse(self, notes):
        savenotestofile(notes,self.scriptpath)
#        analysed = MathEngine()
        analysed = MathEngine(self.scriptpath)
        analysed.debug = self.debug
        analysed.alc = self.alc
        if self.old:
            analysed.settabpompes(self.tabpompes)
        else:
            analysed.settabrecipes(self.tabrecipes,self.tabpompesdb)
        analyse = analysed.solve(self.old,self.complexind,self.tristind,self.nervind,self.alc)
        self.status = "analysed"
        if self.debug:
            print "analysed"
        self.analysed = True
        return analyse
    
    def service(self, note, miditype):
        play = SeqEvent(miditype)
        play.source = (self.client_id, 1)
        if self.debug :
            print "source = " + str(self.client_id)
        play.dest = (self.outClientId, self.outPortId)
        if self.debug :
            print "dest =" + str(self.outClientId)
        play.queue = self.queue
        play.set_data({'note.note' : note, 'note.velocity' : 64})
        if self.debug:
            print str(play) + "envoyé"
        self.output_event(play)
        self.drain_output()
        self.sync_output_queue()
    
    def cocktailyse(self, analyse):
        if self.debug:
            print analyse
#        if self.debug:
#            print "verin = relais n°: " + str(self.up)
#            print "durée levée verin: " + str(self.tabpompes[self.up - 1][7])
#        if self.up != 0:
#            timer = float(str(self.tabpompes[self.up - 1][7]))
#            self.service(int(self.up) + self.dep, SEQ_EVENT_NOTEON)
#            time.sleep(timer)
#            self.service(int(self.up) + self.dep, SEQ_EVENT_NOTEOFF)
        for i in range(len(analyse)):
            if int(float(analyse[i][1])) != 0:
                if self.debug:
                    print "on sert: " + str(analyse[i][0] + self.dep)
                self.service(analyse[i][0] + self.dep, SEQ_EVENT_NOTEON)
                time.sleep(float(analyse[i][1]))
                self.service(analyse[i][0] + self.dep, SEQ_EVENT_NOTEOFF)
                if self.debug:
                    print str(analyse[i][0] + self.dep) + " servi"
            pass
        if self.debug:
            print str(analyse) + " et servi !"
        self.status = "served"
        return self.status
        
    def findmidiport(self):
        outport = (0, 0)
        inport = (0, 0)
        for connections in self.connection_list():
            cname, cid, ports = connections
            # skip midi through
            if cname == 'Midi Through' or cname == self.clientname:
                continue
            for port in ports:
                pid = port[1]
                pinfo = self.get_port_info(pid, cid)
                miditype = pinfo['type']
                caps = pinfo['capability']
                if self.debug:
                    print(str(pid)+str(cid),pinfo, miditype, caps)
                if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT, SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_TYPE_PORT | SEQ_PORT_TYPE_HARDWARE | SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC) and caps in (SEQ_PORT_CAP_SUBS_WRITE | SEQ_PORT_CAP_WRITE, 127):
#                if  caps & (SEQ_PORT_CAP_SUBS_WRITE | SEQ_PORT_CAP_WRITE):
                    if self.debug:
                        print "Using outport: %s:%s" % (cname, pid)
                    outport = (cid, pid)
                    self.outClientId = cid
                    self.outPortId = pid
                if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT, SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_TYPE_PORT | SEQ_PORT_TYPE_HARDWARE | SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC) and caps in (SEQ_PORT_CAP_SUBS_READ | SEQ_PORT_CAP_READ, 127):
#                if  caps & (SEQ_PORT_CAP_SUBS_READ | SEQ_PORT_CAP_READ):
                    if self.debug:
                        print "Using inport: %s:%s" % (cname, pid)
                    inport = (cid, pid)
                    self.inClientId = cid
                    self.inPortId = pid        
        return [inport, outport]
    
    def test(self, startevent, stopevent):
        save = True
        elapsed = float('0.0000')
        for connections in self.connection_list():
            cname, cid, ports = connections
            # skip midi through
            print cname
            for port in ports:
                pid = port[1]
                pinfo = self.get_port_info(pid, cid)
                print pinfo
                #miditype = pinfo['type']
                caps = pinfo['capability']
                print hex(type)
                print hex(caps)
        while True:
            try:
                for event in self.receive_events(timeout=10069, maxevents=1):
                    if event.is_note_type:
                        if event.get_data()['note.note'] == startevent:
                            elapsed = time.time()
                            print "startevent catched " + str(elapsed)
                        elif event.get_data()['note.note'] == stopevent:
                            elapsed = time.time()
                            print "stopevent catched " + str(elapsed)
                            save = False
                            break
                        else:
                            elapsed = time.time()
                            print "note " + str(event.get_data()['note.note']) + " " + str(elapsed)
                    elif event.is_control_type:
                        print str(event.get_data())                
                    else:
                        print "unknown event"
                    
            finally:
                if save:
                    pass
                else:
                    print "break"
                    break
                
        print "exited"
                
if __name__ == "__main__":
    
    seq = sequencer()
    seq.clientname = "Pianocktail-test"
    seqId = seq.client_id
    outportId = seq.create_simple_port("pianocktail-out", SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC , SEQ_PORT_CAP_READ | SEQ_PORT_CAP_SUBS_READ)
    inportId = seq.create_simple_port("pianocktail-in", SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC , SEQ_PORT_CAP_WRITE | SEQ_PORT_CAP_SUBS_WRITE)
    #queueId = seq.create_queue("queue")
    print seq.name
    print seq.client_id
    print inportId
    print seq.streams
    #seq.start_queue(queueId)
    seq.connect_ports((128, 0), (seqId, inportId))
    print seq.connection_list()
    seq.test(36, 119)
    
