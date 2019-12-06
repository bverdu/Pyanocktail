# -*- coding: utf-8 -*-
'''
Created on 27 oct. 2013

@author: babe
'''
import math

tonalite_tab = ['Do Majeur', 'Do# Majeur', 'Re Majeur', 'Re# Majeur', 'Mi Majeur', 'Fa Majeur', 'Fa# Majeur', 'Sol Majeur', 'Sol# Majeur', 'La Majeur', 'La# Majeur',
                'Si Majeur', 'Do Mineur', 'Do# Mineur', 'Re Mineur', 'Re# Mineur', 'Mi Mineur', 'Fa Mineur', 'Fa# Mineur', 'Sol Mineur', 'Sol# Mineur', 'La Mineur', 'La# Mineur', 'Si Mineur']


def format_output(output):
    return ''' Duree=%s tristesse=%s enervement=%s\n Complexite=%s metrique=%s tonalite=%s\n Tempo=%s Cocktail=%s''' % output


def filter_process_result(output, cocktails, compind=1, tristind=1, nervind=1, debug=True):
    result = {}
    res = []
    cocktail = ''
    c = []
#     print("*****"+output)
    for line in output.split("\n"):
        if debug:
            print("****" + line)
        if line.startswith(' Duree'):
            duree = line.split()[0].split('=')[1]
            tristesse = line.split()[1].split('=')[1]
            enervement = line.split()[2].split('=')[1]
            res.append(("Durée du morceau = " + duree +
                        " secondes"))
            res.append(('Tristesse = ' + tristesse))
            res.append(('Énervement = ' + enervement))
            if debug:
                print(u"Durée du morceau = " + duree)
            if debug:
                print("tristesse returned = " + tristesse)
        elif line.startswith(' Complexite'):
            complexite = line.split()[0].split('=')[1]
            metrique = line.split()[1].split('=')[1]
            tonalite = line.split()[2].split('=')[1]
            res.append(('Complexité = ' + complexite))
            if int(metrique.strip('.')) == 2:
                res.append(("Métrique = Binaire"))
                if debug:
                    print(u"Métrique = Binaire")
            elif int(metrique.strip('.')) == 3:
                res.append(("Métrique = Ternaire"))
                if debug:
                    print(u"Métrique = Ternaire")
            else:
                res.append(("Métrique incoherente...."))
                if debug:
                    print(u"Métrique incoherente....")
            res.append(
                ("Tonalité = " + tonalite_tab[int(tonalite.strip('.')) - 1]))
            if debug:
                print(
                    (u"Tonalité = " + tonalite_tab[int(tonalite[0].strip('.')) - 1]))
        elif line.startswith(' Tempo'):
            tempo = line.split()[0].split('=')[1]
#             cock = line.split()[1].split('=')[1:]
            res.append("Tempo = " + tempo + " bpm")
            if debug:
                print(u"Tempo = " + tempo + " bpm")

    pass1 = []
    size = int(len(cocktail) / 4)
    if size == 0:
        size = 1
    for recipe in cocktails:
        if recipe['available'] != 'OK':
            continue
        score = math.fabs(float(tristesse) * tristind -
                          float(recipe['score2']))
        if len(pass1) < 5:
            pass1.append([recipe, score])
        else:
            for recip in pass1:
                if score < recip[1]:
                    recip[0] = recipe
                    recip[1] = score
    pass2 = []
    for r in pass1:
        pass2.append(r[0])
    for recipe in pass2:
        if recipe['available'] != 'OK':
            continue
        score = math.fabs(float(complexite) * compind - float(recipe['score1']))\
            + math.fabs(float(enervement) * nervind - float(recipe['score3']))
        if debug:
            print((recipe['name'] + " score = " + str(score)).encode('utf-8'))
        if len(c):
            if score < c[1]:
                c[0] = int(recipe['id'])
                c[1] = score
                cocktail = recipe['name']
        else:
            c = [int(recipe['id']), score]
            cocktail = recipe['name']

#     for recipe in cocktails:
#         if recipe['available'] != 'OK':
#             continue
#         score = math.fabs(float(complexite)*compind - float(recipe['score1']))\
#          + math.fabs(float(tristesse)*tristind - float(recipe['score2']))\
#          + math.fabs(float(enervement)*nervind - float(recipe['score3']))
#         if debug:
#             print((recipe['name']+" score = "+str(score)).encode('utf-8'))
#         if len(c):
#             if score < c[1]:
#                 c[0] = int(recipe['id'])
#                 c[1] = score
#                 cocktail = recipe['name']
#         else:
#             c = [int(recipe['id']),score]
#             cocktail = recipe['name']
    if len(c) > 0:
        res.append(("Cocktail choisi : " + cocktail))
        if debug:
            print(("cocktail found = " + cocktail +
                   " score = " + str(c[1])))
        result['cocktail'] = c[0]
    else:
        res.append((u"Aucun cocktail trouvé"))
        if debug:
            print(("cocktail found = None"))
        result['cocktail'] = 0
#     try:
#
#     except IndexError:
#         result['cocktail'] = 0
#
    result['result'] = res

    return result
