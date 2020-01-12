# -*- coding: utf-8 -*-
#! /usr/bin/python

#  This module contains all the variables, lists, load and save
# the settings
#
# Bertrand Verdu  08/08

# import MySQLdb
from pyanocktail.dbUtils import initdb
import os
import json


class mainConfig:

    notes = []
    pumps = []
    pumpsdb = []
    recipesdb = []
    cooks = []
    debug = False
    perf = 0
    dep = 49
    up = 0
    down = 0
    start = 36
    stop = 119
    cockt = 118
    panic = 117
    factor = 1
    reload = 116
    uppump = 0
    sysInport = 0
    sysOutport = 0
    downpump = 0
    statusevt = 115
    temoin_save = 0
    temoin_ready = 0
    temoin_analyse = 0
    temoin_error = 0
#     httpport = 8888
    preservice = None
    postservice = None
    old = 1
    alc = 0
    complexind = 0.5
    tristind = 1
    nervind = 1
    langage = 'fr'
#     dbtype = 'sqlite'
#     dbconnectstring= ''
    dbase = 'pianocktail'
    dbuser = 'piano'
    dbpwd = 'cocktail'
    theme = "none"
    dbsession = False
    extProgram = "scilab"
    list_params = ('debug', 'extProgram', 'sysInport',
                   'sysOutport', 'alc', 'complexind', 'tristind', 'nervind',
                   'factor', 'langage')

    def __init__(self, dirname, installdir, port, db=False):
        self.load(dirname, installdir)
        self.httpport = port
        if db:
            self.dbsession = self.dbconnect()
            self.dbsession.ingredients = None
            self.dbsession.pumps = None
            self.dbsession.cocktails = None
            self.dbsession.ingList = None
            self.dbsession.sysIngs = None
            self.dbsession.inputs = None
        self.configdir = dirname

    def dbconnect(self):
        try:
            dbtype = self.dbtype
            dbstring = self.dbconnectstring
        except:
            dbtype = 'sqlite'
            try:
                os.mkdir(os.path.join(os.path.abspath(self.installdir), 'db'))
            except:
                print("db path already created, skipping")
            dbstring = os.path.join(os.path.abspath(
                self.installdir), 'db', 'pianocktail.db')
        self.dbtype = dbtype
        self.dbconnectstring = dbstring
        try:
            if dbtype == 'sqlite':
                #                 if os.access(dbstring, os.F_OK) == False:
                #                     f = open(dbstring, 'w')
                #                     f.write()
                #                     f.close()
                if len(dbstring) > 0:
                    dbstring = '/' + dbstring
            print(dbtype + "://" + dbstring)
            return initdb(dbtype + "://" + dbstring, dbtype, self.debug)
        except Exception as err:
            print("db connection failed : %s" % err)

    def load(self, confdir, installdir):
        self.installdir = installdir
#         notesfile = os.path.join(confdir,'scripts','default.pckt')
#         setPumpfile = os.path.join(dirname,"default.pdb")
#         setCookfile = os.path.join(dirname,"default.rdb")
        print(confdir)
        try:
            configfile = os.path.join(confdir, "config")
            if os.path.exists(configfile):
                loadconffromfile(self, configfile)
            else:
                if not os.path.exists(confdir):
                    os.mkdir(confdir)
                saveConftofile(self, configfile)
        except IOError:
            configfile = os.path.join(
                os.path.expanduser("~/.pianocktail"), "config")
            if os.path.exists(configfile):
                loadconffromfile(self, configfile)
            else:
                saveConftofile(self, configfile)
        self.configfile = configfile

    def save(self, dirname):
        notesfile = os.path.join(dirname, "default.pckt")
        configfile = os.path.join(dirname, "config")
        savenotestofile(self.notes, notesfile)
        saveConftofile(self, configfile)

    def getseqparameters(self):
        params = dict()
        params['dep'] = self.dep
        params['start'] = self.start
        params['stop'] = self.stop
        params['cocktail'] = self.cockt
        params['panic'] = self.panic
        params['reload'] = self.reload
        params['up'] = self.up
        params['down'] = self.down
        params['readylight'] = self.temoin_ready
        params['recordlight'] = self.temoin_save
        params['analyselight'] = self.temoin_analyse
        params['perf'] = self.perf
        params['scriptpath'] = os.path.join(self.installdir, "scripts")
        params['extProgram'] = self.extProgram
        params['old'] = self.old
        params['alc'] = self.alc
        params['compexind'] = self.complexind
        params['tristind'] = self.tristind
        params['nervind'] = self.nervind
        params['factor'] = self.factor
        return params


def loadnotesfromfile(filename):

    notes = []
    dump = open(filename, 'r')
    for line in dump.readlines():
        if line.split()[1] == "1":
            notes.append([int(line.split()[0]), 1, int(
                line.split()[2]), int(line.split()[3])])
        elif line.split()[1] == "on":
            notes.append([int(line.split()[0]), 1, int(
                line.split()[2]), int(line.split()[3])])
        elif line.split()[1] == "0":
            notes.append([int(line.split()[0]), 0, int(
                line.split()[2]), int(line.split()[3])])
        elif line.split()[1] == "off":
            notes.append([int(line.split()[0]), 0, int(
                line.split()[2]), int(line.split()[3])])
        elif line.split()[1] == "5":
            notes.append([int(line.split()[0]), 2, int(
                line.split()[2]), int(line.split()[3])])
        elif line.split()[1] == "ctrl":
            notes.append([int(line.split()[0]), 2, int(
                line.split()[2]), int(line.split()[3])])
        else:
            notes.append([int(line.split()[0]), int(line.split()[1]),
                          int(line.split()[2]), int(line.split()[3])])
    dump.close
    return notes


def loadconffromfile(obj, filename):
    list_params = []
    emptyfile = True
    for line in open(filename, 'r').readlines():
        try:
            try:
                setattr(obj, line.split('=')[0], float(
                    line.split('=')[1].rstrip('\n')))
                print("digit: %s" % str(line.split('=')[1]).rstrip('\n'))
            except ValueError:
                if line.split('=')[0] == "debug":
                    if line.split('=')[1].rstrip('\n') == "False":
                        setattr(obj, 'debug', False)
                        #print("debug mode off")
                    else:
                        setattr(obj, 'debug', True)
                        print("debug mode on")
                else:
                    setattr(obj, line.split('=')[0], str(
                        line.split('=')[1]).rstrip('\n'))
                    if obj.debug:
                        print(line.split('=')[0] + ' ',
                              str(line.split('=')[1]).rstrip('\n'))
#             if str(line.split('=')[1]).rstrip('\n').isdigit():
#
#                 setattr(obj, line.split('=')[0], int(
#                     line.split('=')[1].rstrip('\n')))
#             else:
#                 if line.split('=')[0] == "debug":
#                     if line.split('=')[1].rstrip('\n') == "False":
#                         setattr(obj, 'debug', False)
#                         #print("debug mode off")
#                     else:
#                         setattr(obj, 'debug', True)
#                         print("debug mode on")
#                 else:
#                     setattr(obj, line.split('=')[0], str(
#                         line.split('=')[1]).rstrip('\n'))
#                     if obj.debug:
#                         print(line.split('=')[0] + ' ',
#                               str(line.split('=')[1]).rstrip('\n'))
            list_params.append(line.split('=')[0])
            emptyfile = False
        except:
            pass
    if not emptyfile:
        obj.list_params = list_params
        d = dict()
        for param in list_params:
            d[param] = str(getattr(obj, param))
        j = json.JSONEncoder().encode(d)
        f = open(filename + '.json', 'w+')
        f.write(j)
        f.close


def savenotestofile(notes, filename):

    dump = open(filename, 'w+')
    for i in range(len(notes)):
        if notes[i][1] == 1:
            dump.write(str(notes[i][0]) + " " + "1" + " " +
                       str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        elif notes[i][1] == 0:
            dump.write(str(notes[i][0]) + " " + "0" + " " +
                       str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        elif notes[i][1] == 2:
            dump.write(str(notes[i][0]) + " " + "5" + " " +
                       str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        else:
            dump.write(str(notes[i][0]) + " " + str(notes[i][1]) +
                       " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
    dump.close()


def saveConftofile(obj, filename):
    f = open(filename, 'w')
    for param in obj.list_params:
        # print(str(param))
        f.write(str(param) + "=" + str(getattr(obj, param)) + "\n")
    f.close()
