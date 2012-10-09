function [tonalite] = TONALITE(note_piece)
// ,tonalite
size_piece = size(note_piece);
nbnotes_piece = size_piece(1,1)


/////////////////////////////////////////////////////////////////////////////////////////////////////////

//                              ESTIMATION DE LA TONALITE

/////////////////////////////////////////////////////////////////////////////////////////////////////////

//
//
// Tonalité:
//key_piece = kkkey(note_piece);
// Key of NMAT according to the Krumhansl-Kessler algorithm
// k = kkkey(nmat);
// Returns the key of NMAT according to the Krumhansl-Kessler algorithm.
//
// Input argument: 
//	NOTE_PIECE = notematrix
//
// Output: 
//	K = estimated key of NMAT encoded as a number
// 	encoding: 	C major = 1, C# major = 2, ...
//           		c minor = 13, c# minor = 14, ...
//
// Remarks:
//
// See also KEYMODE, KKMAX, and KKCC.
//
// Example:
//
// Reference:
//	Krumhansl, C. L. (1990). Cognitive Foundations of Musical Pitch.
//	New York: Oxford University Press.
//
//  Author		Date
//  P. Toiviainen	8.8.2002
//© Part of the MIDI Toolbox, Copyright © 2004, University of Jyvaskyla, Finland
// See License.txt

// Correlations of pitch-class distribution with Krumhansl-Kessler tonal hierarchies
// c = kkcc(nmat,<opt>);
// Returns the correlations of the pitch class distribution PCDIST1
// of NMAT with each of the 24 Krumhansl-Kessler profiles.
//
// Input arguments: 
//	NMAT = notematrix
//	OPT = OPTIONS (optional), 'SALIENCE' return the correlations of the 
//     pitch-class distribution according to the Huron & Parncutt (1993) 
//     key-finding algorithm.
//
// Output: 
//	C = 24-component vector containing the correlation coeffients
//		between the pitch-class distribution of NMAT and each 
// 		of the 24 Krumhansl-Kessler profiles.
//
// Remarks: REFSTAT function is called to load the key profiles.
//
// Example: c = kkcc(nmat, 'salience')
//
// See also KEYMODE, KKMAX, and KKKEY in the MIDI Toolbox.
//
// References:
//	Krumhansl, C. L. (1990). Cognitive Foundations of Musical Pitch.
//	New York: Oxford University Press.
//
// Huron, D., & Parncutt, R. (1993). An improved model of tonality 
//     perception incorporating pitch salience and echoic memory. 
//     Psychomusicology, 12, 152-169. 
//

pc = modulo(note_piece(:,4),12)+1;

tau = 0.5;
accent_index = 2;
dur=note_piece(:,7);
dur_acc=(1-exp(-dur/tau)).^accent_index;

pcds=zeros(1,12);      // SCILAB: zeros

[size_pc,tmp]=size(pc);
for k=1:size_pc      // SCILAB: lstsize
	pcds(pc(k)) = pcds(pc(k))+dur_acc(k);
end
pcds = pcds/sum(pcds + 1e-12);      // SCILAB: sum

kkprofs=[0.39	0.14	0.21	0.14	0.27	0.25	0.15	0.32	0.15	0.22	0.14	0.18;
0.18	0.39	0.14	0.21	0.14	0.27	0.25	0.15	0.32	0.15	0.22	0.14;
0.14	0.18	0.39	0.14	0.21	0.14	0.27	0.25	0.15	0.32	0.15	0.22;
0.22	0.14	0.18	0.39	0.14	0.21	0.14	0.27	0.25	0.15	0.32	0.15;
0.15	0.22	0.14	0.18	0.39	0.14	0.21	0.14	0.27	0.25	0.15	0.32;
0.32	0.15	0.22	0.14	0.18	0.39	0.14	0.21	0.14	0.27	0.25	0.15;
0.15	0.32	0.15	0.22	0.14	0.18	0.39	0.14	0.21	0.14	0.27	0.25;
0.25	0.15	0.32	0.15	0.22	0.14	0.18	0.39	0.14	0.21	0.14	0.27;
0.27	0.25	0.15	0.32	0.15	0.22	0.14	0.18	0.39	0.14	0.21	0.14;
0.14	0.27	0.25	0.15	0.32	0.15	0.22	0.14	0.18	0.39	0.14	0.21;
0.21	0.14	0.27	0.25	0.15	0.32	0.15	0.22	0.14	0.18	0.39	0.14;
0.14	0.21	0.14	0.27	0.25	0.15	0.32	0.15	0.22	0.14	0.18	0.39;
0.38	0.16	0.21	0.32	0.15	0.21	0.15	0.28	0.24	0.16	0.2	0.19;
0.19	0.38	0.16	0.21	0.32	0.15	0.21	0.15	0.28	0.24	0.16	0.20;
0.2	0.19	0.38	0.16	0.21	0.32	0.15	0.21	0.15	0.28	0.24	0.16;
0.16	0.2	0.19	0.38	0.16	0.21	0.32	0.15	0.21	0.15	0.28	0.24;
0.24	0.16	0.2	0.19	0.38	0.16	0.21	0.32	0.15	0.21	0.15	0.28;
0.28	0.24	0.16	0.2	0.19	0.38	0.16	0.21	0.32	0.15	0.21	0.15;
0.15	0.28	0.24	0.16	0.2	0.19	0.38	0.16	0.21	0.32	0.15	0.21;
0.21	0.15	0.28	0.24	0.16	0.2	0.19	0.38	0.16	0.21	0.32	0.15;
0.15	0.21	0.15	0.28	0.24	0.16	0.2	0.19	0.38	0.16	0.21	0.32;
0.32	0.15	0.21	0.15	0.28	0.24	0.16	0.2	0.19	0.38	0.16	0.21;
0.21	0.32	0.15	0.21	0.15	0.28	0.24	0.16	0.2	0.19	0.38	0.16;
0.16	0.21	0.32	0.15	0.21	0.15	0.28	0.24	0.16	0.2	0.19	0.38];


[n,p] = size([pcds; kkprofs]');
covpcds = [pcds; kkprofs]' - ones(n,p) * mean([pcds; kkprofs]');
covpcds = covpcds'*covpcds/(n-1);

//covpcds=cov([pcds; kkprofs]');       // SCILAB: corr

c2=zeros(1,24);      // SCILAB: zeros
for k=2:25
	c2(k-1)=covpcds(1,k)/sqrt(covpcds(1,1)*covpcds(k,k));      // SCILAB: sqrt
end
[tmp, tonalite] = max(c2);      // SCILAB: max

endfunction

