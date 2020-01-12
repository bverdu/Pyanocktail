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
from pyalsa.alsaseq import Sequencer, \
    SeqEvent, \
    SEQ_EVENT_NOTEON, \
    SEQ_EVENT_NOTEOFF, \
    SEQ_EVENT_CONTROLLER, \
    SEQ_EVENT_PGMCHANGE, \
    SEQ_BLOCK, \
    SequencerError
# from pyalsa.alsaseq import Sequencer, SeqEvent
#
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
# SEQ_EVENT_NOTEON = 6
# SEQ_EVENT_NOTEOFF = 7

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
#         q = self.seq.queue
        tempo, ppq = self.seq.queue_tempo(self.seq.queue)
        print('tempo: %d ppq: %d' % (tempo, ppq), file=sys.stderr)
        self.mdilist = []
        mdindex = {}
        delay = float(self.notes[0].split()[0])
        for data in self.notes:
            note = data.split()
            if int(note[1]) == 1:
                #                 try:
                #                     mdindex.index(int(note[2]))
                #                     print('double noteon', file=sys.stderr)
                #                 except:
                if int(note[2]) in mdindex:
                    mdindex[int(note[2])].append(len(self.mdilist))
                else:
                    mdindex[int(note[2])] = [len(self.mdilist)]
                self.mdilist.append([int(note[2]), int(note[3]), float(
                    note[0]) - delay, 500, 64])
                last = float(note[0]) - delay
            elif int(note[1]) == 0:
                try:
                    if int(note[2]) in mdindex:
                        i = mdindex[int(note[2])].pop()
                        self.mdilist[i][3] = float(
                            note[0]) - delay - self.mdilist[i][2]
                        self.mdilist[i][4] = int(note[3])
                        if len(mdindex[int(note[2])]) < 1:
                            #                             print("del %d from index" % int(note[2]),
                            #                                   file=sys.stderr)
                            del mdindex[int(note[2])]
#                     k = mdindex.index(int(note[2]))
#                     self.mdilist[k][3] = float(
#                         note[0]) - delay - self.mdilist[k][3]
#                     self.mdilist[k][4] = int(note[3])
#                     mdindex.pop(k)
#                     mdindex[k] = [int(note[2]), 0]
                    else:
                        #                 except ValueError:
                        print('orphan note_off: %d, index: %s' % (
                            int(note[2]), str(mdindex)), file=sys.stderr)
                except Exception as e:
                    print("error on line %d: %s" % (i, str(e)),
                          file=sys.stderr)
                    print("note: %s" % str(note), file=sys.stderr)
                    print("list: %s" % str(self.mdilist[i]), file=sys.stderr)
            else:
                #                 print('controller event', file=sys.stderr)
                if int(note[1]) == 3:
                    self.mdilist.append([-3, int(note[2]),
                                         float(note[0]) - delay, int(note[3]),
                                         int(note[4])])
                elif int(note[1]) == 4:
                    self.mdilist.append([-4, int(note[2]),
                                         float(note[0]) - delay, int(note[3])])
                else:
                    print('??', file=sys.stderr)
        Thread.__init__(self, target=self.play, args=(e_stop,))

    def play(self, e_stop):
        self.running = True
        self.paused = False
        self.out = False
#         self.seq.start_queue(self.seq.queue)
        self.seq.start_queue(0)
#         self.tmst = time() + (self.mdilist[-1][2] / 1000.00)
#         print("time: %d, tmst: %d, delta: %d" % (
#             time(), self.tmst, self.mdilist[-1][2] / 1000.00),
#             file=sys.stderr)
        if self.seq.outClientId:
            delay = float(self.notes[0].split()[0]) / 1000.00
            last = 0.0
            for n in self.notes:
                note = n.split()
#                 print(note, file=sys.stderr)
                if e_stop.is_set():
                    print("bye", file=sys.stderr)
                    break
                evtime = float(note[0]) / 1000.00 - delay
                if len(note) > 4:
                    evtype, evdata, evparam, evvalue = [
                        int(v) for v in note[1:]]
                else:
                    evtype, evdata, evparam = [int(v) for v in note[1:]]
                print(evdata, file=sys.stderr)
                sleep(evtime - last)
                last = evtime
                if evtype == 1:
                    evt = SeqEvent(6)  # Note On
                    evt.set_data({'note.note': evdata,
                                  'note.velocity': evparam})
                elif evtype == 0:
                    evt = SeqEvent(7)  # Note Off
                    evt.set_data({'note.note': evdata})
                elif evtype == 3:
                    evt = SeqEvent(10)  # CONTROL
                    evt.set_data({'control.channel': evdata,
                                  'control.param': evparam,
                                  'control.value': evvalue})
                elif evtype == 4:
                    evt = SeqEvent(11)  # PGMCHANGE
                    evt.set_data({'control.channel': evdata,
                                  'control.value': evparam})
                else:
                    print("Unknow Event: %d" % evtype, file=sys.stderr)
                    continue
                evt.source = (self.seq.client_id, self.seq.outportId)
                evt.dest = (self.seq.outClientId, self.seq.outClientPort)
                print('play event: %s %s' % (
                    evt, evt.get_data()), file=sys.stderr)
                self.seq.output_event(evt)
#                 self.seq.sync_output_queue()
                self.seq.drain_output()

#             i = 0
#             n = len(self.mdilist)
#             print(n, file=sys.stderr)
#             while len(self.mdilist) > 0:
#                 #             print('len of mdilist: %d' % len(self.mdilist))
#                 #                 sleep(0.001)
#                 event = self.mdilist.pop(0)
#                 note = False
#                 if event[0] > 0:
#                     note = True
#                     i += 1
#                     evt = SeqEvent(6)
#             #                 print(event[3])
#             #                 evt.set_data({'note.note' : event[0], 'note.velocity' : event[1], 'note.duration' : event[3]*t , 'note.off_velocity' : event[4]})
#                     evt.set_data({'note.note': event[0],
#                                   'note.velocity': event[1]})
# #                                   'note.duration': int(event[3]),
# #                                   'note.off_velocity': event[4]})
#                 else:
#                     if event[0] == -3:
#                         evt = SeqEvent(10)  # Controler
# #                         print("channel: %d, param: %d, value: %d" % (event[1],
# #                                                                      event[3],
# #                                                                      event[4]),
# #                         file=sys.stderr)
#                         try:
#                             evt.set_data({'control.channel': event[1],
#                                           'control.param': event[3],
#                                           'control.value': event[4]})
# #                             print("param: %d, value: %d" % (event[3], event[4]),
# #                                   file=sys.stderr)
#                         except TypeError:
#                             print("ERR param: %d, value: %d" % (event[3], event[4]),
#                                   file=sys.stderr)
#                             evt.set_data({'control.channel': 1,
#                                           'control.param': 1,
#                                           'control.value': 1})
#                     elif event[0] == -4:
#                         evt = SeqEvent(11)  # PGMCHANGE
#                         try:
#                             evt.set_data({'control.channel': event[1],
#                                           'control.value': event[3]})
# #                             print("value: %d" % event[3], file=sys.stderr)
#                         except TypeError:
#                             print("ERR value: %d" % event[3], file=sys.stderr)
#                             evt.set_data({'control.channel': event[1],
#                                           'control.value': 1})
# #                 evt.source = (self.seq.client_id, self.seq.outportId)
#                 evt.dest = (self.seq.outClientId, self.seq.outClientPort)
# #                 evt.time = None
# #                 evt.timestamp = SEQ_TIME_STAMP_REAL
# #                 evt.time = float(event[2]) / 1000.000
# #                 evt.queue = self.seq.queue
#                 print('play event: %s %s' %
#                       (evt, evt.get_data()), file=sys.stderr)
#                 self.seq.output_event(evt)
#                 self.seq.drain_output()
#                 sleep(float(event[2]) / 1000.000)
# #                 if note:
# #                     evt = SeqEvent(7)
# #             #                 print(event[3])
# #             #                 evt.set_data({'note.note' : event[0], 'note.velocity' : event[1], 'note.duration' : event[3]*t , 'note.off_velocity' : event[4]})
# #                     evt.set_data({'note.note': event[0]})
# #                     evt.dest = (self.seq.outClientId, self.seq.outClientPort)
# #                     self.seq.output_event(evt)
# #                     self.seq.drain_output()
# #                 if n < 1000 and started:
# #                     sleep(1)
# #                     self.seq.drain_output()
# #                 self.seq.drain_output()
#
# #                 if i > (n / 20):
# #                     print(".", file=sys.stderr)
# # #                     sleep(1)
# # #                     self.seq.sync_output_queue()
# #
# #                     i = 0
#
#
# #                     print("drain", file=sys.stderr)
# #                     self.seq.drain_output()
# #                     i = 0
#                 if e_stop.is_set():
#                     print("bye", file=sys.stderr)
#                     #                     self.seq.drain_output()
#                     #                     self.seq.sync_output_queue()
#                     #                     self.seq.stop_queue(self.seq.queue)
#                     #                     self.out = True
#                     break
# #                 try:
# #                     self.seq.drain_output()
# #                 except SequencerError:
# #                     print("Seq error on drain", file=sys.stderr)
# #                     pass
# #                 i += 1
# #                 if i > 100:
# #
# #                     n += 1
# #                     print('boucle %d, i= %d' % (n, i), file=sys.stderr)
# #         #                 print('go')
# #                     i = 0
# #                     self.seq.sync_output_queue()
# #                     if e_stop.is_set():
# #                         self.seq.stop_queue(self.seq.queue)
# #         #                     print("exit")
# #                         self.out = True
# #                         break
# #                     i = 0
#         #         print("end of thread")
#
# #             if self.out == False:
# #             sleep(5)
# #             try:
# #                 self.seq.drain_output()
# #                 sleep(0.1)
# #             except SequencerError:
# #                 print("oups...", file=sys.stderr)
# #                 self.seq.sync_output_queue()
#
# #                 self.seq.sync_output_queue()
# #             sleep(10)
#             while time() < self.tmst:
#                 if e_stop.is_set():
#                     break
#                 self.seq.drain_output()
            if not e_stop.is_set():
                self.seq.sync_output_queue()
                if not e_stop.is_set():
                    self.seq.drain_output()

            while True:
                try:
                    self.seq.stop_queue(self.seq.queue)
                    print("stopped", file=sys.stderr)
                    break
                except SequencerError:
                    pass
#                     print("oups 2...", file=sys.stderr)
        #         self.seq.delete_queue(q)
            self.running = False
            self.seq.playing = False
            print('0 Ready')
            e_stop.clear()
        else:
            print('0 Not Sequencer')

#         self.seq = None

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

    def __init__(self, name, blocking=False):
        #         Sequencer.__init__(self)
        if blocking:
            Sequencer.__init__(self, mode=SEQ_BLOCK)
        else:
            Sequencer.__init__(self)
#         Sequencer.__init__(self, mode=SEQ_BLOCK)
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
        print('4 File saved')

    def quit(self):
        sys.exit()

    def _handleCommand(self, command):
        #         print('handle cmd: %s' % command, file=sys.stderr)
        try:
            params = command.split()[1:]
            self.commands[command.split()[0]](*params)
        except IndexError:
            print('unknown command: %s' % command, file=sys.stderr)

    def _handleMidiEvent(self, event, time_):
        event_time = (time_ - self.start_time) * 1000
#         try:
#             evt = str(int(event.type == SEQ_EVENT_NOTEON))+' '\
#             +str(event.get_data()['note.note'])+' '+str(event_time)
#         except AttributeError:
#             evt = str(int(event[0] == '1'))+' '+event[1:].strip('\n')+\
#             ' '+str(event_time)
        try:
            #             print(event.type == SEQ_EVENT_NOTEON, file=sys.stderr)
            #             print("type: %d" % event.type, file=sys.stderr)
            d = event.get_data()
            if event.type in (SEQ_EVENT_NOTEON, SEQ_EVENT_NOTEOFF):
                if d['note.velocity'] > 0:
                    evt = "%d %d %d %d" % (event_time,
                                           int(event.type == SEQ_EVENT_NOTEON),
                                           d['note.note'],
                                           d['note.velocity'])
#                     evt = str(event_time * 1000) + ' ' +\
#                         str(int(event.type == SEQ_EVENT_NOTEON)) + ' ' +\
#                         str(event.get_data()['note.note']) + ' ' +\
#                         str(event.get_data()['note.velocity'])
                    print("Note: %s" % ("ON" if event.type == SEQ_EVENT_NOTEON
                                        else "OFF"), file=sys.stderr)
                else:
                    evt = "%d 0 %d 0" % (event_time,
                                         d['note.note'])
                    print("Note: %s" % "OFF (velocity = 0)", file=sys.stderr)
            elif event.type == SEQ_EVENT_CONTROLLER:
                evt = "%d 3 %d %d %d" % (event_time,
                                         d['control.channel'],
                                         d['control.param'],
                                         d['control.value'])
                print('CTRL event: %s : %s' %
                      (event, str(event.get_data())), file=sys.stderr)
            elif event.type == SEQ_EVENT_PGMCHANGE:
                evt = "%d 4 %d %d" % (event_time,
                                      d['control.channel'],
                                      d['control.value'])
            else:
                print('got unknown event: %s : %s' %
                      (event, str(event.get_data())), file=sys.stderr)
                return

#                 evt = str(event_time * 1000) + ' ' +\
#                     str(int(event.get_data()['note.velocity'] > 0)) + ' ' +\
#                     str(event.get_data()['note.note']) + ' ' +\
#                     str(event.get_data()['note.velocity'])
#                 print("type: %d %s" % (event.type, str(event.type)),
#                       file=sys.stderr)
#                 print("my types: %d %s, %d %s" % (SEQ_EVENT_NOTEON,
#                                                   str(SEQ_EVENT_NOTEON),
#                                                   SEQ_EVENT_NOTEOFF,
#                                                   str(SEQ_EVENT_NOTEOFF)),
#                       file=sys.stderr)
        except AttributeError:
            #             print(event[0] == b'1', file=sys.stderr)
            #             print(event[0], file=sys.stderr)
            evt = str(event_time) + ' ' +\
                str(int(chr(event[0]))) + ' ' +\
                (event[1:].strip(b'\n')).decode("utf8") + ' ' +\
                '64'
        except KeyError:
            print('got wrong event: %s : %s' %
                  (event, str(event.get_data())), file=sys.stderr)
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
            print(ports)
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
        print('File: %s ' % self.filename, file=sys.stderr)
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
