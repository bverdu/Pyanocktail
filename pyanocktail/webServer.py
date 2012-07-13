# -*- coding: utf-8 -*-
'''
Created on 30 mai 2012

@author: babe
'''
import os, json
from pyanocktail.midi import listInports, listOutports
from twisted.web.resource import Resource
from twisted.web import server, static
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
Com['pump']=10

class Dispatcher(Resource):
    isLeaf = False
    def __init__(self,debug,installdir,task_queue,status_queue,conf):
        Resource.__init__(self)
#        self.seq = seq
        self.conf = conf
        self.task = task_queue
        self.status_queue= status_queue
        self.debug = debug
        self.installdir = installdir
        self.putChild("pictures",static.File(os.path.join(self.installdir,'html','pictures')))
        self.putChild("favicon.png", static.File(os.path.join(self.installdir,'html','favicon.png')))
        self.putChild("style.css", static.File(os.path.join(self.installdir,'html','style.css')))
        self.putChild("fonts", static.File(os.path.join(self.installdir,'html','fonts')))
        self.putChild("scripts", static.File(os.path.join(self.installdir,'html','scripts')))
        self.putChild("notes.pckt", static.File(os.path.join(os.path.expanduser("~/.pianocktail"),'scripts','current.pckt'),defaultType='application/octet-stream'))
    def getChild(self, name, request):
        if self.debug:
            log.msg("page demandée: "+str(name))
        return MainPage(name,self.debug,self.installdir,self.task,self.status_queue,self.conf)
        
class MainPage(Resource):
    def __init__(self,page,debug,installdir,task_queue,status_queue,conf):
        self.page = page
        self.conf = conf
#        self.seq = seq
        self.task = task_queue
        self.status_queue = status_queue
        self.debug = debug
        self.installdir = installdir
    isLeaf = True
    def render_GET(self, request):
        if self.debug:
            log.msg("GET received" + " from page " + str(self.page) +" : "+ str(request.args))
        request.write(self.serve())
        request.finish()
        return server.NOT_DONE_YET
    def render_POST(self, request):
        param = False
        if self.debug:
            log.msg("POST received Headers: " + str(request.getAllHeaders())+"\n")
            log.msg("POST received Args: " + str(request.args)+"\n")
            log.msg("POST received Content: " + str(request.content.getvalue())+"\n")
        try :
            try:
                client = request.args['client'][0]
                action = request.args['action'][0]
                try :
                    command = request.args['command'][0]
                except : pass
                if self.debug:
                    log.msg("client: "+str(client))
                    log.msg("action: "+str(action))
            except:
                try:
                    dictreq = json.load(request.content)
                    log.msg(dictreq)
                    client = dictreq['client']
                    action = dictreq['action']
                    command = dictreq['command']
                    param = dictreq['params']
                except Exception,err:
                    log.msg(err.message)
            if client == 'cli':
                if action in ('status','close','play','record','reload','cocktail','stop'):
                    try:
                        self.task.put(Com[action])
                        status = self.status_queue.get()
                        request.write(status)
                        self.status_queue.put_nowait(status)
                    except Exception,err:
                        request.write(err.message)
                else:
                    request.write("bad command")
            elif client == 'web':
                if action in ('status','close','play','record','reload','cocktail','stop','config','pump'):
                    self.task.put(Com[action])
                    if action == 'record':
                        request.write(self.serve(1))
                    elif action == 'play':
                        request.write(self.serve(2))
                    elif action == 'cocktail':
                        request.write(self.serve(3))
                    elif action == 'config':
                        if param :
                            request.write(self.jsonconf(command,param))
                            if self.debug:
                                log.msg("request processed")
                        else:
                            request.write(self.jsonconf(command))
                            if self.debug:
                                log.msg("request processed")
                    elif action == 'pump':
                        log.msg("coucou")
                        if command :
                            if self.debug:
                                log.msg("pump command"+command)
                            try:
                                self.task.put(command)
                                request.write('0')
                            except:
                                log.msg("task error")
                                request.write('1')
                    else :
                        request.write(self.serve())
                else :
                    request.write("bad command")
        except Exception, err:
            if self.debug:
                log.msg("Error: " + err.message)
            request.write("network error")
        request.finish()
        return server.NOT_DONE_YET
    def serve(self,direct=0):
        if direct == 0:
            if self.page == '':
                stat = 'tata'
                if stat in ['Recording']:
                    htmlfile = (open(os.path.join(self.installdir,"html/recording.html"),'r')).readlines()
                elif stat in ['Analysing','Analyse et service en cours','Service en cours']:
                    htmlfile = (open(os.path.join(self.installdir,"html/cocktailing.html"),'r')).readlines()
                elif stat in ['Playing']:
                    htmlfile = (open(os.path.join(self.installdir,"html/playing.html"),'r')).readlines()
                else :
                    htmlfile = (open(os.path.join(self.installdir,"html/Pianocktail.html"),'r')).readlines()     
                htmlstream = ''
                for line in htmlfile:
                    htmlstream = htmlstream + line.strip('/t').strip('/n')
                return(htmlstream)
            else :
                try :
                    htmlfile = (open(os.path.join(self.installdir,"html/"+self.page+".html"),'r')).readlines()     
                    htmlstream = ''
                    for line in htmlfile:
                        htmlstream = htmlstream + line.strip('/t').strip('/n')
                    return(htmlstream)
                except:
                    return "pigeot 404"
        elif direct == 1:
            if self.page == '':
                htmlfile = (open(os.path.join(self.installdir,"html/recording.html"),'r')).readlines()
                htmlstream = ''
                for line in htmlfile:
                    htmlstream = htmlstream + line.strip('/t').strip('/n')
                return(htmlstream)
        elif direct == 2:
            if self.page == '':
                htmlfile = (open(os.path.join(self.installdir,"html/playing.html"),'r')).readlines()
                htmlstream = ''
                for line in htmlfile:
                    htmlstream = htmlstream + line.strip('/t').strip('/n')
                return(htmlstream)
        elif direct == 3:
            if self.page == '':
                htmlfile = (open(os.path.join(self.installdir,"html/cocktailing.html"),'r')).readlines()
                htmlstream = ''
                for line in htmlfile:
                    htmlstream = htmlstream + line.strip('/t').strip('/n')
                return(htmlstream)
    def jsonconf(self,command,params=[]):
        d = dict()
        if command == 'getconf':
            for param in self.conf.list_params :
                d[param] = getattr(self.conf,param)
                d['inports'] = listInports()
                d['outports'] = listOutports()
                d['connectedin'] = self.conf.sysports[0]
                d['connectedout'] = self.conf.sysports[1]
        elif command == 'setconf':
            for param in params :
                log.msg("update = "+str(param)+" value = "+str(params[param]))
                if str(param) == 'debug':
                    if params[param] == 0:
                        setattr(self.conf,param,False)
                    else:
                        setattr(self.conf,param,True)
                else:
                    setattr(self.conf,param,params[param])
                d['updated'] = "1"
                self.conf.save(self.conf.configdir)
                self.task.put(Com['reload'])
            log.msg("setconf params: "+str(params))
                    
        elif command == 'getpumps':
            d['pumps'] = self.conf.pumpsdb
        elif command == 'getrecipes':
            d['recipes'] = self.conf.recipesdb
        elif command == 'setpumps':
            if self.conf.writePumpdb(params):
                d['updated'] = "1"
                if self.debug:
                    log.msg("update OK")
            else:
                d['updated'] = "0"
                if self.debug:
                    log.msg("update KO")
            log.msg("setpumps params: "+str(params))
        elif command == 'setrecipes':
            if self.conf.writeRecipesdb(params):
                d['updated'] = "1"
                if self.debug:
                    log.msg("update OK")
            else:
                d['updated'] = "0"
                if self.debug:
                    log.msg("update KO")
            log.msg("setrecipes params: "+str(params))
        elif command == 'delrecipes':
            if self.conf.delRecipesdb(params):
                d['updated'] = "1"
                if self.debug:
                    log.msg("update OK")
            else:
                d['updated'] = "0"
                if self.debug:
                    log.msg("update KO")
            log.msg("setrecipes params: "+str(params))
        return json.JSONEncoder().encode(d)
        