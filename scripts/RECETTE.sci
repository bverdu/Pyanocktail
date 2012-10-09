function [recette1] = RECETTE(duree,complexite,tonalite,tempo)
// Ici on d�termine quoi mettre dans le verre !
// 
crit_duree = [0. 10. 30. 90. 180.];
crit_tempo = [50 80 120];

alcfort = ['alc01 ' 'alc02 ' 'alc03 ' 'alc04 ' 'alc05 ' 'alc06 ' 'alc07 ' 'alc08 ' 'alc09 ' 'alc10 ' 'alc11 ' 'alc12 '];

sodamaj = ['sj1 ' 'sj2 ' 'sj3 ' 'sj4 '];
sodamin = ['sn1 ' 'sn2 ' 'sn3 ' 'sn4 '];

complicado = ['tralala ']

recette = [];

// CHOIX DE L'ALCOOL FORT (Tonalite)
recette(1) = alcfort(modulo(tonalite,12));

// DOSAGE DE L'ALCOOL FORT (Duree du morceau)
if ((crit_duree(1)<duree) & (duree<=crit_duree(2))),
//    recette=strcat([recette,'0.']);
    recette(2) = '0 ';
  elseif ((crit_duree(2)<duree) & (duree<=crit_duree(3))),
//    recette=strcat([recette,'1.']);
    recette(2) = '1 ';
  elseif ((crit_duree(3)<duree) & (duree<=crit_duree(4))),
//    recette=strcat([recette,'2.']);
    recette(2) = '2 ';
  elseif ((crit_duree(4)<duree) & (duree<=crit_duree(5))),
//    recette=strcat([recette,'3.']);
    recette(2) = '3 ';
  elseif (duree>crit_duree(5)),
//    recette=strcat([recette,'4.']);
    recette(2) = '4 ';
end

// DETERMINATION DU SODA
// Pre-decoupage de la liste de sodas: majeur - mineur

if floor(tonalite/12)==0.,
    soda=sodamaj;
  elseif  floor(tonalite/12)==1.
    soda=sodamin;
  else,
    soda=[];
end

// DETERMINATION DU SODA
// Choix du soda proprement dit

if (tempo<crit_tempo(1)),
//    recette=strcat([recette,soda(1)]);
//    recette=strcat([recette,'3.']);
    recette(3) = soda(1);
    recette(4) = '3 ';
  elseif ((crit_tempo(1)<tempo) & (tempo<=crit_tempo(2))),
//    recette=strcat([recette,soda(2)]);
//    recette=strcat([recette,'3.']);
    recette(3) = soda(2);
    recette(4) = '3 ';
  elseif ((crit_tempo(2)<tempo) & (tempo<=crit_tempo(3))),
//    recette=strcat([recette,soda(3)]);
//    recette=strcat([recette,'3.']);
    recette(3) = soda(3);
    recette(4) = '3 ';
  elseif ((crit_tempo(3)<tempo)),
    recette(3) = soda(4);
    recette(4) = '3 ';
//    recette=strcat([recette,soda(4)]);
//    recette=strcat([recette,'3.']);
end


// LA PETITE TOUCHE DE VIRTUOSITE - C'EST PEUT-ETRE BON

if complexite>0.7,
    recette(5)=complicado(1);
    recette(6)='1 ';
end

recette1=strcat(recette);

endfunction

