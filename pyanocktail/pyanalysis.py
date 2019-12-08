# -*- coding: utf-8 -*-

# This software is free software; you can redistribute it and/or modify it under
# the terms of version 2 of GNU General Public License as published by the
# Free Software Foundation (see License.txt).

from __future__ import division

import numpy as np

# Note FJ :
# format des fichiers pckt :
# je crois qu'on a
# colonne 0 : temps de l'évènement (en ms)
# colonne 1 : type dévènement (0 note off, 1 note on, 5 sustain on ou off)
# colonne 2 : hauteur de la note
# colonne 3 : intensité de la note


def arggsort(data):
    # Il n'y a pas d'équivalent direct à la fonction gsort de scilab dans numpy
    # gsort ordonne les résultats du plus grand au plus petit, en imposant en plus
    # de conserver l'ordre des indices pour les valeurs identiques

    # on recupère les valeurs ordonnées du plus grand au plus petit
    ordered_data = np.sort(data)[::-1]
    # on récupère les indices correspondants
    indexes = np.argsort(data)[::-1]

    # il est maintenant nécessaire de faire une boucle pour réordonner les indices
    # pour les valeurs identiques
    # début de la plage (inclus) pour laquel les valeurs ordonnées sont
    # identiques
    ind_start = 0
    # fin de la plage (exclus) pour laquel les valeurs ordonnées sont
    # identiques
    ind_stop = 1
    for ind in range(1, indexes.shape[0]):
        if ordered_data[ind] == ordered_data[ind - 1]:
            ind_stop += 1
        else:
            indexes[ind_start:ind_stop] = np.sort(indexes[ind_start:ind_stop])
            ind_start = ind_stop
            ind_stop += 1
    indexes[ind_start:ind_stop] = np.sort(indexes[ind_start:ind_stop])

    return indexes


def PIANOCKTAIL(notes):
    ######################################
    #  Ouverture des fichiers - Liste des ON / OFF / SUSTAIN
    ######################################

    #     piano = np.loadtxt(fname)
    if isinstance(notes, list):
        piano = np.array(notes)
    else:
        piano = np.loadtxt(notes)
    l = piano.shape[0]
    # Liste des ON / OFF / SUSTAIN
    M_On = piano[piano[:, 1] == 1, :]
    nbnotes_piece = M_On.shape[0]
    M_Off = piano[piano[:, 1] == 0, :]
    nbnoff_piece = M_Off.shape[0]
    M_Sust = piano[piano[:, 1] == 5, :]
    nbsust_piece = M_Sust.shape[0]

    # Conversion des instants millisecondes -> secondes
    M_On[:, 0] = M_On[:, 0] / 1000.
    M_Off[:, 0] = M_Off[:, 0] / 1000.
    M_Sust[:, 0] = M_Sust[:, 0] / 1000.

    ######################################
    #  Verif des sustains: si nombre impair, off a la fin du morceau
    ######################################

    # !!! FJ : attention, je n'ai aucun fichier de test avec des données de
    # sustain, tout ce qui concerne le sustain n'a donc pas été testé
    if nbsust_piece % 2 != 0:
        M_Sust = np.vstack([M_Sust, [np.max(M_Off[:, 0]), 5., 0., 0.]])
        nbsust_piece = M_Sust.shape[0]

    # Separation des sustains On / Off
    Sust_On = M_Sust[0::2, :]
    Sust_Off = M_Sust[1::2, :]

    ######################################
    #  Determination de la fin des notes
    ######################################

    for i in np.arange(nbnotes_piece):
        j = 0
        while ((M_Off[j, 2] != M_On[i, 2]) or (M_Off[j, 0] < M_On[i, 0])) \
                and (j < nbnoff_piece - 1):
            j += 1
        M_On[i, 1] = M_Off[j, 0]
        M_Off[j, 2] = 0.

    del M_Off
    del piano

    note_piece = np.zeros([nbnotes_piece, 7])
    note_piece[:, 3] = M_On[:, 2]
    note_piece[:, 4] = M_On[:, 3]
    note_piece[:, 5] = M_On[:, 0]
    note_piece[:, 6] = M_On[:, 1] - M_On[:, 0]

    del M_On

    size_piece = note_piece.shape
    nbnotes_piece = size_piece[0]

    # Duration of the piece in seconds:
    t_piece = np.max(note_piece[:, 5])
    duree = t_piece

    # Density of notes (notes/seconds):
    densite = nbnotes_piece / t_piece

    # Attaques:
    # !!! FJ : Il manque pas un indice à note_piece dans np.mean(note_piece))^(1/3) ?
    # OUI : ajouter [:,4]

    # !!! FJ : scilab renvoie 0 pour stdev lorsqu'on lui passe une seule valeur
    # (ie il y a une seule note dans le morceau), numpy renvoie nan
    # -> j'ajoute un test
    if note_piece.shape[0] == 1:
        Enervement = np.mean(note_piece[:, 4]) * 0.1**(1. / 3.) * 1.1
    else:
        Enervement = np.mean(note_piece[:, 4]) * \
            (0.1 + 1.0 * (np.std(note_piece[:, 4], ddof=1)) / np.mean(note_piece[:, 4]))**(1. / 3.) \
            * 1.1

    metrique = METRIQUE(note_piece)
    tonalite = TONALITE(note_piece)
    tempo = TEMPO(note_piece)

    # Complexite:
    # !!! FJ : C'est normal le commentaire à la fin ?
    # OUI c'est normal
    Complexite = (densite * 60 / tempo)**1.2  # *densite**0.3

    # Tristesse du morceau
    # 45 points pour le tempo et bonus de 40 si tonalite mineure, bonus de 15 si binaire
    # !!! FJ : pourquoi il y a un max là ?
    # OUI c'est normal !!!
    tristesse = max(45 * (1 - tempo / 150) + 40 *
                    np.floor(tonalite / 13.), 0) + 15 * (1 - np.floor(metrique / 3.))

    cocktail = RECETTE(duree, Complexite, tonalite, tempo)

    return (duree, tristesse, Enervement, Complexite, metrique, tonalite, tempo, cocktail)


def RECETTE(duree, complexite, tonalite, tempo):
    # Ici on détermine quoi mettre dans le verre !

    crit_duree = [0., 10., 30., 90., 180.]
    crit_tempo = [50, 80, 120]

    alcfort = ['alc01 ', 'alc02 ', 'alc03 ', 'alc04 ', 'alc05 ', 'alc06 ',
               'alc07 ',  'alc08 ', 'alc09 ', 'alc10 ', 'alc11 ', 'alc12 ']

    sodamaj = ['sj1 ', 'sj2 ', 'sj3 ', 'sj4 ']
    sodamin = ['sn1 ', 'sn2 ', 'sn3 ', 'sn4 ']

    complicado = ['tralala ']

    recette = []

    # CHOIX DE L'ALCOOL FORT (Tonalite)
    recette.append(alcfort[(tonalite - 1) % 12])

    # DOSAGE DE L'ALCOOL FORT (Duree du morceau)
    # !!! FJ : il faudrait récrire ces boucles de manière plus générique
    # avec des opérations sur les tableaux directement
    if ((crit_duree[0] < duree) and (duree <= crit_duree[1])):
        recette.append('0 ')
    elif ((crit_duree[1] < duree) and (duree <= crit_duree[2])):
        recette.append('1 ')
    elif ((crit_duree[2] < duree) and (duree <= crit_duree[3])):
        recette.append('2 ')
    elif ((crit_duree[3] < duree) and (duree <= crit_duree[4])):
        recette.append('3 ')
    elif (duree > crit_duree[4]):
        recette.append('4 ')

    # DETERMINATION DU SODA
    # Pre-decoupage de la liste de sodas: majeur - mineur
    # !!! FJ il faudrait vérifier comment est codée la tonalité, mais si les
    # valeurs 1 à 12 sont en majeur, là il y a une erreur car 12 est reconnu
    # comme mineur, et est-ce que le else est censé arriver ?
    # OUI, c'est à corriger -> J'ai remplacé tonalite par tonalite-1
    # bug_6.pckt permet de tomber sur un cas où la tonalité vaut 24, ce qui
    # provoquait un problème avec le code non corrigé
    if np.floor((tonalite - 1) / 12.) == 0.:
        soda = sodamaj
    elif np.floor((tonalite - 1) / 12.) == 1.:
        soda = sodamin
    else:
        soda = []

    # DETERMINATION DU SODA
    # Choix du soda proprement dit
    if (tempo < crit_tempo[0]):
        recette.append(soda[0])
        recette.append('3 ')
    elif ((crit_tempo[0] < tempo) and (tempo <= crit_tempo[1])):
        recette.append(soda[1])
        recette.append('3 ')
    elif ((crit_tempo[1] < tempo) and (tempo <= crit_tempo[2])):
        recette.append(soda[2])
        recette.append('3 ')
    elif ((crit_tempo[2] < tempo)):
        recette.append(soda[3])
        recette.append('3 ')

    # LA PETITE TOUCHE DE VIRTUOSITE - C'EST PEUT-ETRE BON
    if complexite > 0.7:
        recette.append(complicado[0])
        recette.append('1 ')

    recette1 = ''.join(recette)

    return recette1


def TONALITE(note_piece):
    size_piece = note_piece.shape
    nbnotes_piece = size_piece[0]

    ####################################################
    # ESTIMATION DE LA TONALITE
    ####################################################
    #
    # Tonalité:
    # key_piece = kkkey(note_piece)
    # Key of NMAT according to the Krumhansl-Kessler algorithm
    # k = kkkey(nmat)
    # Returns the key of NMAT according to the Krumhansl-Kessler algorithm.
    #
    # Input argument:
    #   NOTE_PIECE = notematrix
    #
    # Output:
    #   K = estimated key of NMAT encoded as a number
    #   encoding: C major = 1, C# major = 2, ...
    #             c minor = 13, c# minor = 14, ...
    #
    # Remarks:
    #
    # See also KEYMODE, KKMAX, and KKCC.
    #
    # Example:
    #
    # Reference:
    #   Krumhansl, C. L. (1990). Cognitive Foundations of Musical Pitch.
    #   New York: Oxford University Press.
    #
    # Author           Date
    # P. Toiviainen    8.8.2002
    # © Part of the MIDI Toolbox, Copyright © 2004, University of Jyvaskyla, Finland
    # See License.txt

    # Correlations of pitch-class distribution with Krumhansl-Kessler tonal hierarchies
    # c = kkcc(nmat, <opt>)
    # Returns the correlations of the pitch class distribution PCDIST1
    # of NMAT with each of the 24 Krumhansl-Kessler profiles.
    #
    # Input arguments:
    #   NMAT = notematrix
    #   OPT = OPTIONS (optional), 'SALIENCE' return the correlations of the
    #       pitch-class distribution according to the Huron & Parncutt (1993)
    #       key-finding algorithm.
    #
    # Output:
    #   C = 24-component vector containing the correlation coeffients
    #       between the pitch-class distribution of NMAT and each
    #       of the 24 Krumhansl-Kessler profiles.
    #
    # Remarks: REFSTAT function is called to load the key profiles.
    #
    # Example: c = kkcc(nmat, 'salience')
    #
    # See also KEYMODE, KKMAX, and KKKEY in the MIDI Toolbox.
    #
    # References:
    #   Krumhansl, C. L. (1990). Cognitive Foundations of Musical Pitch.
    #   New York: Oxford University Press.
    #
    # Huron, D., & Parncutt, R. (1993). An improved model of tonality
    #     perception incorporating pitch salience and echoic memory.
    #     Psychomusicology, 12, 152-169.
    #

    pc = note_piece[:, 3] % 12

    tau = 0.5
    accent_index = 2
    dur = note_piece[:, 6]
    dur_acc = (1 - np.exp(-dur / tau))**accent_index

    # !!! FJ : il faudrait réécrire pour utiliser pcds sous la forme
    # np.zeros(12)
    pcds = np.zeros([1, 12])

    size_pc = pc.shape[0]
    for k in np.arange(size_pc):
        pcds[0, int(pc[k])] = pcds[0, int(pc[k])] + dur_acc[k]
    pcds = pcds / np.sum(pcds + 1e-12)

    kkprofs = np.array([
        [0.39, 0.14, 0.21, 0.14, 0.27, 0.25, 0.15, 0.32, 0.15, 0.22, 0.14, 0.18],
        [0.18, 0.39, 0.14, 0.21, 0.14, 0.27, 0.25, 0.15, 0.32, 0.15, 0.22, 0.14],
        [0.14, 0.18, 0.39, 0.14, 0.21, 0.14, 0.27, 0.25, 0.15, 0.32, 0.15, 0.22],
        [0.22, 0.14, 0.18, 0.39, 0.14, 0.21, 0.14, 0.27, 0.25, 0.15, 0.32, 0.15],
        [0.15, 0.22, 0.14, 0.18, 0.39, 0.14, 0.21, 0.14, 0.27, 0.25, 0.15, 0.32],
        [0.32, 0.15, 0.22, 0.14, 0.18, 0.39, 0.14, 0.21, 0.14, 0.27, 0.25, 0.15],
        [0.15, 0.32, 0.15, 0.22, 0.14, 0.18, 0.39, 0.14, 0.21, 0.14, 0.27, 0.25],
        [0.25, 0.15, 0.32, 0.15, 0.22, 0.14, 0.18, 0.39, 0.14, 0.21, 0.14, 0.27],
        [0.27, 0.25, 0.15, 0.32, 0.15, 0.22, 0.14, 0.18, 0.39, 0.14, 0.21, 0.14],
        [0.14, 0.27, 0.25, 0.15, 0.32, 0.15, 0.22, 0.14, 0.18, 0.39, 0.14, 0.21],
        [0.21, 0.14, 0.27, 0.25, 0.15, 0.32, 0.15, 0.22, 0.14, 0.18, 0.39, 0.14],
        [0.14, 0.21, 0.14, 0.27, 0.25, 0.15, 0.32, 0.15, 0.22, 0.14, 0.18, 0.39],
        [0.38, 0.16, 0.21, 0.32, 0.15, 0.21, 0.15, 0.28, 0.24, 0.16, 0.20, 0.19],
        [0.19, 0.38, 0.16, 0.21, 0.32, 0.15, 0.21, 0.15, 0.28, 0.24, 0.16, 0.20],
        [0.20, 0.19, 0.38, 0.16, 0.21, 0.32, 0.15, 0.21, 0.15, 0.28, 0.24, 0.16],
        [0.16, 0.20, 0.19, 0.38, 0.16, 0.21, 0.32, 0.15, 0.21, 0.15, 0.28, 0.24],
        [0.24, 0.16, 0.20, 0.19, 0.38, 0.16, 0.21, 0.32, 0.15, 0.21, 0.15, 0.28],
        [0.28, 0.24, 0.16, 0.20, 0.19, 0.38, 0.16, 0.21, 0.32, 0.15, 0.21, 0.15],
        [0.15, 0.28, 0.24, 0.16, 0.20, 0.19, 0.38, 0.16, 0.21, 0.32, 0.15, 0.21],
        [0.21, 0.15, 0.28, 0.24, 0.16, 0.20, 0.19, 0.38, 0.16, 0.21, 0.32, 0.15],
        [0.15, 0.21, 0.15, 0.28, 0.24, 0.16, 0.20, 0.19, 0.38, 0.16, 0.21, 0.32],
        [0.32, 0.15, 0.21, 0.15, 0.28, 0.24, 0.16, 0.20, 0.19, 0.38, 0.16, 0.21],
        [0.21, 0.32, 0.15, 0.21, 0.15, 0.28, 0.24, 0.16, 0.20, 0.19, 0.38, 0.16],
        [0.16, 0.21, 0.32, 0.15, 0.21, 0.15, 0.28, 0.24, 0.16, 0.20, 0.19, 0.38]])

    tmp_mat = np.vstack([pcds, kkprofs]).transpose()
    [n, p] = tmp_mat.shape
    covpcds = tmp_mat - np.dot(np.ones([n, p]), np.mean(tmp_mat))
    covpcds = np.dot(covpcds.transpose(), covpcds) / (n - 1)

    # !!! FJ : c'est normal que ce soit commenté ça ?
    # OUI, a priori l'équivalent est codé directement juste au dessus
    # covpcds = cov([pcds; kkprofs]');       # SCILAB: corr

    c2 = np.zeros(24)
    for k in np.arange(1, 25):
        c2[k - 1] = covpcds[0, k] / np.sqrt(covpcds[0, 0] * covpcds[k, k])
    tonalite = np.argmax(c2) + 1
    return tonalite


def TEMPO(note_piece):

    # !!! FJ il faudrait réécrire cette fonction en vectoriel (là c'est bouré de
    # boucles et bien difficile à lire...)

    size_piece = note_piece.shape
    nbnotes_piece = size_piece[0]

    # !!! FJ : Le cas où une seule est présente fait planter l'algo
    # -> il faudra décider comment on gère ce cas, pour l'instant je mets un
    # test et je renvoie une valeur arbitraire
    if nbnotes_piece == 1:
        tempo = 1.
        return tempo

    ####################################################
    # ESTIMATION DU TEMPO
    ####################################################

    # Calcul de la fin de chacune des notes (en seconde) et remplacement de la
    # colonne "durée en beats"

    note_piece[:, 1] = note_piece[:, 5] + note_piece[:, 6]

    # DECOMPTE DES EVENEMENTS DISTINCTS (i.e UN ACCORD = UN EVENEMENT)
    # Matrice Note_classees :
    #   Colonne 1: Instant de la frappe (en secondes)
    #   Colonne 2: Instant de fin de la note (en secondes)
    #   Colonne 3: Nombre de touches frappées à la fois

    Dur_min = np.min(note_piece[:, 6])
    tolerance = max(Dur_min / 3, 0.05)

    Nb_att = 1
    Note_classees = np.zeros([nbnotes_piece, 3])
    Note_classees[0, 0] = note_piece[0, 5]
    Note_classees[0, 1] = note_piece[0, 1]

    # !!! FJ : Il ne manque pas quelque chose pour gérer Note_classees[0, 2] ?
    # là ça vaut 0
    # OUI, il faut initialiser à 1 pour tenir compte de la note qu'on vient de
    # classer
    Note_classees[0, 2] = 1

    Last_time = note_piece[0, 5]

    dtim1 = 0.1

    for i in np.arange(1, nbnotes_piece):
        dti = note_piece[i, 5] - Last_time
        if dti >= tolerance:  # Non-simultanéité de 2 notes
            Nb_att += 1
            Note_classees[Nb_att - 1, 0] = note_piece[i, 5]
            Note_classees[Nb_att - 1, 1] = note_piece[i, 1]
            Note_classees[Nb_att - 1, 2] = 1
            Last_time = note_piece[i, 5]
        else:  # Simultanéité de 2 notes
            Note_classees[Nb_att - 1, 2] += 1

    # MARQUAGE / PONDERATION DES EVENEMENTS POUR EN DEDUIRE UN POIDS RYTHMIQUE

    Poids_tempo = np.zeros([Nb_att, 6])
    Poids_tempo[:, 0] = Note_classees[:Nb_att, 0]

    # Marquage Nr1: Valeurs successives d'inter-onsets proches/égales

    Poids_tempo[0, 1] = 1   # Initialisation

    for i in np.arange(2, Nb_att):
        dti = Note_classees[i, 0] - Note_classees[i - 1, 0]
        dtim1 = Note_classees[i - 1, 0] - Note_classees[i - 2, 0]
        if abs(dtim1 - dti) <= 0.2 * dtim1:
            Poids_tempo[i, 1] = 1

    # Marquage Nr2: intervalles entre attaques allongés

    Poids_tempo[0, 2] = 1   # Initialisation

    for i in np.arange(1, Nb_att - 1):
        dti = Note_classees[i, 0] - Note_classees[i - 1, 0]
        dtip1 = Note_classees[i + 1, 0] - Note_classees[i, 0]
        if dtip1 / dti <= 1.2:
            Poids_tempo[i, 2] = 1

    # Marquage Nr3: Nb de notes par accord

    Poids_tempo[:, 3] = Note_classees[:Nb_att, 2] - np.ones(Nb_att)

    # Marquage Nr4: Nb d'accords se terminant sur une attaque donnée
    dist_time = np.zeros(Nb_att)

    for i in np.arange(2, Nb_att):
        for j in np.arange(Nb_att):
            dist_time[j] = np.abs(Note_classees[j, 1] - Note_classees[i, 0])

        marq2 = np.nonzero(dist_time <= tolerance)[0]
        l = marq2.shape[0]
        if l > 0:
            Poids_tempo[i, 4] = l - 1

    # !!! FJ : Il vaudrait mieux écrire la ligne ci-dessous sous forme de produit matriciel
    Poids_tempo[:, 5] = 1 * Poids_tempo[:, 1] + 1 * Poids_tempo[:,
                                                                2] + 2 * Poids_tempo[:, 3] + 2 * Poids_tempo[:, 4]

    # GENERATION DE BATTUES POSSIBLES
    # Principe: on choisit un évènement
    #
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    #           TEMPO DE L'ENSEMBLE DU MORCEAU
    #
    # Initialisation: début de la propagation des battues à partir du 1/12 de
    # la durée du morceau

    # !!! FJ : je pense qu'il y a un gros bug là dans le code scilab, parce qu'il
    # manque un des indices, il utilise la matrice comme un vecteur et trouve des indices très grands
    # OK, ma modif est bonne
    indices = np.nonzero(Note_classees[:, 0] > (
        Note_classees[Nb_att - 1, 0] / 12))[0]

    i1 = max(indices[0], 1)

    # On vérifie que le point de départ est bien un maximum local de poids
    # tempo (borné à 1/6 de la longueur du morceau)

    while (i1 < (np.fix(Nb_att / 6.) - 1)) and \
          ((Poids_tempo[i1 - 1, 5] >= Poids_tempo[i1, 5]) or (Poids_tempo[i1 + 1, 5] >= Poids_tempo[i1, 5])):
        i1 += 1

    # Initialisation des battues: intervalles de temps entre la valeur de
    # départ et toutes les notes jouées jusque là

    # !!! FJ : Note_classees(1:(i1-1)) vaut implicitement Note_classees(1:(i1-1),1)), c'est bien ce qu'on veut ?
    # Pourquoi ne pas mettre explicitement le deuxième indice ?
    # OK, ma modif est bonne, comme ça marchait Tom n'a pas repéré ("wild
    # programming")
    battuesav = Note_classees[i1, 0] - Note_classees[:i1, 0]

    # !!! FJ : sur le fichier bug_4.pckt, ici battuesap vaut [] et je ne sais
    # pas si c'est correct
    battuesap = Note_classees[int((
        i1 + 1)):int((i1 + 2 + np.fix(Nb_att / 6))), 0] - Note_classees[i1, 0]
    #!!! FJ : Pourquoi indiquer les indices dans battues qui n'existe pas encore ?
    # OK, Tom savait pas que c'était pas nécessaire
    # battues[0:i1+np.fix(Nb_att/6)] = np.vstack([battuesav, battuesap])
    battues = np.hstack([battuesav, battuesap])

    # Elimination des battues de plus de 1.3 secondes

    # !!! FJ : il va falloir adapter des choses là -> notamment à passer en vectoriel

    # Modif FJ : dans certains cas, on a un plantage parce que battues ne contient aucune
    # battue inférieure à 1.3 -> pour éviter le plantage, on prend le minimum des battues
    # disponibles dans ce cas
    if battues.min() < 1.3:
        ind_battues = np.nonzero(battues < 1.3)[0]
    else:
        ind_battues = np.nonzero(battues == battues.min())[0]

    Nb_battues = ind_battues.shape[0]

    liste_battues = np.zeros([Nb_battues, 3])

    for i in np.arange(Nb_battues):
        k = ind_battues[i]
        liste_battues[i, 0] = battues[k]

    # !!! FJ : scilab fait le tri à l'envers (du plus grand au plus petit,
    # je dois ajouter [::-1] pour inverser l'ordre des résultats
    liste_battues[:, 0] = np.sort(liste_battues[:, 0])[::-1]

    for i in np.arange(Nb_battues):
        i2 = i1
        # Critere pour la propagation d'une battue:
        crit_dist = max(0.1 * liste_battues[i, 0], 2 * tolerance)

        # Recherche de la frappe la plus proche

        ind_max = min(
            i2 + np.floor(liste_battues[i, 0] / tolerance) + 1, Nb_att - 2)

        # !!! FJ : Dans le cas limite ou i2 = ind_max (cf fichier bug_1.pckt,
        # on a une expression de la forme [] - un truc, et le comportement par
        # défaut dans ce cas est différent entre scilab et Python -> il faut
        # gérer à part ce cas.
        # Le code original :
        # test = np.abs(Note_classees[i2+1:ind_max+1, 0] - Note_classees[i2, 0] - liste_battues[i, 0])
        # devient :
        if i2 >= ind_max:
            test = np.abs(Note_classees[i2, 0] + liste_battues[i, 0])
        else:
            test = np.abs(
                Note_classees[int(i2 + 1):int(ind_max + 1), 0] - Note_classees[i2, 0] - liste_battues[int(i), 0])
        distance = np.min(test)
        ind_possible = np.argmin(test) + 1
        # !!! FJ : cette initialisation semble inutile, à confirmer
        #temp_batt = [liste_battues[i, 0]]
        # OK tant que ça marche
        temp_batt = []
        Nb_prop = 1
        while (distance < crit_dist) and ((ind_max) < Nb_att - 1):
            Nb_prop += 1

            # !!! FJ : Je ne sais pas bien ce qu'est censé faire le code là,
            # mais je trouve dans mes fichiers des cas (cf bug_2.pckt) où
            # i2+ind_possible dépasse la limite du tableau -> j'ajoute un test,
            # mais il faudrait voir quelle est la bonne solution
            if i2 + ind_possible < Note_classees.shape[0]:
                temp_batt.append(
                    abs(Note_classees[i2, 0] - Note_classees[i2 + ind_possible, 0]))
            else:
                break

            # Mise a jour de la battue (moyenne des battues trouvees
            # precedemment)
            # !!! FJ : Ça ne sert à rien de faire ces assignations à chaque boucle while, il suffirait de le faire à la fin
            # On devrait pouvoir le sortir, à tester
            liste_battues[i, 0] = np.mean(temp_batt)
            liste_battues[i, 1] = Note_classees[i2 +
                                                ind_possible, 0] - Note_classees[i1, 0]
            liste_battues[i, 2] = Nb_prop
            # Re-setting for next loop
            # !!! FJ : Est-ce qui se passe vraiment ce qu'on veut là ? ind_possible n'est pas recalculé au cours de la boucle
            # OUI le commentaire est faux ind_possible est modifié à la
            # dernière ligne de cette boucle
            i2 += ind_possible
            ind_max = min(
                i2 + np.floor(liste_battues[i, 0] / tolerance) + 1, Nb_att - 2)

            # !!! FJ : il y a un cas bizarre qui arrive notamment sur
            # 'current_super_enerve.pckt', je suis obligé d'ajouter un if pour
            # reproduire le comportement de scilab dans ce cas pour lequel
            # []-1 = -1 alors que pour numpy []-1 = []
            if i2 >= ind_max:
                test = np.abs(Note_classees[i2, 0] + liste_battues[i, 0])
            else:
                #                 print("ind_max: %s" % ind_max)
                #                 print("i: %s" % i)
                #                 print("i2: %s" % i2)
                test = np.abs(Note_classees[(
                    i2 + 1):int(ind_max) + 1, 0] - Note_classees[i2, 0] - liste_battues[i, 0])
            distance = np.min(test)
            ind_possible = np.argmin(test) + 1
        del temp_batt

    # !!! FJ : J'ai pas bien suivi ce que fait l'algo, mais ce qu'on trouve dans
    # liste_battues est un peu douteux (plusieurs fois la même ligne), à vérifier
    # OK, comme l'algo apprend la batue, il peut s'adapter et tomber sur les
    # mêmes valeurs
    ind_tempo = np.argmax(liste_battues[:, 2])
    # !!! FJ : problème l'ordre que sort gsort de scilab pour les valeurs identique est différent de celui que j'obtiens avec np.sort
    # -> pour avoir le même résultat je suis obligé d'implémenter ma propre fonction arggsort
    k = arggsort(liste_battues[:, 2])

    battues_classees = np.zeros([Nb_battues, 3])

    for i in np.arange(Nb_battues):
        battues_classees[i, :] = liste_battues[k[i], 0:3]

    # !!! FJ : dist_batt est définie mais non-utilisée dans la version scilab
    # OK
    # dist_batt = np.zeros([Nb_battues, Nb_battues])

    # Si une battue a un multiple dans la liste, augmentation de son poids
    for i in np.arange(Nb_battues):
        for j in np.arange(Nb_battues):
            # !!! FJ : J'ai un fichier (bug_5.pckt) sur lequel j'obtiens une division par 0 ici
            # j'ajoute un test, mais il faudrait voir quelle est la bonne
            # solution
            if battues_classees[j, 0] != 0.:
                if ((battues_classees[i, 0] / battues_classees[j, 0]) > 1.9) \
                        and ((battues_classees[i, 0] / battues_classees[j, 0]) < 2.1):
                    battues_classees[i, 2] = battues_classees[i, 2] * 3.0

    # !!! FJ : je ne pige pas bien pourquoi il y a le code suivant, les battues
    # n'étant pas ordonnées le while s'arrete sur la première de la liste plus
    # grande que 0.4, mais on n'a aucune autre garantie sur sa valeur
    # si le but c'est de retirer toutes les valeurs en dessous de 0.4,
    # ça ne marche pas
    # -> Il y a bien un problème en fait il faudrait retirer ces valeurs de battue bien avant au moment où on fait
    # ind_battues = np.nonzero(battues<1.3)[0]
    ind_mini = 0

    if np.max(battues_classees[:, 0]) > 0.4:
        while battues_classees[ind_mini, 0] < 0.4:
            ind_mini += 1

    ind_tempo = np.argmax(battues_classees[ind_mini:Nb_battues, 2])

    # !!! FJ : le deuxième indice est manquant dans scilab
    # OK
    # !!! FJ : J'ai un fichier (bug_5.pckt) sur lequel j'obtiens une division par 0 ici
    # j'ajoute un test, mais il faudrait voir quelle est la bonne solution
    if battues_classees[ind_tempo + ind_mini, 0] != 0.:
        tempo = 60 / battues_classees[ind_tempo + ind_mini, 0]
    else:
        tempo = 1.

    # FJ !!! : ajout pour probleme fichier bug_4.pckt. Voir coment bien gérer
    # ce cas
    if tempo < 0.:
        tempo = 1.

    return tempo


def METRIQUE(note_piece):
    ####################################################
    # ESTIMATION DE LA METRIQUE (binaire / ternaire)
    ####################################################

    # Autocorrelation-based estimate of meter
    # m = meter(nmat,<option>)
    # Returns an autocorrelation-based estimate of meter of NMAT.
    # Based on temporal structure and on Thomassen's melodic accent.
    # Uses discriminant function derived from a collection of 12000 folk melodies.
    # m = 2 for simple duple
    # m = 3 for simple triple or compound
    #
    # Input argument:
    #    NMAT = notematrix
    #    OPTION (Optional, string) = Argument 'OPTIMAL' uses a weighted combination
    #      of duration and melodic accents in the inference of meter (see Toiviainen & Eerola, 2004).
    #
    # Output:
    #    M = estimate of meter (M=2 for simple duple; M=3 for simple triple or compound)
    #
    # References:
    #    Brown, J. (1993). Determination of the meter of musical scores by
    #         autocorrelation. Journal of the Acoustical Society of America,
    #         94(4), 1953-1957.
    #    Toiviainen, P. & Eerola, T. (2004). The role of accent periodicities in meter induction:
    #         a classification study, In x (Ed.), Proceedings of the ICMPC8. xxx:xxx.
    #
    # Change History :
    # Date        Time    Prog    Note
    # 11.8.2002    18:36    PT    Created under MATLAB 5.3 (Macintosh)
    #© Part of the MIDI Toolbox, Copyright © 2004, University of Jyvaskyla, Finland
    # See License.txt

    # !!! FJ : pourquoi y'a ça ?:
    #    ac = ofacorr(onsetfunc(nmat,'dur'));

    NDIVS = 4  # four divisions per quater note
    MAXLAG = 8
    ob = note_piece[:, 5]
    acc = note_piece[:, 6]

    vlen = NDIVS * max(2 * MAXLAG, np.ceil(np.max(ob)) + 1)
    of = np.zeros(int(vlen))

    # Note FJ : La fonction round de numpy n'utilise pas la même convention que scilab pour les valeurs
    # pile entre deux entiers (par exemple 0.5).
    # Pour avoir le même comportement que sous scilab, au lieu d'utiliser :
    # ind = np.mod(np.round(ob*NDIVS), of.shape[0])
    # on utilise la fonction round par défaut de Python qui a le même
    # comportement que dans scilab :
    my_round = np.vectorize(lambda x: round(x))
    ind = np.mod(my_round(ob * NDIVS), of.shape[0])

    # Note FJ : on ne peut pas remplacer la boucle suivante par
    # of[ind.astype(int)] += acc
    # car elle n'est pas équivalente si ind contient plusieurs fois le même
    # indice
    for k in np.arange(ind.shape[0]):
        of[int(ind[k])] += acc[k]

    # !!! FJ : éventuellement mettre of-of.mean dans une variable temporaire ici
    ac = np.correlate(of - of.mean(), of - of.mean(),
                      mode='full')[of.shape[0] - 1:]

    # !!! FJ : ind1 et ind2 sont définis mais pas utilisés dans scilab
    # ind1 = 1;
    # ind2 = min(length(ac),MAXLAG*NDIVS+1);

    if ac[0] > 0:
        ac /= ac[0]

    # !!! FJ : réécrire les boucles for ci-dessous en vectoriel
    if ac.shape[0] % 2 > 0.:
        for i in np.arange(np.floor(ac.shape[0] / 2)):
            ac[i] = ac[2 + 2 * i]
    else:
        for i in np.arange(np.floor(ac.shape[0] / 2) - 1):
            ac[int(i)] = ac[2 + 2 * int(i)]

    if ac[3] >= ac[5]:
        metrique = 2
    else:
        metrique = 3

    return metrique


if __name__ == '__main__':
    #    duree, tristesse, Enervement, Complexite, metrique, tonalite, tempo, cocktail = PIANOCKTAIL('current_super_enerve.pckt')
    #    a1 = "Duree =  "+str(duree)+" - Tristesse =  "+str(tristesse)+" - Enervement =  "+str(Enervement)
    #    a2 = "Complexite =  "+str(Complexite)+" - Metrique =  "+str(metrique)+" - Tonalite =  "+str(tonalite)
    #    a3 = "Tempo =  "+str(tempo)+" - Cocktail =  "+str(cocktail)
    #    print(a1)
    #    print(a2)
    #    print(a3)

    precision = '10.13'

    import sys
    if len(sys.argv) > 1:
        precision = sys.argv[1]

    from glob import glob
    data_dir_path = '.'

    if len(sys.argv) > 2:
        data_dir_path = sys.argv[2]

    file_names = glob(data_dir_path + '/*.pckt')
    file_names.sort()
    #file_names = ['random_96.pckt']

    form = '{:' + precision + 'f}'

    for file_name in file_names:
        duree, tristesse, Enervement, Complexite, metrique, tonalite, tempo, cocktail = PIANOCKTAIL(
            file_name)
        print('fichier    : ' + file_name)
        print('duree      : ' + form.format(duree))
        print('tristesse  : ' + form.format(tristesse))
        print('enervement : ' + form.format(Enervement))
        print('complexite : ' + form.format(Complexite))
        print('metrique   : ' + form.format(metrique))
        print('tonalite   : ' + form.format(tonalite))
        print('tempo      : ' + form.format(tempo))
        print('cocktail   : ' + cocktail)
        print('')
        sys.stdout.flush()
        sys.stderr.write(file_name + ' processed by Python\n')
        sys.stderr.flush()

    sys.stderr.write('\nProcessing by Python finished\n\n')
    sys.stderr.flush()
