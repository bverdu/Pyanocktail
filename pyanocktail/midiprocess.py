#! /usr/bin/python2
# -*- coding: utf-8 -*-
'''
Created on 16 déc. 2012

@author: Bertrand Verdu

Standalone asynchrone module to capture  midi events and perform sequencer operations
Interactive mode to capture commands and fake midi notes from stdin
'''

from __future__ import print_function
from threading import Thread
import select
import sys
from os import getpid, read
from time import time, sleep
from optparse import OptionParser
from pyalsa.alsaseq import Sequencer, \
                            SeqEvent, \
                            SEQ_TIME_STAMP_REAL, \
                            SEQ_PORT_TYPE_MIDI_GENERIC, \
                            SEQ_PORT_TYPE_PORT, \
                            SEQ_PORT_TYPE_APPLICATION, \
                            SEQ_PORT_TYPE_HARDWARE, \
                            SEQ_PORT_CAP_SUBS_WRITE, \
                            SEQ_PORT_CAP_WRITE, \
                            SEQ_PORT_CAP_SUBS_READ, \
                            SEQ_PORT_CAP_READ, \
                            SEQ_EVENT_NOTE, \
                            SEQ_EVENT_NOTEON, \
                            SEQ_EVENT_NOTEOFF

options = {}
options[('-l', '--list')] = {'dest':'list_type',
                             'action':'store',
                             'type':'choice',
                             'choices':['i','o','io'],
                             'metavar':'list_type',
                             'help':'Liste les connexions midi'}
options[('-s', '--sequencer')] = {'dest':'seq', 'action':'store_true', 
                                  'default':False, 'help':u'Démarre un séquenceur Midi'}
options[('-a', '--auto')] = {'dest':'auto', 'action':'store_true',
                             'default':False, 'help':u'Détection et Connexion automatique'}
options[('-n', '--name')] = {'dest':'seq_name', 'default':'pyanocktail', 'help':u'Nom du séquenceur Midi'}
options[('-f', '--file')] = {'dest':'file_name', 'default':'current.pckt', 'help':u'Fichier de destination'}

class player(Thread):
    
    def __init__(self, seq, notes):
        self.seq=seq
        self.notes = notes
        self.running = False
        Thread.__init__(self)
        
    def run(self):
        self.running = True
        self.paused = False
        q = self.seq.queue
        self.seq.start_queue(q)
        tempo, ppq = self.seq.queue_tempo(q)
        print('tempo: %d ppq: %d' % (tempo, ppq), file=sys.stderr)
        mdilist = []
        mdindex = []
        delay = float(self.notes[0].split()[0])
        for data in self.notes:
            note = data.split()
            if int(note[1]) == 1:
                try:
                    mdindex.index([int(note[2]),1])
                    print('double noteon', file=sys.stderr)
                except:
                    mdindex.append([int(note[2]),1])
                    mdilist.append([int(note[2]), int(note[3]), float(note[0])-delay, float(note[0])-delay,64])
            elif int(note[1]) == 0:
                try:
                    k = mdindex.index([int(note[2]),1])
                    mdilist[k][3]=float(note[0])-delay -mdilist[k][3]
                    mdilist[k][4]=int(note[3])
                    mdindex[k] = [int(note[2]),0]
                except:
                    print('orphan note_off', file=sys.stderr)
            else:
                print('controller event', file=sys.stderr)
        i = 0
        for event in mdilist:
            if self.running:
                while self.paused:
                    sleep(0.5)
                evt = SeqEvent(SEQ_EVENT_NOTE)
                evt.source = (self.seq.client_id, self.seq.outportId)
                evt.dest = (self.seq.outClientId, self.seq.outClientPort)
                evt.timestamp = SEQ_TIME_STAMP_REAL
                evt.time = float(event[2])/1000.000
#                 print(event[3])
    #                 evt.set_data({'note.note' : event[0], 'note.velocity' : event[1], 'note.duration' : event[3]*t , 'note.off_velocity' : event[4]})
                evt.set_data({'note.note' : event[0], 'note.velocity' : event[1], 'note.duration' : int(event[3]) , 'note.off_velocity' : event[4]})
                evt.queue = q
                print('play event: %s %s' % (evt, evt.get_data()), file=sys.stderr)
                self.seq.output_event(evt)
                self.seq.drain_output()
                if self.running == False:
                    break
                i += 1
                if i > 20:
                    self.seq.sync_output_queue()
                    i = 0
                        
        if self.running:
            self.seq.sync_output_queue()
        self.seq.stop_queue(q)
#         self.seq.delete_queue(q)
        self.running = False
        self.seq.playing = False
        print('0 Ready')
    def stop(self):
        self.running = False
    def pause(self):
        if self.paused:
            self.paused = False
        else:
            self.paused = True

class Seq(Sequencer):
    
    '''Main sequencer class with utility functions
    parameter: name of the sequencer'''    
    
    def __init__(self,name):
        Sequencer.__init__(self)
        self.commands = {'connect':self.connect,'serve':self.serve
                ,'disconnect':self.disconnect_ports,'record':self.record
                ,'load':self.load, 'play':self.play
                ,'list':self.list,'quit':self.quit}
        self.clientname = name
        self.queue = self.create_queue('Output_queue')
        self.inportId = self.create_simple_port("pianocktail-in", 
                                                SEQ_PORT_TYPE_APPLICATION |
                                                SEQ_PORT_TYPE_MIDI_GENERIC ,
                                                SEQ_PORT_CAP_WRITE | SEQ_PORT_CAP_SUBS_WRITE)
        self.outportId = self.create_simple_port("pianocktail-out",
                                                 SEQ_PORT_TYPE_APPLICATION |
                                                 SEQ_PORT_TYPE_MIDI_GENERIC ,
                                                 SEQ_PORT_CAP_READ | SEQ_PORT_CAP_SUBS_READ)
        
    def list(self,list_type):
        '''list inputs, outputs or both midi ports on system
        parameters : i (input)
                     o (output)
                     io (both)
                     '''
        for connection in self.connection_list():
            cname, cid, ports = connection
#            print(ports)
            if cname == 'Midi Through':
                    continue
            for port in ports:
                pid = port[1]
                pinfo = self.get_port_info(pid, cid)
                miditype = pinfo['type']
                caps = pinfo['capability']
                if caps in (SEQ_PORT_CAP_SUBS_WRITE | 
                            SEQ_PORT_CAP_WRITE, 127) \
                            and list_type in ('i','io'):
                    if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, 
                                    SEQ_PORT_TYPE_PORT,
                                    SEQ_PORT_TYPE_APPLICATION,
                                    SEQ_PORT_TYPE_HARDWARE,
                                    SEQ_PORT_TYPE_PORT | 
                                    SEQ_PORT_TYPE_HARDWARE | 
                                    SEQ_PORT_TYPE_MIDI_GENERIC,
                                    SEQ_PORT_TYPE_APPLICATION |
                                    SEQ_PORT_TYPE_MIDI_GENERIC): 
                        print('4 Input: %s %s:%s' %(cname, cid, pid))
                if caps in (SEQ_PORT_CAP_SUBS_READ |
                                    SEQ_PORT_CAP_READ, 127) \
                                    and list_type in ('o','io'):
                    if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, 
                                    SEQ_PORT_TYPE_PORT,
                                    SEQ_PORT_TYPE_APPLICATION,
                                    SEQ_PORT_TYPE_HARDWARE,
                                    SEQ_PORT_TYPE_PORT | 
                                    SEQ_PORT_TYPE_HARDWARE | 
                                    SEQ_PORT_TYPE_MIDI_GENERIC,
                                    SEQ_PORT_TYPE_APPLICATION |
                                    SEQ_PORT_TYPE_MIDI_GENERIC): 
                        print('4 Output: %s %s:%s' %(cname, cid, pid))
                        
    def serve(self,pump_number,on_off):
        '''send midi note to output client
        parameters:
            pump_number : note
            on_off : note type (0 for NOTEOFF, 1 for NOTEON)
            '''
        if int(on_off) == 1:
            miditype = SEQ_EVENT_NOTEON
        else:
            miditype = SEQ_EVENT_NOTEOFF
        play = SeqEvent(miditype)
        play.source = (self.client_id, 1)
        print("4 source = %s" % str(self.client_id))
        try:
            play.dest = (self.outClientId, self.outClientPort)
            print("4 destination = %s" % str(self.outClientId))
        except:
            print("No output connexion, exiting", file=sys.stderr)
            return
        play.queue = self.queue
        play.set_data({'note.note' : int(pump_number), 'note.velocity' : 64})
        print('2 ' + str(play) + " envoyé")
        self.output_event(play)
        self.drain_output()
        self.sync_output_queue()
    
    def record(self,param):
        if int(self.recording) != int(param) :
            if int(param) == 0:
                self.recording = False
                self._write(self.recordfile)
                print('0 Recorded')
            else:
                self.start_time = time()
                self.records = []
                self.recordfile = []
                self.recording = True
                print('1 Recording')

                
    def play(self, state):
        if int(state) == 1:
            if self.playing :
                print("3 Pause")
                self.player.pause()
            else:
                print("1 Playing")
                self.player = player(self, self.records)
                self.player.start()
                self.playing = True
        else:
            print("0 Stopped")
            try:
                self.player.stop()
                self.player.join()
            except:
                print('player already stopped', file=sys.stderr)
            self.playing = False
        
    def load(self, filename):
        try:
            f = open(filename, 'r')
            self.records = f.readlines
        except:
            print('Unable to open file: %s' % filename, file=sys.stderr)
        
    def _store_event(self,event):
        if self.recording:
            self.records.append(event)
            self.recordfile.append(event+'\n')
            
    def _write(self,note_list):
        f = open(self.filename,'w+')
        f.writelines(note_list)
        f.close()
        print('2 file saved')
        
    def quit(self):
        sys.exit()
        
    def _handleCommand(self,command):
        try:
            params = command.split()[1:]
            self.commands[command.split()[0]](*params)
        except Exception as err:
            print(err)
            print('unknown command', file=sys.stderr)
            
    def _handleMidiEvent(self,event,time_):
        event_time = time_ - self.start_time
#         try:
#             evt = str(int(event.type == SEQ_EVENT_NOTEON))+' '\
#             +str(event.get_data()['note.note'])+' '+str(event_time)
#         except AttributeError:
#             evt = str(int(event[0] == '1'))+' '+event[1:].strip('\n')+\
#             ' '+str(event_time)
        try:
            evt = str(event_time*1000)+' '+\
            str(int(event.type == SEQ_EVENT_NOTEON))+' '+\
            str(event.get_data()['note.note'])+' '+\
            str(event.get_data()['note.velocity'])
        except AttributeError:
            evt = str(event_time*1000)+' '+\
            str(int(event[0] == '1'))+' '+\
            event[1:].strip('\n')+' '+\
            '64'
        except:
            print('got unknown event: %s at %s' %(event,event_time), file=sys.stderr)
            return
        print(evt, file=sys.stderr)
        self._store_event(evt)
        
    def connect(self, source, dest):
        try:
            self.connect_ports(source, dest, 0, 0, 1, 1)
        except Exception as e:
            print('Connection Error: ' % e.message, file=sys.stderr)
            return
        if source == (self.client_id, self.outportId):
            name = self.get_client_info(dest[0])
            self.outClientId, self.outClientPort = dest
            print("2 Output_port: %s %s:%s" % (name, dest[0], dest[1]))
        elif dest == (self.client_id, self.outportId):
            name = self.get_client_info(source[0])
            self.inClientId, self.inClientPort = source
            print("2 Input_port: %s %s:%s" % (name, source[0], source[1]))
            
    def connect_auto(self):
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
                if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT, SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_TYPE_PORT | SEQ_PORT_TYPE_HARDWARE | SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC) and caps in (SEQ_PORT_CAP_SUBS_WRITE | SEQ_PORT_CAP_WRITE, 127):
#                if  caps & (SEQ_PORT_CAP_SUBS_WRITE | SEQ_PORT_CAP_WRITE):
                    print("2 Output_port: %s %s:%s" % (cname, cid, pid))
                    outport = (cid, pid)
#                    self.outClientId = cid
#                    self.outPortId = pid
                if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_PORT, SEQ_PORT_TYPE_APPLICATION, SEQ_PORT_TYPE_HARDWARE, SEQ_PORT_TYPE_PORT | SEQ_PORT_TYPE_HARDWARE | SEQ_PORT_TYPE_MIDI_GENERIC, SEQ_PORT_TYPE_APPLICATION | SEQ_PORT_TYPE_MIDI_GENERIC) and caps in (SEQ_PORT_CAP_SUBS_READ | SEQ_PORT_CAP_READ, 127):
#                if  caps & (SEQ_PORT_CAP_SUBS_READ | SEQ_PORT_CAP_READ):
                    print("2 Input_port: %s %s:%s" % (cname, cid, pid))
                    inport = (cid, pid)
#                    self.inClientId = cid
#                    self.inPortId = pid
        if inport != (0, 0):
                self.connect_ports(inport, (self.client_id, self.inportId), 0, 0, 1, 1)
                self.inClientId = outport[0]
                self.inClientPort = outport[1] 
        if outport != (0, 0):
                self.connect_ports((self.client_id, self.outportId), outport)
                self.outClientId = outport[0]
                self.outClientPort = outport[1]       
                        
    def start(self,command_in,auto,filename):
        self.recording = False
        self.playing = False
        self.start_time = time()
        poller = select.poll()
        self.filename = filename
        print('Sequenceur Midi %s started on pid %d' % (self.clientname, getpid()), file=sys.stderr)
        if auto:
            self.connect_auto()
        self.register_poll(poller, input=True, output=False)
        poller.register(command_in,select.POLLIN)
        while True:
            poller.poll()
            event_time = time()
            try:
                events = self.receive_events(timeout = 1, maxevents = 4)
                test = events[0]
            except IndexError:
                command = read(command_in,20)
                print(command, file=sys.stderr)
                for c in command.split('\n'):
                    if len(c)>0:
                        try :
                            test=int(c[0])
                            self._handleMidiEvent(c[:5], event_time)
                        except ValueError:
                            self._handleCommand(c)
                            
            else:
                for event in events:
                    self._handleMidiEvent(event, event_time)

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [options] ')
    for param, option in options.items():
        parser.add_option(*param, **option)
    opts, args = parser.parse_args()
    seq = Seq(opts.seq_name)
    if opts.list_type:
        seq.list(opts.list_type)
    if opts.seq:
        seq.start(0,opts.auto,opts.file_name)
    del(seq)
    