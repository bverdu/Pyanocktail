# -*- coding: utf-8 -*-
#! /usr/bin/python

#  This module contains all the variables, lists, load and save
# the settings
#                    
# Bertrand Verdu  08/08

import bsddb3
import MySQLdb
import os
import json

class defaultConf:
    
    notes = []
    pumps = []
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
    httpport = 8888
    old = 1
    alc = 0
    complexind = 0.5
    tristind = 1
    nervind = 1
    dbase = 'pianocktail'
    dbuser = 'piano'
    dbpwd = 'cocktail'
    theme = "none"
    installdir = "/home/babe/Projets/eclipse/Pyanocktaild/src/"
    list_params = ('debug','dep','up','down','start','stop','cockt','panic','reload','uppump','downpump','statusevt','temoin_save','temoin_ready','temoin_analyse','temoin_error','httpport','theme','installdir','perf','sysInport','sysOutport','alc','complexind','tristind','nervind')
    def __init__(self,dirname):
        self.maindb = self.dbconnect()
        self.load(dirname)
        self.configdir = dirname
    def dbconnect(self):
        try:
            return MySQLdb.connect(user=self.dbuser,passwd=self.dbpwd,db=self.dbase)
        except Exception,err:
            return False
            print("mysql connection failed : "+err.message)
    def refreshdb(self):
        status = False
        self.maindb = self.dbconnect()
        if self.maindb:
            try:
                self.pumpsdb,self.downpumpdb,self.uppumpdb = loadPumpsfromdb(self.maindb,self.debug)
                self.recipesdb = loadRecipesfromdb(self.maindb,self.debug)
                self.maindb.close()
                status = True
            except Exception,err:
                print("RefreshDB Error: "+err.message)
        return status
    def writePumpdb(self,rows):
        status = False
        self.maindb = self.dbconnect()
        if self.maindb:
            ing = self.maindb.cursor(MySQLdb.cursors.DictCursor)
            for row in rows:
                try:
                    if self.debug:
                        print("Insert:\n"+row['name']+"\n"+row['deg']+"\n"+row['pump']+"\n"+row['time']+"\n")
                    write = ing.execute('''INSERT INTO ing 
                    SET name = %s, deg = %s, pump = %s, time= %s 
                    ON DUPLICATE KEY UPDATE 
                    deg = %s, pump = %s, time= %s ''',
                    (row['name'],row['deg'],row['pump'],row['time']
                     ,row['deg'],row['pump'],row['time']))
                    if self.debug:
                        print(str(write)+"rows wrote\n")
                    status = True
                except Exception,err:
                    print("Insert or Update Error: "+err.message+"\n")
                    print("Insert or Update Error: "+str(err)+"\n")
                    status = False
                    break
            self.maindb.close()
        else:
            status = False
        if status:
            return self.refreshdb()
        else:
            return False
    def writeRecipesdb(self,dictrow):
        status = False
        self.maindb = self.dbconnect()
        if self.maindb:
            ing = self.maindb.cursor(MySQLdb.cursors.DictCursor)
            for row in dictrow:
                try:
                    write = ing.execute('''INSERT INTO cocktail 
                    SET name = %s, ing1 = %s, qte1 = %s, ing2 = %s, qte2 = %s
                    , ing3 = %s, qte3 = %s, ing4= %s, qte4= %s, ing5 = %s, qte5 = %s
                    ,ing6 = %s, qte6 = %s, tristesse = %s, nerf = %s
                    ON DUPLICATE KEY UPDATE 
                    ing1 = %s, qte1 = %s, ing2 = %s, qte2 = %s
                    , ing3 = %s, qte3 = %s, ing4= %s, qte4= %s, ing5 = %s, qte5 = %s
                    ,ing6 = %s, qte6 = %s, tristesse = %s, nerf = %s ''',
                    (row['name'], row['ing1'], row['qte1'], row['ing2'], row['qte2'], row['ing3'], 
                     row['qte3'], row['ing4'], row['qte4'], row['ing5'], row['qte5'], row['ing6'],
                     row['qte6'], row['tristesse'], row['nerf'], 
                     row['ing1'], row['qte1'], row['ing2'], row['qte2'], row['ing3'], row['qte3'], 
                     row['ing4'], row['qte4'], row['ing5'], row['qte5'], row['ing6'], row['qte6'], 
                     row['tristesse'], row['nerf']))
                    if self.debug:
                        print(str(write)+"rows wrote\n")
                    status = True
                except Exception,err:
                    print("Insert or Update Error: "+err.message+"\n")
                    print("Insert or Update Error: "+str(err)+"\n")
                    status = False
                    break
            self.maindb.close()
        else:
            status = False
        if status:
            return self.refreshdb()
        else:
            return False
    def delRecipesdb(self,dictkey):
        status = False
        self.maindb = self.dbconnect()
        if self.maindb:
            ing = self.maindb.cursor(MySQLdb.cursors.DictCursor)
            for key in dictkey:
                try:
                    write = ing.execute('''DELETE FROM cocktail WHERE name = %s''',(key))
                    if self.debug:
                        print(str(write)+"rows deleted\n")
                    status = True
                except Exception,err:
                    print("Delete Error: "+err.message+"\n")
                    print("Delete Error: "+str(err)+"\n")
                    status = False
                    break
            self.maindb.close()
        else:
            status = False
        if status:
            return self.refreshdb()
        else:
            return False
    def getdebug(self):
        return self.debug
        print self.debug
    def getdep(self):
        return self.dep
    def getup(self):
        return self.up
    def getdown(self):
        return self.down
    def getstart(self):
        return self.start
    def getstop(self):
        return self.stop
    def getcockt(self):
        return self.cockt
    def getpanic(self):
        return self.panic
    def getreload(self):
        return self.reload
    def getstatusevt(self):
        return self.statusevt
    def getrecordled(self):
        return self.temoin_save
    def getreadyled(self):
        return self.temoin_ready
    def getcocktailled(self):
        return self.temoin_analyse
    def geterrorled(self):
        return self.temoin_error
    def getpumps(self):
        return self.pumps
    def getnotes(self):
        return self.notes
    def getcooks(self):
        return self.cooks
    def load(self,dirname):
        notesfile = os.path.join(dirname,"default.pckt")
        setPumpfile = os.path.join(dirname,"default.pdb")
        setCookfile = os.path.join(dirname,"default.rdb")
        configfile = os.path.join(dirname,"config")
        if os.path.exists(configfile):  
            loadconffromfile(self,configfile)
        if os.path.exists(notesfile):  
            self.notes = loadnotesfromfile(notesfile)
        if os.path.exists(setPumpfile):
            self.pumps,self.downpump,self.uppump = loadPumpsfromfile(setPumpfile,self.debug)  
        else:
            for i in range(0,32):
                self.pumps.append(['vide','0','0','0','4','0','0','0.0'])
        if os.path.exists(setCookfile):
            self.cooks = loadCooksfromfile(setCookfile)
        else:
            self.cooks.append(['vide',['0','sans'],['0','sans'],['0','sans'],['0','sans'],['0','sans'],['0','sans'],['0','sans']])
        if self.maindb:
            self.pumpsdb,self.downpumpdb,self.uppumpdb = loadPumpsfromdb(self.maindb,self.debug)
            self.recipesdb = loadRecipesfromdb(self.maindb,self.debug)
            self.maindb.close()
            
    def save(self,dirname):
        notesfile = os.path.join(dirname,"default.pckt")
        setPumpfile = os.path.join(dirname,"default.pdb")
        setCookfile = os.path.join(dirname,"default.rdb")
        configfile = os.path.join(dirname,"config")
        savenotestofile(self.notes,notesfile)
        savePumpstofile(self.pumps,setPumpfile)
        saveConftofile(self,configfile)
        saveCookstofile(self.cooks,setCookfile)
        
    def getseqparameters(self):
        params = dict()
        params['dep']= self.dep
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
        params['scriptpath'] = os.path.join(self.installdir,"scripts2")
        params['old'] = self.old 
        params['alc'] = self.alc
        params['compexind'] = self.complexind
        params['tristind'] = self.tristind
        params['nervind'] = self.nervind
        return params
                
def loadnotesfromfile(filename):

    notes = []
    dump = open(filename,'r')
    for line in dump.readlines():
        if line.split()[1] == "1":
            notes.append([int(line.split()[0]),1,int(line.split()[2]),int(line.split()[3])])
        elif line.split()[1] == "on":
            notes.append([int(line.split()[0]),1,int(line.split()[2]),int(line.split()[3])])
        elif line.split()[1] == "0":
            notes.append([int(line.split()[0]),0,int(line.split()[2]),int(line.split()[3])])
        elif line.split()[1] == "off":
            notes.append([int(line.split()[0]),0,int(line.split()[2]),int(line.split()[3])])
        elif line.split()[1] == "5":
            notes.append([int(line.split()[0]),2,int(line.split()[2]),int(line.split()[3])])
        elif line.split()[1] == "ctrl":
            notes.append([int(line.split()[0]),2,int(line.split()[2]),int(line.split()[3])])
        else:
            notes.append([int(line.split()[0]),int(line.split()[1]),int(line.split()[2]),int(line.split()[3])])
    dump.close
    return notes

def loadconffromfile(obj,filename):
    list_params = []
    emptyfile = True
    for line in open(filename,'r').readlines():
        try:
            if str(line.split('=')[1]).rstrip('\n').isdigit() :
#                print("digit!")
                setattr(obj,line.split('=')[0],int(line.split('=')[1].rstrip('\n')))  
            else:
                if line.split('=')[0] == "debug":
                    if line.split('=')[1].rstrip('\n') == "False":
                        setattr(obj,'debug',False)
                        print("debug mode off")
                    else :
                        setattr(obj,'debug',True)
                        print("debug mode on")
                else:
                    setattr(obj,line.split('=')[0],str(line.split('=')[1]).rstrip('\n'))
            list_params.append(line.split('=')[0])
            emptyfile = False
        except:
            pass
    if not emptyfile :
        obj.list_params = list_params
        d = dict()
        for param in list_params:
            d[param] = str(getattr(obj,param))
        j = json.JSONEncoder().encode(d)
        f = open(filename+'.json','w+')
        f.write(j)
        f.close

    
                           
                           
def savenotestofile(notes,filename):

    dump = open(filename,'w+')
    for i in range(len(notes)):
        if notes[i][1] == 1:
            dump.write(str(notes[i][0])+ " " +"1"+ " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        elif notes[i][1] == 0:
            dump.write(str(notes[i][0]) + " " + "0" + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        elif notes[i][1] == 2:
            dump.write(str(notes[i][0]) + " " + "5" + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
        else :
            dump.write(str(notes[i][0]) + " " + str(notes[i][1]) + " " + str(notes[i][2]) + " " + str(notes[i][3]) + "\n")
    dump.close()
    
def saveConftofile(obj,filename):
    f = open(filename,'w+')
    for param in obj.list_params:
        f.write(str(param)+"="+str(getattr(obj,param))+"\n")
    f.close()
    
    
def loadPumpsfromfile(filename,debug):
    
    if debug:
        print filename
        
    filein = bsddb3.rnopen(filename)
    last, toto = filein.last()
    tabpumps = []
    up = 0
    down = 0
    for key in range(last):
        cle,donnee = filein.set_location(key+1)
        tabpumps.append(donnee.split('%',7))
        if donnee[0] == 'DOWN':
            down = cle
            if debug:
                print "down = "+str(cle)
        elif donnee[0] == 'UP':
            up = cle
            if debug:
                print "up = "+str(cle)
        if debug:
            print donnee.split('%',7)
    filein.close()
#    print(tabpumps)
    return tabpumps,down,up

def loadPumpsfromdb(db,debug):
    
    pumps = db.cursor(MySQLdb.cursors.DictCursor)
    down = False
    up = False
    pumps.execute("""SELECT name, deg, pump, time FROM ing
          WHERE pump > 0 ORDER by pump""")
    tabpumps = pumps.fetchall()
    if debug:
        print("mysql fetchpump result: "+str(tabpumps)+"\n")
    for row in tabpumps:
        if row['name'] == 'UP':
            up = row['pump']
            if debug:
                print("UP = "+str(up)+"\n")
            if down :
                break
        elif row['name'] == 'DOWN':
            down = row['pump']
            if debug:
                print("DOWN = "+str(down)+"\n")
            if up :
                break
    return tabpumps,down,up


def savePumpstofile(tabpumps,filename):
        
    fileout = bsddb3.rnopen(filename,'n')
    for key in range(len(tabpumps)):
        data = ''
        for i in range(len(tabpumps[key])):
            if i == 0:
                data = str(tabpumps[key][i])
            else:
                data = data + '%' + str(tabpumps[key][i])
        fileout[key+1] = data
    fileout.close()
    
    
def loadCooksfromfile(filename):
        
    filein = bsddb3.rnopen(filename)
    last,toto = filein.last()
    tabcooks = []
    global data
    data = ''
    for key in range(last):
        cle,donnee = filein.set_location(key+1)
        data = donnee.split('%',14)
        tabcooks.append([data[0],[data[1],data[2]],[data[3],data[4]],[data[5],data[6]],[data[7],data[8]],[data[9],data[10]],[data[11],data[12]],[data[13],data[14]]])
    filein.close()
    return tabcooks

def loadRecipesfromdb(db,debug):
    recipes = db.cursor(MySQLdb.cursors.DictCursor)
    recipes.execute("""CALL getCocktails;""")
    tabrecipes = recipes.fetchall()
    if debug:
        print("mysql fetchrecipes result: "+str(tabrecipes)+"\n")
    return tabrecipes
            
        
def saveCookstofile(tabcooks,filename):
        
    fileout = bsddb3.rnopen(filename,'n')
    for cle in range(len(tabcooks)):
        data = ''
        for element in range(len(tabcooks[cle])):
            if element == 0:
                data = str(tabcooks[cle][element])
            else:
                for i in range(len(tabcooks[cle][element])):
                    data = data + '%' + str(tabcooks[cle][element][i])
            fileout[cle+1] = data
        fileout.close()
        


    
    



