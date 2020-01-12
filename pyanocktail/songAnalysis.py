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
    trist_min = 1000
#     print("*****"+output)
    for line in output.split("\n"):
        #         if debug:
        #             print("****" + line)
        if line.startswith(' Duree'):
            duree = float(line.split()[0].split('=')[1])
            tristesse = float(line.split()[1].split('=')[1])
            enervement = float(line.split()[2].split('=')[1])
            res.append(("Durée du morceau: %d secondes" % duree))
            res.append(('Mélancolie: %d' % tristesse))
            res.append(('Passion: %d' % enervement))
            if debug:
                print("Durée du morceau: %.2f" % duree)
            if debug:
                print("Tristesse: %.3f" % tristesse)
                print("Énervement: %.3f" % enervement)
        elif line.startswith(' Complexite'):
            complexite = float(line.split()[0].split('=')[1])
            metrique = line.split()[1].split('=')[1]
            tonalite = line.split()[2].split('=')[1]
            res.append(('Virtuosisticité: %d' % complexite))
            if debug:
                print("Complexité: %.3f " % complexite)
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
                    print("Métrique incoherente....")
            res.append(
                ("Tonalité: %s" % tonalite_tab[int(tonalite.strip('.')) - 1]))
            if debug:
                print(
                    ("Tonalité: %s" %
                     tonalite_tab[int(tonalite[0].strip('.')) - 1]))
        elif line.startswith(' Tempo'):
            tempo = float(line.split()[0].split('=')[1])
#             cock = line.split()[1].split('=')[1:]
            res.append("Tempo: %d bpm" % tempo)
            if debug:
                print("Tempo: %d" % tempo)

    pass1 = []
    size = int(len(cocktail) / 4)
    if size == 0:
        size = 1
    print("************ Pass 1 **************")
    for recipe in cocktails:
        if recipe['available'] != 'OK':
            continue
        score = math.fabs(tristesse * tristind -
                          float(recipe['score2']))
#         if debug:
#             print("%s pass1 score: %.3f" % (recipe['name'], score))
        score_tonio = math.fabs((
            (tristesse * tristind +
             complexite * compind +
             enervement * nervind) / 3.0) - (
            (float(recipe['score1']) +
             float(recipe['score2']) +
             float(recipe['score3'])) / 3.0)
        )
#         print("%s pass1 score par moy: %.3f" % (recipe['name'], score_tonio))
        if len(pass1) == 0:
            pass1 = [[recipe, score]]
            print("%s added to pass2 list in position %d" % (
                recipe['name'], len(pass1)))
        else:
            if len(pass1) < 4:
                if score > pass1[-1][1]:
                    pass1.append([recipe, score])
                    print("%s added to pass2 list in position %d" % (
                        recipe['name'], len(pass1)))
                else:
                    ins = 0
                    for i, r in enumerate(pass1):
                        if score < r[1]:
                            ins = i
                            break
                    if debug:
                        print("%s inserted to pass2 list in position %d" % (
                            recipe['name'], ins + 1))
                        print("score: %.2f, score by mean: %.2f" %
                              (score, score_tonio))
                    pass1.insert(ins, [recipe, score])
            else:
                if score < pass1[3][1]:
                    ins = 3
                    for i, r in enumerate(pass1):
                        if score < r[1]:
                            ins = i
                            break
                    if debug:
                        print("%s inserted to pass2 list in position %d" % (
                            recipe['name'], ins + 1))
                        print("score: %.2f, score by mean: %.2f" %
                              (score, score_tonio))
                    pass1.insert(ins, [recipe, score])
#             for recip in pass1:
#                 if recip[1] < trist_min:
#                     trist_min = recipe[1]
#                 if score < recip[1]:
#                     recip[0] = recipe
#                     recip[1] = score.
    pass1 = pass1[:4]
    pass2 = []
    pass3 = []
    if debug:
        print("************ Pass 2 **************")
    for r in pass1:
        pass2.append(r[0])
    for recipe in pass2:
        score = math.fabs(enervement * nervind - float(recipe['score3']))
#         score = math.fabs(float(complexite) * compind - float(recipe['score1']))\
#             + math.fabs(float(enervement) * nervind - float(recipe['score3']))
#         if debug:
#             print("%s pass2 score: %.3f" % (recipe["name"], score))
#             print((recipe['name'] + " score = " + str(score)).encode('utf-8'))
        if len(pass3) > 1:
            if score < pass3[-1][1]:
                ins = 1
                for i, s in enumerate(pass3):
                    if score < s[1]:
                        if debug:
                            print("%s inserted to pass3 list in position %d" %
                                  (recipe['name'], i))
                            print("score: %d" % score)
                        ins = i
                        break
                pass3.insert(ins, [recipe, score])
        else:
            if len(pass3):
                if score < pass3[0][1]:
                    pass3.insert(0, [recipe, score])
                    print("%s inserted to pass3 list in position 1" %
                          recipe['name'])
                    print("score: %d" % score)
                else:
                    pass3.append([recipe, score])
                    print("%s added to pass3 list in position 2" %
                          recipe['name'])
                    print("score: %d" % score)
            else:
                pass3.append([recipe, score])
                print("%s added to pass3 list in position 1" %
                      recipe['name'])
                print("score: %d" % score)
    pass3 = pass3[:2]
    print("************ Pass 3 **************")
    for r in pass3:
        score = math.fabs(complexite * compind - float(r[0]['score1']))
        if debug:
            print("%s Final score: %.3f" % (r[0]["name"], score))
        if len(c):
            if score < c[1]:
                c[0] = int(r[0]['id'])
                c[1] = score
                cocktail = r[0]['name']
        else:
            c = [int(r[0]['id']), score]
            cocktail = r[0]['name']

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
            print("Cocktail: %s, score = %.3f" % (cocktail, c[1]))
        result['cocktail'] = c[0]
    else:
        res.append((u"Aucun cocktail trouvé"))
        if debug:
            print(("No Cocktail found"))
        result['cocktail'] = 0
#     try:
#
#     except IndexError:
#         result['cocktail'] = 0
#
    result['result'] = res

    return result
