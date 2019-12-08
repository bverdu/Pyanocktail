#! /usr/bin/python2
# -*- coding: utf-8 -*-
'''
Created on 16 déc. 2012

@author: Bertrand Verdu

Standalone asynchrone module to capture  midi events and perform sequencer operations
Interactive mode to capture commands and fake midi notes from stdin
'''

from __future__ import print_function
from threading import Thread, Event
import select
import sys
from os import getpid, read
from time import time, sleep
from optparse import OptionParser
# from pyalsa.alsaseq import Sequencer, \
#     SeqEvent, \
#     SEQ_TIME_STAMP_REAL, \
#     SEQ_PORT_TYPE_MIDI_GENERIC, \
#     SEQ_PORT_TYPE_PORT, \
#     SEQ_PORT_TYPE_APPLICATION, \
#     SEQ_PORT_TYPE_HARDWARE, \
#     SEQ_PORT_CAP_SUBS_WRITE, \
#     SEQ_PORT_CAP_WRITE, \
#     SEQ_PORT_CAP_SUBS_READ, \
#     SEQ_PORT_CAP_READ, \
#     SEQ_EVENT_NOTE, \
#     SEQ_EVENT_NOTEON, \
#     SEQ_EVENT_NOTEOFF
from pyalsa.alsaseq import Sequencer, SeqEvent

SEQ_TIME_STAMP_REAL = 1
SEQ_PORT_TYPE_MIDI_GENERIC = 2
SEQ_PORT_TYPE_PORT = 524288
SEQ_PORT_TYPE_APPLICATION = 1048576
SEQ_PORT_TYPE_HARDWARE = 65536
SEQ_PORT_CAP_SUBS_WRITE = 64
SEQ_PORT_CAP_WRITE = 2
SEQ_PORT_CAP_SUBS_READ = 32
SEQ_PORT_CAP_READ = 1
SEQ_EVENT_NOTE = 5
SEQ_EVENT_NOTEON = 6
SEQ_EVENT_NOTEOFF = 7

options = {}
options[('-l', '--list')] = {'dest': 'list_type',
                             'action': 'store',
                             'type': 'choice',
                             'choices': ['i', 'o', 'io'],
                             'metavar': 'list_type',
                             'help': 'Liste les connexions midi'}
options[('-s', '--sequencer')] = {'dest': 'seq', 'action': 'store_true',
                                  'default': False, 'help': u'Démarre un séquenceur Midi'}
options[('-a', '--auto')] = {'dest': 'auto', 'action': 'store_true',
                             'default': False, 'help': u'Détection et Connexion automatique'}
options[('-n', '--name')] = {'dest': 'seq_name',
                             'default': 'pyanocktail', 'help': u'Nom du séquenceur Midi'}
options[('-f', '--file')] = {'dest': 'file_name',
                             'default': 'current.pckt', 'help': u'Fichier de destination'}


class player(Thread):

    def __init__(self, e_stop, seq):
        self.seq = seq
        self.notes = seq.records
        self.running = False
        q = self.seq.queue
        self.seq.start_queue(q)
        tempo, ppq = self.seq.queue_tempo(q)
        print('tempo: %d ppq: %d' % (tempo, ppq), file=sys.stderr)
        self.mdilist = []
        mdindex = []
        delay = float(self.notes[0].split()[0])
        for data in self.notes:
            note = data.split()
            if int(note[1]) == 1:
                try:
                    mdindex.index([int(note[2]), 1])
                    print('double noteon', file=sys.stderr)
                except:
                    mdindex.append([int(note[2]), 1])
                    self.mdilist.append([int(note[2]), int(note[3]), float(
                        note[0]) - delay, float(note[0]) - delay, 64])
            elif int(note[1]) == 0:
                try:
                    k = mdindex.index([int(note[2]), 1])
                    self.mdilist[k][3] = float(
                        note[0]) - delay - self.mdilist[k][3]
                    self.mdilist[k][4] = int(note[3])
                    mdindex[k] = [int(note[2]), 0]
                except:
                    print('orphan note_off', file=sys.stderr)
            else:
                print('controller event', file=sys.stderr)
        Thread.__init__(self, target=self.play, args=(e_stop,))

    def play(self, e_stop):
        self.running = True
        self.paused = False
        self.out = False
        if self.seq.outClientId:
            i = 0
            n = 0
            while len(self.mdilist) > 0:
                #             print('len of mdilist: %d' % len(self.mdilist))
                sleep(0.001)
                event = self.mdilist.pop(0)
                evt = SeqEvent(SEQ_EVENT_NOTE)
                evt.source = (self.seq.client_id, self.seq.outportId)
                evt.dest = (self.seq.outClientId, self.seq.outClientPort)
                evt.timestamp = SEQ_TIME_STAMP_REAL
                evt.time = float(event[2]) / 1000.000
        #                 print(event[3])
        #                 evt.set_data({'note.note' : event[0], 'note.velocity' : event[1], 'note.duration' : event[3]*t , 'note.off_velocity' : event[4]})
                evt.set_data({'note.note': event[0], 'note.velocity': event[1], 'note.duration': int(
                    event[3]), 'note.off_velocity': event[4]})
                evt.queue = self.seq.queue
        #             print('play event: %s %s' % (evt, evt.get_data()), file=sys.stderr)
                self.seq.output_event(evt)
                self.seq.drain_output()
                i += 1
                if i > 20:
                    n += 1
        #                 print('boucle %d' % n)
        #                 print('go')
                    self.seq.sync_output_queue()
                    if e_stop.is_set():
                        self.seq.stop_queue(self.seq.queue)
        #                     print("exit")
                        self.out = True
                        break
                    i = 0
        #         print("end of thread")
            if self.out == False:
                self.seq.sync_output_queue()
                self.seq.stop_queue(self.seq.queue)
        #         self.seq.delete_queue(q)
            self.running = False
            self.seq.playing = False
            print('0 Ready')
            e_stop.clear()
        else:
            print('0 Not Sequencer')

#     def stop(self, event):
#         self.running = False
#         self.mdilist = []
# #         event.set()
#     def pause(self, event):
#         if self.paused:
#             self.paused = False
# #             event.set()
#         else:
#             self.paused = True


class Seq(Sequencer):

    '''Main sequencer class with utility functions
    parameter: name of the sequencer'''

    def __init__(self, name):
        Sequencer.__init__(self)
        self.commands = {b'connect': self.connect, b'serve': self.serve, b'disconnect': self.disconnect_ports,
                         b'record': self.record, b'load': self.load, b'play': self.play, b'list': self.list, b'quit': self.quit}
        self.clientname = name
        self.queue = self.create_queue('Output_queue')
        self.inportId = None
        self.outportId = None
        self.outClientId = None
        test = 0
        while not self.make_seqs():
            test += 1
            if test > 5:
                print("Unable to create Sequencer", file=sys.stderr)
                break
            print("test: %d" % test, file=sys.stderr)


#         self.playerEvent = Event()
#         self.playerExitEvent = Event()

    def make_seqs(self):
        ret = True
        if not self.inportId:
            try:
                self.inportId = self.create_simple_port(
                    "pianocktail-in",
                    SEQ_PORT_TYPE_APPLICATION |
                    2,
                    SEQ_PORT_CAP_WRITE | SEQ_PORT_CAP_SUBS_WRITE)
            except SystemError as e:
                print("inport failed: %s" % str(e), file=sys.stderr)
                ret = False
        if not self.outportId:
            try:
                self.outportId = self.create_simple_port(
                    "pianocktail-out",
                    SEQ_PORT_TYPE_APPLICATION |
                    SEQ_PORT_TYPE_MIDI_GENERIC,
                    SEQ_PORT_CAP_READ | SEQ_PORT_CAP_SUBS_READ)
            except SystemError:
                print("outport failed", file=sys.stderr)
                ret = False
        return ret

    def list(self, list_type):
        '''list inputs, outputs or both midi ports on system
        parameters : i (input)
                     o (output)
                     io (both)
                     '''
        for connection in self.connection_list():
            cname, cid, ports = connection
#             print(ports)
            if cname == 'Midi Through':
                continue
            for port in ports:
                pid = port[1]
                try:
                    pinfo = self.get_port_info(pid, cid)
                except SystemError:
                    pinfo = self.get_port_info(pid, cid)
                miditype = pinfo['type']
                caps = pinfo['capability']
                if caps & SEQ_PORT_CAP_WRITE and list_type in (b'i', b'io'):
                    if miditype & SEQ_PORT_TYPE_MIDI_GENERIC:
                        print('4 Input: %s %s:%s' % (cname, cid, pid))
                if caps in (SEQ_PORT_CAP_SUBS_READ |
                            SEQ_PORT_CAP_READ, 127) \
                        and list_type in (b'o', b'io'):
                    if miditype in (SEQ_PORT_TYPE_MIDI_GENERIC,
                                    SEQ_PORT_TYPE_PORT,
                                    SEQ_PORT_TYPE_APPLICATION,
                                    SEQ_PORT_TYPE_HARDWARE,
                                    SEQ_PORT_TYPE_PORT |
                                    SEQ_PORT_TYPE_HARDWARE |
                                    SEQ_PORT_TYPE_MIDI_GENERIC,
                                    SEQ_PORT_TYPE_APPLICATION |
                                    SEQ_PORT_TYPE_MIDI_GENERIC):
                        print('4 Output: %s %s:%s' % (cname, cid, pid))

    def serve(self, pump_number, on_off):
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
        play.set_data({'note.note': int(pump_number), 'note.velocity': 64})
        print('2 ' + str(play) + " envoyé")
        self.output_event(play)
        self.drain_output()
        self.sync_output_queue()

    def record(self, param):
        if int(self.recording) != int(param):
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
            if self.playing:
                if self.paused:
                    self.paused = False
                    print("1 Playing")
                else:
                    print("3 Paused")
                    self.paused = True
            else:
                self.playerExitEvent = Event()
                self.playing = True
                self.paused = False
                self.player = player(self.playerExitEvent, self)
                print("1 Playing")
                self.player.start()
        else:
            print("0 Stopping")
            self.playerExitEvent.set()
            self.playing = False
            self.player.join()

    def load(self, filename):
        try:
            f = open(filename, 'r')
            self.records = f.readlines()
        except:
            print('Unable to open file: %s' % filename, file=sys.stderr)

    def _store_event(self, event):
        if self.recording:
            self.records.append(event)
            self.recordfile.append(event + '\n')

    def _write(self, note_list):
        f = open(self.filename, 'w+')
        f.writelines(note_list)
        f.close()
        print('2 file saved')

    def quit(self):
        sys.exit()

    def _handleCommand(self, command):
        #         print('handle cmd: %s' % command, file=sys.stderr)
        try:
            params = command.split()[1:]
            self.commands[command.split()[0]](*params)
        except Exception as err:
            print('unknown command: %s' % command, file=sys.stderr)

    def _handleMidiEvent(self, event, time_):
        event_time = time_ - self.start_time
#         try:
#             evt = str(int(event.type == SEQ_EVENT_NOTEON))+' '\
#             +str(event.get_data()['note.note'])+' '+str(event_time)
#         except AttributeError:
#             evt = str(int(event[0] == '1'))+' '+event[1:].strip('\n')+\
#             ' '+str(event_time)
        try:
            #             print(event.type == SEQ_EVENT_NOTEON, file=sys.stderr)
            #             print("type: %d" % event.type, file=sys.stderr)
            evt = str(event_time * 1000) + ' ' +\
                str(int(event.get_data()['note.velocity'] > 0)) + ' ' +\
                str(event.get_data()['note.note']) + ' ' +\
                str(event.get_data()['note.velocity'])
        except AttributeError:
            #             print(event[0] == b'1', file=sys.stderr)
            #             print(event[0], file=sys.stderr)
            evt = str(event_time * 1000) + ' ' +\
                str(int(chr(event[0]))) + ' ' +\
                (event[1:].strip(b'\n')).decode("utf8") + ' ' +\
                '64'
        except:
            print('got unknown event: %s at %s' %
                  (event, event_time), file=sys.stderr)
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
                try:
                    pinfo = self.get_port_info(pid, cid)
                except OverflowError:
                    pinfo = self.get_port_info(pid, cid)
                miditype = pinfo['type']
                caps = pinfo['capability']
                if miditype & SEQ_PORT_TYPE_MIDI_GENERIC and caps & SEQ_PORT_CAP_WRITE:
                    # if  caps & (SEQ_PORT_CAP_SUBS_WRITE |
                    # SEQ_PORT_CAP_WRITE):
                    print("2 Output_port: %s %s:%s" % (cname, cid, pid))
                    outport = (cid, pid)
#                    self.outClientId = cid
#                    self.outPortId = pid
                if miditype & SEQ_PORT_TYPE_MIDI_GENERIC and caps & SEQ_PORT_CAP_READ:
                    # if  caps & (SEQ_PORT_CAP_SUBS_READ | SEQ_PORT_CAP_READ):
                    print("2 Input_port: %s %s:%s" % (cname, cid, pid))
                    inport = (cid, pid)
#                    self.inClientId = cid
#                    self.inPortId = pid
        if inport != (0, 0):
            self.connect_ports(
                inport, (self.client_id, self.inportId), 0, 0, 1, 1)
            self.inClientId = outport[0]
            self.inClientPort = outport[1]
        if outport != (0, 0):
            self.connect_ports((self.client_id, self.outportId), outport)
            self.outClientId = outport[0]
            self.outClientPort = outport[1]

    def start(self, command_in, auto, filename):
        self.recording = False
        self.playing = False
        self.paused = False
        self.start_time = time()
        self.load(filename)
        poller = select.poll()
        self.filename = filename
        print('Sequenceur Midi %s started on pid %d' %
              (self.clientname, getpid()), file=sys.stderr)
        if auto:
            self.connect_auto()
        self.register_poll(poller, input=True, output=False)
        poller.register(command_in, select.POLLIN)
        while True:
            poller.poll()
            event_time = time()
            try:
                events = self.receive_events(timeout=1, maxevents=4)
                test = events[0]
            except IndexError:
                command = read(command_in, 20)
#                 print("444: %s" % command, file=sys.stderr)
                for c in command.split(b'\n'):
                    #                     print(c, file=sys.stderr)
                    if len(c) > 0:
                        if int(c[0]) < 58:
                            self._handleMidiEvent(c[:5], event_time)
                        else:
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
        seq.start(0, opts.auto, opts.file_name)
    del(seq)
