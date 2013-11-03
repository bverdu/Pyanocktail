# -*- coding: utf-8 -*-
'''
Created on 27 oct. 2013

@author: babe
'''
import math

tonalite_tab = ['Do Majeur', 'Do# Majeur', 'Ré Majeur', 'Ré# Majeur', 'Mi Majeur', 'Fa Majeur', 'Fa# Majeur', 'Sol Majeur', 'Sol# Majeur', 'La Majeur', 'La# Majeur', 'Si Majeur', 'Do Mineur', 'Do# Mineur', 'Ré Mineur', 'Re# Mineur', 'Mi Mineur', 'Fa Mineur', 'Fa# Mineur', 'Sol Mineur', 'Sol# Mineur', 'La Mineur', 'La# Mineur', 'Si Mineur']

def filter_process_result(output, cocktails, compind=1, tristind=1, nervind=1, debug=True):
    result = {}
    res = []
    cocktail = ''
    c = [0, 999.99]
#     print("*****"+output)
    for line in output.split("\n"):
        if debug:
            print("****"+line)
        if line.startswith(' Duree'):
            duree = line.split()[0].split('=')[1]
            tristesse = line.split()[1].split('=')[1]
            enervement = line.split()[2].split('=')[1]
            res.append(u"Durée du morceau = " + duree + " secondes")
            res.append('tristesse = '+tristesse)
            res.append('enervement = '+enervement)
            if debug:
                print(u"Durée du morceau = " + duree)
            if debug:
                print("tristesse returned = "+tristesse)
        elif line.startswith(' Complexite'):
            complexite = line.split()[0].split('=')[1]
            metrique = line.split()[1].split('=')[1]
            tonalite = line.split()[2].split('=')[1]
            res.append('complexite = '+complexite)
            if int(metrique.strip('.')) == 2:
                res.append(u"Métrique = Binaire")
                if debug:
                    print(u"Metrique = Binaire")
            elif int(metrique.strip('.')) == 3:
                res.append(u"Metrique = Ternaire")
                if debug:
                    print(u"Metrique = Ternaire")
            else:
                res.append(u"Metrique incoherente....")
                if debug:
                    print(u"Metrique incoherente....")
            res.append(u"Tonalité = "+tonalite_tab[int(tonalite.strip('.'))-1])
            if debug:
                print(u"Tonalite = " +tonalite_tab[int(tonalite[0].strip('.')) - 1])
        elif line.startswith(' Tempo'):
            tempo = line.split()[0].split('=')[1]
            cock = line.split()[1].split('=')[1:]
            res.append("Tempo = "+ tempo +" bpm")
            if debug:
                print("Tempo = " + tempo + " bpm")
    
    for recipe in cocktails:
        if recipe['available'] != 'OK':
            continue
        score = math.fabs(float(complexite)*compind - float(recipe['score1']))\
         + math.fabs(float(tristesse)*tristind - float(recipe['score2']))\
         + math.fabs(float(enervement)*nervind - float(recipe['score3']))
        if debug:
            print(recipe['name']+" score = "+str(score))
        if score < c[1]:
            print("rr")
            c[0] = int(recipe['id'])
            print("rrr")
            c[1] = score
            cocktail = recipe['name']
    res.append(u"Cocktail choisi : "+cocktail)
    if debug:
        print("cocktail found = "+cocktail+" score = "+str(c[1]))
        
    result['cocktail'] = c[0]
    result['result'] = res
    
    return result