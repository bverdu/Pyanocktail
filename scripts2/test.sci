function [duree,densite,Enervement,Complexite,metrique,tonalite,tempo,cocktail,is_particulier] = PIANOCKTAIL(fname)
// ,tonalite
////////////////////////////////////////////////////////////////////////////
//  Ouverture des fichiers - Liste des ON /OFF / SUSTAIN
////////////////////////////////////////////////////////////////////////////

piano = fscanfMat(fname);

[l,tmp]=size(piano);

M_Off=[];
M_On=[];
M_Sust=[];

// Liste des ON / OFF / SUSTAIN

for i = 1:l,
  if piano(i,2)==1,
    tmp = piano(i,:);
    M_On=[M_On;tmp];
  elseif piano(i,2)==0,
    tmp = piano(i,:);
    M_Off=[M_Off;tmp];
  elseif piano(i,2)==5,
    tmp = piano(i,:);
    M_Sust=[M_Sust;tmp];
  end
end

// Conversion des instants millisecondes -> secondes
M_On(:,1)=M_On(:,1)/1000.;
M_Off(:,1)=M_Off(:,1)/1000.;
M_Sust(:,1)=M_Sust(:,1)/1000.;
[nbnotes_piece,tmp]=size(M_On);
[nbnoff_piece,tmp]=size(M_Off);
[nbsust_piece,tmp]=size(M_Sust);

//disp(M_On)
//disp(M_Off)

////////////////////////////////////////////////////////////////////////////
//  Verif des sustains: si nombre impair, off a la fin du morceau
////////////////////////////////////////////////////////////////////////////

if modulo(nbsust_piece,2)<>0
  tmp=[max(M_Off(:,1)) 5 0 0];
  M_Sust=[M_Sust;tmp];
  [nbsust_piece,tmp]=size(M_Sust);
end

// Separation des sustains On (impairs) / Off (pairs)

Sust_On=[];
Sust_Off=[];
for i=1:int(nbsust_piece/2.)
  Sust_On(i,:)=M_Sust(2*i-1.,:)
  Sust_Off(i,:)=M_Sust(2*i,:)
end

//disp(Sust_On)
//disp(Sust_Off)
////////////////////////////////////////////////////////////////////////////
//  Determination de la fin des notes
////////////////////////////////////////////////////////////////////////////




  for i = 1:nbnotes_piece
    j = 1; 
    while or([(M_Off(j,3)<>M_On(i,3)),(M_Off(j,1)<M_On(i,1))])&(j<nbnoff_piece),
      j=j+1;
    end
    M_On(i,2)=M_Off(j,1);
    M_Off(j,3)=0.;
  end




clear M_Off;
clear piano;


note_piece=zeros(nbnotes_piece,7);

note_piece(:,4)=M_On(:,3);

note_piece(:,5)=M_On(:,4);

note_piece(:,6)=M_On(:,1);

note_piece(:,7)=M_On(:,2)-M_On(:,1);

clear M_On

////////////////////////////////////////////////////////////////////////////////////////////////
// Modifications 26-Mai 2009 - Ajout de comparaison de morceaux prédéfinis
// 
// Liste des morceaux (1 = do naturel, par demi-tons) 
// une ligne de la matrice correspond à un morceau à tester
particularites=[[1,1,1,3,5,3];[1,1,1,3,1,-4]];

[Nb_particuliers,Lg_particuliers]=size(particularites);

// Variable stockant les tests "ce morceau est-il ceci ou bien cela?"

is_particulier=zeros(Nb_particuliers,1);


if (Nb_particuliers<>0)&(nbnotes_piece>(Lg_particuliers-1))
  for i=1:(nbnotes_piece-Lg_particuliers+1)
    for j=1:Nb_particuliers
      sequence=modulo((note_piece(i:(i+Lg_particuliers-1),4)-(note_piece(i,4)-1))',12);
      distance=norm(particularites(j,:)-(sequence));
      if distance<=1
	  is_particulier(j,1)=is_particulier(j,1)+1;
      end
    end
  end
end
///// Fin des modifs du 26 Mai
////////////////////////////////////////////////////////////////////////////////////////////////


size_piece = size(note_piece);
nbnotes_piece = size_piece(1,1)

// Duration of the piece in seconds:
t_piece = max(note_piece(:,6));
duree = t_piece

// Density of notes (notes/seconds):
densite = nbnotes_piece/t_piece


// Attaques:
Enervement = mean(note_piece(:,5))
//disp(note_piece(:,7))
// Duree moyenne / ecart type:
Complexite = mean(note_piece(:,7)) / stdev(note_piece(:,7))

exec('METRIQUE.sci',-1);
exec('TONALITE.sci',-1);
exec('TEMPO.sci',-1);
exec('RECETTE.sci',-1);

metrique=METRIQUE(note_piece);
//disp(note_piece)
tonalite=TONALITE(note_piece);
tempo=TEMPO(note_piece);

cocktail = RECETTE(duree,Complexite,tonalite,tempo);

endfunction



