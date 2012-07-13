function [metrique] = METRIQUE(note_piece)
// ,tonalite
/////////////////////////////////////////////////////////////////////////////////////////////////////////

//                              ESTIMATION DE LA METRIQUE (binaire / ternaire)

/////////////////////////////////////////////////////////////////////////////////////////////////////////


//Autocorrelation-based estimate of meter
// m = meter(nmat,<option>)
// Returns an autocorrelation-based estimate of meter of NMAT.
// Based on temporal structure and on Thomassen's melodic accent.
// Uses discriminant function derived from a collection of 12000 folk melodies.
// m = 2 for simple duple
// m = 3 for simple triple or compound
//
// Input argument:
//	NMAT = notematrix
//	OPTION (Optional, string) = Argument 'OPTIMAL' uses a weighted combination
//      of duration and melodic accents in the inference of meter (see Toiviainen & Eerola, 2004).
//
// Output:
//	M = estimate of meter (M=2 for simple duple; M=3 for simple triple or compound)
//
// References:
//     Brown, J. (1993). Determination of the meter of musical scores by 
//         autocorrelation. Journal of the Acoustical Society of America, 
//         94(4), 1953-1957.
//     Toiviainen, P. & Eerola, T. (2004). The role of accent periodicities in meter induction:
//	     a classification study, In x (Ed.), Proceedings of the ICMPC8. xxx:xxx.
//
// Change History :
// Date		Time	Prog	Note
// 11.8.2002	18:36	PT	Created under MATLAB 5.3 (Macintosh)
//© Part of the MIDI Toolbox, Copyright © 2004, University of Jyvaskyla, Finland
// See License.txt

//	ac = ofacorr(onsetfunc(nmat,'dur'));

NDIVS = 4; // four divisions per quater note
MAXLAG=8;
ob=note_piece(:,6);
acc=note_piece(:,7);

vlen = NDIVS*max([2*MAXLAG ceil(max(ob))+1]);
of = zeros(vlen,1);
ind = modulo(round(ob*NDIVS),length(of))+1;
for k=1:length(ind)
    of(ind(k)) = of(ind(k))+acc(k);
end
ac= corr(of,length(of))*length(of); 
ind1 = 1; 
ind2 = min(length(ac),MAXLAG*NDIVS+1);      


if ac(1)>0 ac = ac/ac(1); end

if modulo(length(ac),2)>0.
  for i=1:floor(length(ac)/2)
    ac(i)=ac(1+2*i);
  end
else
  for i=1:(floor(length(ac)/2)-1)
    ac(i)=ac(1+2*i);
  end
end
  
if ac(4) >= ac(6)
	metrique = 2
else
	metrique = 3
end

endfunction

