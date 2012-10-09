function [tempo] = TEMPO(note_piece)

size_piece = size(note_piece);
nbnotes_piece = size_piece(1,1)


/////////////////////////////////////////////////////////////////////////////////////////////////////////

//                              ESTIMATION DU TEMPO

/////////////////////////////////////////////////////////////////////////////////////////////////////////


// Calcul de la fin de chacune des notes (en seconde) et remplacement de la colonne
// "durï¿½e en beats"

note_piece(:,2) = note_piece(:,6) + note_piece(:,7);
//disp(note_piece(1:20,6))
//disp(note_piece(1:20,7))
// DECOMPTE DES EVENEMENTS DISTINCTS (i.e UN ACCORD = UN EVENEMENT)
// Matrice Note_classees : 
//                   Colonne 1: Instant de la frappe (en secondes)
//                   Colonne 2: Instant de fin de la note (en secondes)
//                   Colonne 3: Nombre de touches frappï¿½es ï¿½ la fois

Dur_min=min(note_piece(:,7));
//tolerance=0.05;
tolerance=max(Dur_min/3,0.05);
//disp('tolerance')
//disp(tolerance)
//
Nb_att=1;
Note_classees = zeros(nbnotes_piece,3);
Note_classees(1,1)=note_piece(1,6);
Note_classees(1,2)=note_piece(1,2);
//
//
Last_time=note_piece(1,6);
//
dtim1=0.1;
//
for i=2:nbnotes_piece;
    dti = note_piece(i,6)-Last_time;
//    if dti~=0
    if dti>=tolerance    // Non-simultanéité de 2 notes
        Nb_att=Nb_att+1;
        Note_classees(Nb_att,1)=note_piece(i,6);
        Note_classees(Nb_att,2)=note_piece(i,2);
        Note_classees(Nb_att,3)=1;
        Last_time=note_piece(i,6);
    else                 // Simultanéité de 2 notes
        Note_classees(Nb_att,3)=Note_classees(Nb_att,3)+1;
    end    
end
//
//
//disp(Nb_att)
//disp(Note_classees)
//
//
// MARQUAGE / PONDERATION DES EVENEMENTS POUR EN DEDUIRE UN POIDS RYTHMIQUE
//
//
Poids_tempo=zeros(Nb_att,6);
Poids_tempo(:,1)=Note_classees(1:Nb_att,1);
//
// Marquage Nr1: Valeurs successives d'inter-onsets proches/égales
//
Poids_tempo(1,2)=1;   // Initialisation
//
for i=3:Nb_att
    dti=Note_classees(i,1)-Note_classees(i-1,1);
    dtim1=Note_classees(i-1,1)-Note_classees(i-2,1);
    if abs(dtim1-dti)<=0.2*dtim1
        Poids_tempo(i,2)=1;
    end
end
//
//
// Marquage Nr2: intervalles entre attaques allongï¿½s
//
Poids_tempo(1,3)=1;   // Initialisation
//
for i=2:(Nb_att-1)
    dti=Note_classees(i,1)-Note_classees(i-1,1);
    dtip1=Note_classees(i+1,1)-Note_classees(i,1);
    if dtip1/dti<=1.2
        Poids_tempo(i,3)=1;
    end
end
//
//
//
// Marquage Nr3: Nb de notes par accord
//
Poids_tempo(:,4)=Note_classees(1:Nb_att,3)-ones(Nb_att,1);
//
//
// Marquage Nr4: Nb d'accords se terminant sur une attaque donnï¿½e
//
//
dist_time=zeros(Nb_att,1);
//
for i=3:Nb_att
    for j=1:Nb_att
        dist_time(j,1)=abs(Note_classees(j,2)-Note_classees(i,1));
    end
    marq2 = find(dist_time<=tolerance);
    l=length(marq2);
    if l>0
        Poids_tempo(i,5)=length(marq2)-1;
    end
end
//
//
Poids_tempo(:,6)=1*Poids_tempo(:,2)+1*Poids_tempo(:,3)+2*Poids_tempo(:,4)+2*Poids_tempo(:,5);
//
//plot(Poids_tempo(1:50,1),Poids_tempo(1:50,6),'m-',Poids_tempo(1:50,1),Poids_tempo(1:50,2),'c-',Poids_te//mpo(1:50,1),Poids_tempo(1:50,4),'b-',Poids_tempo(1:50,1),Poids_tempo(1:50,5),'k-')
//
//
// GENERATION DE BATTUES POSSIBLES
// Principe: on choisit un ï¿½vï¿½nement
//
//--------------------------------------------------------------------------
//--------------------------------------------------------------------------
//--------------------------------------------------------------------------
//           TEMPO DE L'ENSEMBLE DU MORCEAU
//
// Initialisation: début de la propagation des battues à partir du 1/12 de la durée du morceau
//disp(Note_classees(1:50,:))
indices = find(Note_classees>(Note_classees(Nb_att,1)/12));
i1=max(indices(1),2);
//disp(Note_classees(:,1))
//disp(Note_classees)
//disp(Nb_att)
//
// On vérifie que le point de départ est bien un maximum local de poids tempo (borné à 1/6 de la longueur du morceau)

while or([(Poids_tempo(i1-1,6)>=Poids_tempo(i1,6)),(Poids_tempo(i1+1,6)>=Poids_tempo(i1,6))])&(i1<int(Nb_att/6))
    i1=i1+1;
end
//
//
// Initialisation des battues: intervalles de temps entre la valeur de départ et toutes les notes jouées jusque là
//
battuesav=Note_classees(i1)-Note_classees(1:(i1-1));
battuesap=Note_classees((i1+1):(i1+1+int(Nb_att/6)))-Note_classees(i1);
battues(1:i1+int(Nb_att/6))=[battuesav;battuesap];
//disp(battues)
//disp(battuesap)
//disp(battues);
//
//
// Elimination des battues de plus de 1.3 secondes
//
//
ind_battues=find(battues<1.3);
//
//
a = size(ind_battues);
Nb_battues=a(2);
//
liste_battues=zeros(Nb_battues,3);
//
for i=1:Nb_battues
    k=ind_battues(i);
    liste_battues(i,1)=battues(k);
end
//
liste_battues(:,1)=gsort(liste_battues(:,1))
//
//
//
for i=1:Nb_battues
//    disp('==================================================================')
//    liste_battues(i,1)
    j=1;
    i2=i1;
// Critere pour la propagation d'une battue:
    crit_dist = max(0.1*liste_battues(i,1),2*tolerance)
//    disp(crit_dist)
// Receherche de la frappe la plus proche 

    ind_max=min(i2+floor(liste_battues(i,1)/tolerance)+1,Nb_att-1);
    test=abs(Note_classees((i2+1):ind_max,1) - Note_classees(i2,1) - liste_battues(i,1));
    [distance,ind_possible]=min(test);
//    disp(ind_possible)
    temp_batt(j)=liste_battues(i,1);
    Nb_prop=1
    while (distance<crit_dist)&((ind_max)<Nb_att)
        Nb_prop=Nb_prop+1
 //&((ind_max)<Nb_att)
        temp_batt(j)=abs(Note_classees(i2,1)-Note_classees(i2+ind_possible,1));
        // Mise a jour de la battue (moyenne des battues trouvees
        // precedemment)
        liste_battues(i,1)=mean(temp_batt);
        liste_battues(i,2)=Note_classees(i2+ind_possible,1)-Note_classees(i1,1);
        liste_battues(i,3)=Nb_prop;
        // Re-setting for next loop
        i2=i2+ind_possible;
        ind_max=min(i2+floor(liste_battues(i,1)/tolerance)+1,Nb_att-1);
//        Note_classees((i2+1):ind_max,1)
//        Note_classees(i2,1)
//        liste_battues(i,1)
        test=abs(Note_classees((i2+1):ind_max,1) - Note_classees(i2,1) - liste_battues(i,1));
        [distance,ind_possible]=min(test);
        j=j+1;
    end
    clear temp_batt;
end
//
//size(liste_battues)
//
[a,ind_tempo]=max(liste_battues(:,3));
[tmp,k]=gsort(liste_battues(:,3));
//disp(k)
//disp(size(k))
battues_classees=zeros(Nb_battues,3);
//disp(size(liste_battues))
//disp(Nb_battues)
for i=1:Nb_battues
  battues_classees(i,:)=liste_battues(k(i,1),1:3);
end
//disp(liste_battues)
//disp(battues_classees)
dist_batt=zeros(Nb_battues,Nb_battues)
//k=1

// Si une battue a un multiple dans la liste, augmentation de son poids
for i=1:Nb_battues,
  for j=1:Nb_battues,
    if ((battues_classees(i,1)/battues_classees(j,1))>1.9)&((battues_classees(i,1)/battues_classees(j,1))<2.1)
    battues_classees(i,3)=battues_classees(i,3)*3.0
    end
  end
end
//
// disp(dist_batt)
//
// disp(battues_classees)
ind_mini=1
while battues_classees(ind_mini,1)<0.4
    ind_mini=ind_mini+1
end


[a,ind_tempo]=max(battues_classees(ind_mini:Nb_battues,3))
// disp(max(battues_classees(ind_mini:Nb_battues,3)))
// disp(ind_mini)

// disp(ind_tempo)
// disp(ind_mini)
// disp(ind_tempo+ind_mini)
// disp(battues_classees(ind_mini:Nb_battues,:))

tempo=60/battues_classees((ind_tempo+ind_mini-1));

//disp(battues_classees((ind_tempo+ind_mini-1)))

//tempo_moy = Nb_att/(duree/60);
//
//



endfunction

