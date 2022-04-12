#!/bin/tcsh
#
# source $HEADAS/headas-init.csh
set marke = $#argv
if($marke == 0) then
  echo "Aufgabe: Bildrekonstruktion mit ESO-IRBis: a) Erzeugung der Plotts, welche die gemessenen"
  echo "         Visbilities/Closure phases vergleichen mit den aus den 3 besten Rekonstruktionen abgeleiteten;"
  echo "         b) Abbildung der besten Rek. (ungefaltet/gefaltet) und das Original, falls vorhanden, wenn das Original"
  echo "            nicht vorhanden, dann werden das Startbild & der Start-Prior dargestellt."
  echo
  echo "Eingaben: [FOV of reconstruction in mas] [result fits file from ESO-IRBis] [scaling factor for the convolution of the reconstruction]"
  echo "          [cost funcion, regularization function, oradius,step,count, mu,mufac,count, npix, startmode,startparam] [OBJ-Name] [model image/no]"
  echo "          [FWHM of fitted Gaussian (mas)] [diameter of fitted UD (mas)] [diameter of fitted FDD (mas)] [power for the UV density weight]"
  echo "          [1: for frequency 0 a visibility is calculated, 0: this is not done] [FWHM of the fitted Lorentz function (mas)]"
#  echo "Ausgaben: Visibility-Plotts: visa.ps visb.ps visc.ps, diffvisa.ps diffvisb.ps diffvisc.ps; CP-Plotts: cpa.ps cpb.ps cpc.ps"
  echo "Ausgaben: Visibility-Plotts: visa.ps visb.ps visc.ps; CP-Plotts: cpa.ps cpb.ps cpc.ps"

else

set fov  = $1  # fov in mas
set fits = $2  # Ergebniss-Fits-File aus ESO-IRBis
set convscale = $3  # Scale factor for the convolution (1.0 means telescope diameter = max basline; >1.0 means telescope diameter > max basline)
set costFunc = $4
set regFunc  = $5
set oradiusStart = $6
set stepSize     = $7
set oradiusNumber = $8
set muStart  = $9
set muFactor = $10
set muNumber = $11
set npix = $12
set startmode = $13
set startparam = $14
set objname = $15
set model = $16
set tgauss = $17
set tud    = $18
set tfdd   = $19
set weightPower = $20
set calcVis2f0 = $21
set tld    = $22

echo "Inputs: "
echo "fov fits convscale costFunc regFunc oradiusStart stepSize oradiusNumber muStart muFactor muNumber npix startmode startparam objname model tgauss tud tfdd weightPower calcVis2f0: "
echo $fov $fits $convscale $costFunc $regFunc $oradiusStart $stepSize $oradiusNumber $muStart $muFactor $muNumber $npix $startmode $startparam $objname $model $tgauss $tud $tfdd $tld $weightPower $calcVis2f0

echo "a) Plotts: Visbilities/Closure phases"
set vis20 = `echo *.vis2.dat`
set cp    = `echo *.cp.dat`
set vis2 = $vis20.new; rm -f $vis2; awk '{ if($1!="#") {print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$12,$13,$14,$11;}; }' $vis20 > $vis2
ls -l $vis2 $cp
echo "FOV = $fov mas"
#
# vis2 - new (11-12-15):
# measured squared visibilities vs reconstructed squared visibilities
# nr lambda u v bl vis2 err gd ud fdd ld rec1 rec2 rec3
# 1  2      3 4 5  6    7   8  9  10  11 12   13   14
#
# $vis20.new  == $vis2
# nr lambda u v bl vis2 err gd ud fdd rec1 rec2 rec3 ld
# 1  2      3 4 5  6    7   8  9  10  11   12   13   14
#
# cp :
# nr lambda u1 v1 u2 v2 amp cp cperr biserr rec1_amp rec1_cp rec2_amp rec2_cp rec3_amp rec3_cp
# 1  2      3  4  5  6  7   8  9     10     11       12      13       14      15       16
# cp: neu seit 13-11-15:
# nr lambda u1 v1 u2 v2 amp amperr cp cperr biserr rec1_amp rec1_cp rec2_amp rec2_cp rec3_amp rec3_cp
# 1  2      3  4  5  6  7   8      9  10    11     12       13       14      15      16       17
rm -f $vis2.0 $cp.0

# ----- Erzeugung der Chi^2 und ResidualRatio aus den eingelesenen V^2-Daten  $vis2
set chivis2a = `awk 'BEGIN{sum=0.;z=0.} { if($1!="#") {res=($6-$11)/$7; sum=sum+res^2; z=z+1.;}; } END{printf "%8.3f\n", sum/z;}' $vis2`
set chivis2b = `awk 'BEGIN{sum=0.;z=0.} { if($1!="#") {res=($6-$12)/$7; sum=sum+res^2; z=z+1.;}; } END{printf "%8.3f\n", sum/z;}' $vis2`
set chivis2c = `awk 'BEGIN{sum=0.;z=0.} { if($1!="#") {res=($6-$13)/$7; sum=sum+res^2; z=z+1.;}; } END{printf "%8.3f\n", sum/z;}' $vis2`
set resratioa = `awk 'BEGIN{sump=0.;summ=0.;} { if($1!="#") {res=($6-$11)/$7; if(res>0.) {sump=sump+res;}; if(res<=0.) {summ=summ-res;}; }; } END{rr=10000.; if((sump>0.)&&(summ>0.)) {rr=sump/summ; if(rr<1.) {rr=summ/sump;};}; printf "%8.3f\n",rr;}' $vis2`
set resratiob = `awk 'BEGIN{sump=0.;summ=0.;} { if($1!="#") {res=($6-$12)/$7; if(res>0.) {sump=sump+res;}; if(res<=0.) {summ=summ-res;}; }; } END{rr=10000.; if((sump>0.)&&(summ>0.)) {rr=sump/summ; if(rr<1.) {rr=summ/sump;};}; printf "%8.3f\n",rr;}' $vis2`
set resratioc = `awk 'BEGIN{sump=0.;summ=0.;} { if($1!="#") {res=($6-$13)/$7; if(res>0.) {sump=sump+res;}; if(res<=0.) {summ=summ-res;}; }; } END{rr=10000.; if((sump>0.)&&(summ>0.)) {rr=sump/summ; if(rr<1.) {rr=summ/sump;};}; printf "%8.3f\n",rr;}' $vis2`

# ----- Erzeugung der Visibilities $vis2.0 aus den quadrierten Visibilities in $vis2
awk -v fov=$fov 'BEGIN{z=0;} { if(($1=="#")&&(z==0)) {print "# Nr. |", "U |", "V |", "Vis |", "VisErr |", "Gaussian |", "Uniform d |", "Fully dark d |", "Vis (1.rec) |", "Vis (2.rec) |", "Vis (3.rec) |", "f (1/arcsec) |", "Lorentz ";}; \
                               if(($1=="#")&&(z==1)) {print "# 1   |", "2 |", "3 |", "4   |", "5      |", "6        |", "7        |", "8            |", "9           |", "10          |", "11          |", "12          |", "13   ";}; \
                               if($1!="#") {rad=sqrt($3^2+$4^2); radc=rad*1000.; vis=sqrt(sqrt($6^2)); if($6==0.0) {viserr=0.0;}; if($6!=0.0) {viserr=0.5*$7/vis;}; \
                                            visgauss=sqrt(sqrt($8^2)); visud=sqrt(sqrt($9^2)); visfdd=sqrt(sqrt($10^2)); visld=sqrt(sqrt($14^2)); visa=sqrt(sqrt($11^2)); visb=sqrt(sqrt($12^2)); visc=sqrt(sqrt($13^2)); \
                                            print $1,$3,$4,vis,viserr,visgauss,visud,visfdd, visa,visb,visc,radc,visld;}; z=z+1;}' $vis2 > $vis2.0


# ----- Erzeugung der Chi^2 und ResidualRatio aus den eingelesenen CP-Daten  $cp
set pi = `echo 1. | awk '{print atan2($1,$1)*4.;}'`
set chicpa   = `awk -v p=$pi 'BEGIN{sum=0.;z=0.} { if($1!="#") {d0=$9-$13;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d=d0;dd=d00;if(dd>d11) {d=d1;dd=d11;};if(dd>d22) {d=d2;dd=d22};res=d/$10; sum=sum+res^2; z=z+1.;}; } END{printf "%8.3f\n", sum/z;}' $cp`
set chicpb   = `awk -v p=$pi 'BEGIN{sum=0.;z=0.} { if($1!="#") {d0=$9-$15;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d=d0;dd=d00;if(dd>d11) {d=d1;dd=d11;};if(dd>d22) {d=d2;dd=d22};res=d/$10; sum=sum+res^2; z=z+1.;}; } END{printf "%8.3f\n", sum/z;}' $cp`
set chicpc   = `awk -v p=$pi 'BEGIN{sum=0.;z=0.} { if($1!="#") {d0=$9-$17;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d=d0;dd=d00;if(dd>d11) {d=d1;dd=d11;};if(dd>d22) {d=d2;dd=d22};res=d/$10; sum=sum+res^2; z=z+1.;}; } END{printf "%8.3f\n", sum/z;}' $cp`
set cpresa   = `awk -v p=$pi 'BEGIN{sump=0.;summ=0.;} { if($1!="#") {d0=$9-$13;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d=d0;dd=d00;if(dd>d11) {d=d1;dd=d11;};if(dd>d22) {d=d2;dd=d22};res=d/$10; if(res>0.) {sump=sump+res;}; if(res<=0.) {summ=summ-res;}; }; } END{rr=10000.; if((sump>0.)&&(summ>0.)) {rr=sump/summ; if(rr<1.) {rr=summ/sump;};}; printf "%8.3f\n",rr;}' $cp`
set cpresb   = `awk -v p=$pi 'BEGIN{sump=0.;summ=0.;} { if($1!="#") {d0=$9-$15;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d=d0;dd=d00;if(dd>d11) {d=d1;dd=d11;};if(dd>d22) {d=d2;dd=d22};res=d/$10; if(res>0.) {sump=sump+res;}; if(res<=0.) {summ=summ-res;}; }; } END{rr=10000.; if((sump>0.)&&(summ>0.)) {rr=sump/summ; if(rr<1.) {rr=summ/sump;};}; printf "%8.3f\n",rr;}' $cp`
set cpresc   = `awk -v p=$pi 'BEGIN{sump=0.;summ=0.;} { if($1!="#") {d0=$9-$17;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d=d0;dd=d00;if(dd>d11) {d=d1;dd=d11;};if(dd>d22) {d=d2;dd=d22};res=d/$10; if(res>0.) {sump=sump+res;}; if(res<=0.) {summ=summ-res;}; }; } END{rr=10000.; if((sump>0.)&&(summ>0.)) {rr=sump/summ; if(rr<1.) {rr=summ/sump;};}; printf "%8.3f\n",rr;}' $cp`

# Calculation of qrec from the above calculated Chi^2/RR data
# with qrec = ( |Cv-1|+|RR{V^2}-1| + |Cb-1|+|RR{CP}-1| )/4; mit Cv=Chi^2{V^2} oder Cv=1/Chi^2{V^2} bei Chi^2{V^2}<1, Cb=Chi^2{CP} oder Cb=1/Chi^2{CP} bei Chi^2{CP}<1
set qreca = `echo $chivis2a $resratioa $chicpa $cpresa | awk '{Cv=$1; if(Cv<1.) {Cv=1./$1;}; Cb=$3; if(Cb<1.) {Cb=1./$3;}; qrec = ( sqrt((Cv-1.)^2)+sqrt(($2-1.)^2)+sqrt((Cb-1.)^2)+sqrt(($4-1.)^2) )/4.; printf "%12.3f", qrec;}'`
echo $qreca
set cpqreca = `echo $chivis2a $resratioa $chicpa $cpresa | awk '{Cv=$1; if(Cv<1.) {Cv=1./$1;}; Cb=$3; if(Cb<1.) {Cb=1./$3;}; qrec = ( sqrt((Cb-1.)^2)+sqrt(($4-1.)^2) )/2.; printf "%12.3f", qrec;}'`
echo $cpqreca

# Plots: die rek. CP durch Addition von +-360Grad anpassen an die gemessenen CPs (moeglichst kleiner Abstand)
set pi = `echo 1. | awk '{print atan2($1,$1)*4.;}'`
awk -v p=$pi 'BEGIN{z=0;} { if(($1=="#")&&(z==0)) {print "# Nr. |", "U1 |", "V1 |", "U2 |", "V2 |", "CP [deg]|", "CP err |", "CP (1.rec) |", "CP (2.rec) |", "CP (3.rec) |"}; \
                             if(($1=="#")&&(z==1)) {print "# 1   |", "2  |", "3  |", "4  |", "5  |", "6       |", "7      |", "8          |", "9          |", "10         |";}; \
                             if($1!="#") {d0=$9-$13;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d8=$13;dd=d00;if(dd>d11) {d8=$13-2.*p;dd=d11;};if(dd>d22) {d8=$13+2.*p;dd=d22}; \
                                          d0=$9-$15;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d9=$15;dd=d00;if(dd>d11) {d9=$15-2.*p;dd=d11;};if(dd>d22) {d9=$15+2.*p;dd=d22}; \
                                          d0=$9-$17;d1=d0+2.*p;d2=d0-2.*p;d00=d0^2;d11=d1^2;d22=d2^2;d10=$17;dd=d00;if(dd>d11) {d10=$17-2.*p;dd=d11;};if(dd>d22) {d10=$17+2.*p;dd=d22}; \
                                          cp=$9*180./p; cperr=$10*180./p; cpa=d8*180./p; cpb=d9*180./p; cpc=d10*180./p; print $1,$3,$4,$5,$6,cp,cperr,cpa,cpb,cpc;}; z=z+1;}' $cp > $cp.0

# A) plott of the visibilities as function of the length of the spatial frequency
# Spaltenbelgung von $vis2.0:
# Nr. |", "U |", "V |", "Vis |", "VisErr |", "Gaussian |", "Uniform d |", "Fully dark d |", "Vis (1.rec) |", "Vis (2.rec) |", "Vis (3.rec) |", "f (1/arcsec) |", "Lorentz "
# 1   |", "2 |", "3 |", "4   |", "5      |", "6        |", "7         |", "8            |", "9           |", "10          |", "11          |", "12           |", "13   "

rm -f visa.ps visb.ps visc.ps
rm -f $vis2.0.sorted ttt; awk '{if($1!="#") {print $0;};}' $vis2.0 > ttt; sort -n -k 12 ttt > $vis2.0.sorted

ls -l {$vis2}* {$cp}*

set psplotva = visa.ps
rm -f $psplotva
# ./gnupl.csh
# Input: [name of the ascii file of the data] [text for the measured data] [text for the fitted data] 
#        [column of the X axis in the file] [column of the measured data] [column of the errors of the measured data]
#        [column of the fitted data] [text on X axis] [text on Y axis] [name of the ps plot]
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" $psplotva "Chi\^2/RR = $chivis2a/$resratioa" 9
ls -l $psplotva

set psplotvb = visb.ps
rm -f $psplotvb
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" $psplotvb "Chi\^2/RR = $chivis2b/$resratiob" 10
ls -l $psplotva $psplotvb

set psplotvc = visc.ps
rm -f $psplotvc
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" $psplotvc "Chi\^2/RR = $chivis2c/$resratioc" 11

ls -l $psplotva $psplotvb $psplotvc
rm -f t1.eps t2.eps; cp $psplotva t1.eps; cp $psplotvb t2.eps

# ./gnupl2.csh
# Input: [name of the ascii file of the data] [text for the measured data]
#        [column of the X axis in the file] [column of the measured data] [column of the errors of the measured data]
#        [text on X axis] [text on Y axis] [name of the ps plot]
#        [text for the fitted data] [column of the fitted data] ...

# A2) plot of the fitted model visibilities and measured visibilities as a function of the length of the spatial frequency
rm -f gaussa.ps uda.ps fdda.ps lda.ps gaussudfdda.ps
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" gaussa.ps "fitted Gaussian model (FWHM={$tgauss}mas)" 6
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" uda.ps "fitted Uniform disk model (diameter={$tud}mas)" 7
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" fdda.ps "fitted Fully darkened disk model (diameter={$tfdd}mas)" 8
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" lda.ps "fitted Lorentz function (FWHM={$tld}mas)" 13
$SCRIPTS/gnupl2.csh $vis2.0.sorted "measured visibilities" 12 4 5 "spatial frequency (1/arcsec)" "Visibility" gaussudfdda.ps \
                            "fitted Uniform disk model (diameter={$tud}mas)" 7 "fitted Gaussian model (FWHM={$tgauss}mas)" 6 "fitted Fully darkened disk model (diameter={$tfdd}mas)" 8 \
			    "fitted Lorentz function (FWHM={$tld}mas)" 13

ls -l gaussa.ps uda.ps fdda.ps lda.ps gaussudfdda.ps

# B) plott of the difference of the visibilities^2 ordered according to increasing values of the measured visibilities
# vis2:
# nr u v bl vis2 err gd ud fdd rec1 rec2 rec3 # nicht _nt
# 1  2 3 4  5    6   7  8  9   10   11   12
# nr lambda u v bl vis2 err gd ud fdd rec1 rec2 rec3  # _nt
# 1  2      3 4 5  6    7   8  9  10  11   12   13
rm -f diffvisa.ps diffvisb.ps diffvisc.ps
rm -f $vis2.sorted ttt; awk '{if($1!="#") {print $0;};}' $vis2 > ttt; sort -n -k 6 ttt > $vis2.sorted
rm -f $vis2.sorted.0; awk 'BEGIN{z=0;} {z=z+1; print $0,z;}' $vis2.sorted > $vis2.sorted.0

# Input: [name of the ascii file of the data] [text for the measured data] [text for the fitted data] 
#        [column of the X axis in the file] [column of the measured data] [column of the errors of the measured data]
#        [column of the fitted data] [text on X axis] [text on Y axis] [name of the ps plot]
rm -f $vis2.sorted.00; awk '{print $11, $11-$6, $7, 0;}' $vis2.sorted.0 > $vis2.sorted.00
# $SCRIPTS/gnupl2.csh $vis2.sorted.00 "(measured - reconstructed) visibilities\^2: Chi\^2/RR = $chivis2a/$resratioa" "-" 1 2 3 4 "number of increasing measured visibility\^2" "(measured - reconstructed) Visibility\^2" diffvisa.ps

rm -f $vis2.sorted.00; awk '{print $9, $10-$4, $5, 0;}' $vis2.sorted.0 > $vis2.sorted.00
# $SCRIPTS/gnupl2.csh $vis2.sorted.00 "(measured - reconstructed) visibilities\^2: Chi\^2/RR = $chivis2b/$resratioc" "-" 1 2 3 4 "number of increasing measured visibility\^2" "(measured - reconstructed) Visibility\^2" diffvisb.ps

rm -f $vis2.sorted.00; awk '{print $9, $11-$4, $5, 0;}' $vis2.sorted.0 > $vis2.sorted.00
# $SCRIPTS/gnupl2.csh $vis2.sorted.00 "(measured - reconstructed) visibilities\^2: Chi\^2/RR = $chivis2c/$resratioc" "-" 1 2 3 4 "number of increasing measured visibility\^2" "(measured - reconstructed) Visibility\^2" diffvisc.ps

# ls -l diffvisa.ps diffvisb.ps diffvisc.ps

# C) plott of the closure phases ordered according to increasing values of the measured closure phases
# $cp.0 :
#  Nr. |", "U1 |", "V1 |", "U2 |", "V2 |", "CP [deg]|", "CP err |", "CP (1.rec) |", "CP (2.rec) |", "CP (3.rec) |
#  1   |", "2  |", "3  |", "4  |", "5  |", "6       |", "7      |", "8          |", "9          |", "10         |
# a) sorting the CPs according to increasing values of the measuered CPs --> $cp.0.sorted.0
rm -f $cp.0.sorted ttt; awk '{if($1!="#") {print $0;};}' $cp.0 > ttt; sort -n -k 6 ttt > $cp.0.sorted
rm -f $cp.0.sorted.0; awk 'BEGIN{z=0;} { z=z+1; print $0, z; }' $cp.0.sorted > $cp.0.sorted.0

# b) plotting the CPs as function of the longest baseline vector:
# $cp.0.lbl :
# length of longest baseline | measured CP | CP error | CP (1.rec) | CP (2.rec) | CP (3.rec) |
# 1                            2             3          4            5            6
rm -f $cp.0.lbl $cp.0.lbl.sorted
awk '{ if($1!="#") {u=sqrt($2^2+$3^2); v=sqrt($4^2+$5^2); wx=$2+$4; wy=$3+$5; w=sqrt(wx^2+wy^2); ll=u; if(v>ll) {ll=v;}; \
                    if(w>ll) {ll=w;}; lll=ll*1000.; print lll, $6, $7, $8, $9, $10;}; }' $cp.0 > $cp.0.lbl;
sort -n -k 1 $cp.0.lbl > $cp.0.lbl.sorted


# ./gnupl2.csh
# Input: [name of the ascii file of the data] [text for the measured data]
#        [column of the X axis in the file] [column of the measured data] [column of the errors of the measured data]
#        [text on X axis] [text on Y axis] [name of the ps plot]
#        [text for the fitted data] [column of the fitted data] ...

# to a)
rm -f cpa.ps
$SCRIPTS/gnupl2.csh $cp.0.sorted.0 "measured closure phases" 11 6 7 "number of increasing measured closure phase" "Closure phase (deg)" cpa.ps \
"Chi^2/RR = $chicpa/$cpresa" 8
rm -f cpb.ps
$SCRIPTS/gnupl2.csh $cp.0.sorted.0 "measured closure phases" 11 6 7 "number of increasing measured closure phase" "Closure phase (deg)" cpb.ps \
"Chi^2/RR = $chicpb/$cpresb" 9
rm -f cpc.ps
$SCRIPTS/gnupl2.csh $cp.0.sorted.0 "measured closure phases" 11 6 7 "number of increasing measured closure phase" "Closure phase (deg)" cpc.ps \
"Chi^2/RR = $chicpc/$cpresc" 10

# to b)
rm -f cpaa.ps
$SCRIPTS/gnupl3.csh $cp.0.lbl.sorted "measured closure phases" 1 2 3 "spatial frequency of longest baseline (1/arcsec)" "Closure phase (deg)" cpaa.ps \
"Chi^2/RR = $chicpa/$cpresa" 4
rm -f cpbb.ps
$SCRIPTS/gnupl3.csh $cp.0.lbl.sorted "measured closure phases" 1 2 3 "spatial frequency of longest baseline (1/arcsec)" "Closure phase (deg)" cpbb.ps \
"Chi^2/RR = $chicpb/$cpresb" 5
rm -f cpcc.ps
$SCRIPTS/gnupl3.csh $cp.0.lbl.sorted "measured closure phases" 1 2 3 "spatial frequency of longest baseline (1/arcsec)" "Closure phase (deg)" cpcc.ps \
"Chi^2/RR = $chicpc/$cpresc" 6

ls -l cpa.ps cpb.ps cpc.ps cpaa.ps cpbb.ps cpcc.ps


cp $SCRIPTS/plot3b.tex .
rm -f plot3b.ps results.1.reconstruction.ps; rm -f t1.eps t2.eps t3.eps; cp gaussudfdda.ps t1.eps; cp visa.ps t2.eps; cp cpa.ps t3.eps; latex plot3b.tex; dvips plot3b.dvi; mv plot3b.ps results.1.reconstruction.ps
rm -f plot3b.ps results.2.reconstruction.ps; rm -f t1.eps t2.eps t3.eps; cp gaussudfdda.ps t1.eps; cp visb.ps t2.eps; cp cpb.ps t3.eps; latex plot3b.tex; dvips plot3b.dvi; mv plot3b.ps results.2.reconstruction.ps
rm -f plot3b.ps results.3.reconstruction.ps; rm -f t1.eps t2.eps t3.eps; cp gaussudfdda.ps t1.eps; cp visc.ps t2.eps; cp cpc.ps t3.eps; latex plot3b.tex; dvips plot3b.dvi; mv plot3b.ps results.3.reconstruction.ps
rm -f plot3b.*

ls -l results.1.reconstruction.ps results.2.reconstruction.ps results.3.reconstruction.ps


echo "b) Abbildung der besten Rek. (ungefaltet/gefaltet) und das Original oder das Startbild & Prior"

	echo "--------------- fdump --------------------- A ---------------------------"

	# quality parameter of the best reconstruction:
         fdump  $fits\[2\] \!rec33.txt QREC -; set qrec = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt COST -; set cost = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt CHI2BIS -; set chi2bis = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt RRESBIS -; set rresbis = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt CHI2VIS2 -; set chi2vis2 = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt RRESVIS2 -; set rresvis2 = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt CHI2CP -; set chi2cp = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`
         fdump  $fits\[2\] \!rec33.txt RRESCP -; set rrescp = `awk '{if ($0 ~ /  1  /) {printf "%12.4f", $2;}}' rec33.txt`

        set cpqrec = `echo $chi2cp $rrescp | awk '{ Cb=$1; if($1<1.) {Cb=1./$1;}; qrec = ( sqrt((Cb-1.)^2) + sqrt(($2-1.)^2) )/2.; printf "%12.4f", qrec; }'`
	echo "# qrec   |  cost  |  chi2bis |  rresbis | chi2vis2 | rresvis2 | chi2cp | cpqrec "
	echo  $qrec "  " $cost "  " $chi2bis "   " $rresbis "  " $chi2vis2 "   " $rresvis2 "  " $chi2cp "  " $rrescp "  " $cpqrec
	echo "--------------- fdump --------------------- E ---------------------------"
        

#        rm -f tkhh; awk -v w=$qrec '{ if(($15 == w",")||($15 == w"0,")||($15 == w"00,")) {print $0;}; }' esorex.log > tkhh
#        rm -f tkhh; awk -v w=$qrec '{ if(($15 == w",")||($15 == w"0,")||($15 == w"00,")) {print $0;}; }' esorex.log > tkhh
#        set khh0       = `awk '{w=$45;} END{printf "%12.3f", w;}' tkhh`              ; if( x$khh0 == "x" ) set khh = -1; if( x$khh0 != "x" ) set khh = $khh0; echo $khh; rm -f tkhh
        set qrecbest = `awk -v w=$qrec 'BEGIN{mindist=1e10;} { dist=sqrt((w-$15)^2); if(dist < mindist) {mindist=dist; qrecbest=$15;}; } END{print qrecbest;}' esorex.log`
        rm -f tkhh; awk -v w=$qrecbest '{ if($15 == w) {print $0;}; }' esorex.log > tkhh
        set khh0       = `awk 'BEGIN{z=0;} {z=z+1; if(z==1) {w=$45;};} END{printf "%12.3f", w;}' tkhh`              ; if( x$khh0 == "x" ) set khh = -1; if( x$khh0 != "x" ) set khh = $khh0; echo $khh; rm -f tkhh
	set khhm = $khh

        rm -f liste0;  fstruct colinfo=no $fits >> liste0
        set bestrecNr = 0; set bestrecconvNr = `awk '{if ($0 ~ /REC_CONV /) {print $1;}}' liste0`; set uvcoverageNr = `awk '{if ($0 ~ /UV_COVERAGE /) {print $1;}}' liste0`
	set startimageNr = `awk '{if ($0 ~ /START_IMAGE /) {print $1;}}' liste0`; set prioriamgeNr = `awk '{if ($0 ~ /PRIOR_IMAGE /) {print $1;}}' liste0`

	  if( $model != "no" ) then
	    set modelNr = `awk '{if ($0 ~ /MODEL_IMAGE /) {print $1;}}' liste0`; set modelconvNr = `awk '{if ($0 ~ /MODEL_CONV /) {print $1;}}' liste0`
	    rm -f bestrec.fits;  fextract $fits\[$bestrecNr\] \!bestrec.fits\[0\]
	    rm -f bestrecconv.fits;  fextract $fits\[$bestrecconvNr\] \!bestrecconv.fits\[0\]
	    rm -f model.fits;  fextract $fits\[$modelNr\] \!model.fits\[0\]
	    rm -f modelconv.fits; fextract $fits\[$modelconvNr\] \!modelconv.fits\[0\]
	  else
	    set khhm = -1
	    rm -f bestrec.fits;  fextract $fits\[$bestrecNr\] \!bestrec.fits\[0\]
            rm -f bestrecconv.fits;  fextract $fits\[$bestrecconvNr\] \!bestrecconv.fits\[0\]
	  endif

	if( X$khhm == "X" ) set khhm = 0.000
	echo "khh khhm = " $khh $khhm

	set khhm0 = $khh
	if( ($model != "no") && ($khhm != 0.000) ) set khh = $khhm


	rm -f liste khhm0.ll
        echo " calcVis2f0 weightPower convscale = " $calcVis2f0  $weightPower $convscale
        echo "# quality parameter of the best reconstruction:" >> liste
	echo "# ----------------------------------------------" >> liste 
        echo "# qrec   |  cost  |  chi2bis |  rresbis | chi2vis2 | rresvis2 | chi2cp  | rrescp | dist$convscale || FOV (mas) |Reg-Fct.|oradius step number|mu factor number|calcVis2f0|weightPower| npix |startmode|startparam|directory  " >> liste
        echo  $qrec "   " $cost "  " $chi2bis "   " $rresbis "  " $chi2vis2 "   " $rresvis2 "   " $chi2cp "  " $rrescp "  " $khh "    " $fov "       " $regFunc "       " $oradiusStart $stepSize $oradiusNumber "     " $muStart $muFactor $muNumber "        " $calcVis2f0  "       " $weightPower "      " $npix "     " $startmode "      " $startparam  "   " $cwd:t >> liste
#        echo  $qrec "   " $cost "  " $chi2bis "   " $rresbis "  " $chi2vis2 "   " $rresvis2 "   " $chi2cp "  " $rrescp "  " $khhm "    " $fov "       " $regFunc "       " $oradiusStart $stepSize $oradiusNumber "     " $muStart $muFactor $muNumber "        " $calcVis2f0  "       " $weightPower "      " $npix "     " $startmode "      " $startparam  "   " $cwd:t >> liste
 
	echo "# quality parameter of the best reconstruction (dist from esorex.log):" >> khhm0.ll
        echo "# ----------------------------------------------" >> khhm0.ll
        echo "# qrec   |  cost  |  chi2bis |  rresbis | chi2vis2 | rresvis2 | chi2cp  | rrescp | dist$convscale || FOV (mas) |Reg-Fct.|oradius step number|mu factor number|calcVis2f0|weightPower| npix |startmode|startparam|directory  " >> khhm0.ll
        echo  $qrec "   " $cost "  " $chi2bis "   " $rresbis "  " $chi2vis2 "   " $rresvis2 "   " $chi2cp "  " $rrescp "  " $khhm0 "    " $fov "       " $regFunc "       " $oradiusStart $stepSize $oradiusNumber "     " $muStart $muFactor $muNumber "        " $calcVis2f0  "       " $weightPower "      " $npix "     " $startmode "      " $startparam  "   " $cwd:t >> khhm0.ll
#

# size0 : Kantenlaenge in Pixel des dargestellten Felder
        set size0 = 256

	# readout of the best reconstruction, unconvolved and convolved, the :
	foreach sc (sqrt lin log)
	  rm -f $fits:r.bestrec.$sc.jpeg $fits:r.bestrec.$sc.pdf $fits:r.bestrec.$sc.ps;  fextract $fits\[$bestrecNr\] \!bestrec.fits\[0\]; \
          set ff = bestrec.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
	  mv $ff:r.$disp.ps $fits:r.bestrec.$sc.ps; mv $ff:r.$disp.pdf $fits:r.bestrec.$sc.pdf                                       # best rec unconvolved

          rm -f $fits:r.bestrecconv.$sc.jpeg $fits:r.bestrecconv.$sc.pdf $fits:r.bestrecconv.$sc.ps;  fextract $fits\[$bestrecconvNr\] \!bestrecconv.fits\[0\]; \
	  set ff = bestrecconv.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
	  mv $ff:r.$disp.ps $fits:r.bestrecconv.$sc.ps; mv $ff:r.$disp.pdf $fits:r.bestrecconv.$sc.pdf                               # best rec convolved

	  rm -f $fits:r.uv.$sc.jpeg $fits:r.uv.$sc.pdf $fits:r.uv.$sc.ps;  fextract $fits\[$uvcoverageNr\] \!uv.fits\[0\]; \
	  set ff = uv.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
	  mv $ff:r.$disp.ps $fits:r.uv.$sc.ps; mv $ff:r.$disp.pdf $fits:r.uv.$sc.pdf                     # uv coverage

	  if( $model == "no" ) then
	    rm -f $fits:r.start.$sc.jpeg $fits:r.start.$sc.pdf $fits:r.start.$sc.ps;  fextract $fits\[$startimageNr\] \!start.fits\[0\]; \
	    set ff = start.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
            mv $ff:r.$disp.ps $fits:r.start.$sc.ps; mv $ff:r.$disp.pdf $fits:r.start.$sc.pdf                            # start image  unconvolved

	    rm -f $fits:r.prior.$sc.jpeg $fits:r.prior.$sc.pdf $fits:r.prior.$sc.ps;  fextract $fits\[$prioriamgeNr\] \!prior.fits\[0\]; \
	    set ff = prior.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
            mv $ff:r.$disp.ps $fits:r.prior.$sc.ps; mv $ff:r.$disp.pdf $fits:r.prior.$sc.pdf                            # prior image  unconvolved
          endif

	  if( $model != "no" ) then
	    rm -f $fits:r.model.$sc.jpeg $fits:r.model.$sc.pdf $fits:r.model.$sc.ps;  fextract $fits\[$modelNr\] \!model.fits\[0\]; \
	    set ff = model.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
            mv $ff:r.$disp.ps $fits:r.model.$sc.ps; mv $ff:r.$disp.pdf  $fits:r.model.$sc.pdf                         # model image  unconvolved

	    rm -f $fits:r.modelconv.$sc.jpeg $fits:r.modelconv.$sc.pdf $fits:r.modelconv.$sc.ps; fextract $fits\[$modelconvNr\] \!modelconv.fits\[0\]; \
	    set ff = modelconv.fits; ftcopy ''$ff'[-*,-*]' $ff.0; mv $ff.0 $ff; set disp = $sc; if( $sc == "lin" ) set disp = linear; $SCRIPTS/fits2ps.fits2bitmap.csh $ff $disp
            mv $ff:r.$disp.ps $fits:r.modelconv.$sc.ps; mv $ff:r.$disp.pdf $fits:r.modelconv.$sc.pdf                  # model image convolved
	 endif
	end

          if( $model != "no" ) then
            set modelNr = `awk '{if ($0 ~ /MODEL_IMAGE /) {print $1;}}' liste0`; set modelconvNr = `awk '{if ($0 ~ /MODEL_CONV /) {print $1;}}' liste0`
            rm -f bestrec.fits;  fextract $fits\[$bestrecNr\] \!bestrec.fits\[0\]
            rm -f bestrecconv.fits;  fextract $fits\[$bestrecconvNr\] \!bestrecconv.fits\[0\]
            rm -f model.fits;  fextract $fits\[$modelNr\] \!model.fits\[0\]
            rm -f modelconv.fits; fextract $fits\[$modelconvNr\] \!modelconv.fits\[0\]
          else
            rm -f bestrec.fits;  fextract $fits\[$bestrecNr\] \!bestrec.fits\[0\]
            rm -f bestrecconv.fits;  fextract $fits\[$bestrecconvNr\] \!bestrecconv.fits\[0\]
          endif

#	rm -f tt1.eps tt2.eps tt3.eps; cp gaussudfdda.ps tt1.eps; cp visa.ps tt2.eps; cp cpa.ps tt3.eps
	rm -f tt1.eps tt2.eps tt3.eps; cp gaussudfdda.ps tt1.eps; cp visa.ps tt2.eps; cp cpaa.ps tt3.eps
# *.eps-Files fuer $SCRIPTS/plot6plus3text.csh
# --> tt1.eps == gaussudfdda.ps
# --> tt2.eps == visa.ps
# --> tt3.eps == cpaa.ps

	foreach sc (sqrt lin log)
	if( $model == "no" ) then
          set i = 0
          foreach f ($fits:r.start.$sc.ps $fits:r.prior.$sc.ps $fits:r.bestrec.$sc.ps $fits:r.bestrecconv.$sc.ps $fits:r.uv.$sc.ps $fits:r.uv.$sc.ps)
	    @ i++; ps2eps $f; rm -f t$i.eps; mv $f:r.eps t$i.eps; ls -l t$i.eps
	  end
	else
          set i = 0
          foreach f ($fits:r.model.$sc.ps $fits:r.modelconv.$sc.ps $fits:r.bestrec.$sc.ps $fits:r.bestrecconv.$sc.ps $fits:r.uv.$sc.ps $fits:r.uv.$sc.ps)
            @ i++; ps2eps $f; rm -f t$i.eps; mv $f:r.eps t$i.eps; ls -l t$i.eps
          end
	endif
# *.eps-Files fuer $SCRIPTS/plot6plus3text.csh
# --> t1.eps == $fits:r.model.$sc.ps or $fits:r.start.$sc.ps
# --> t2.eps == $fits:r.modelconv.$sc.ps or $fits:r.prior.$sc.ps
# --> t3.eps == $fits:r.bestrec.$sc.ps
# --> t4.eps == $fits:r.bestrecconv.$sc.ps
# --> t5.eps == $fits:r.uv.$sc.ps

rm -f param.txt
echo "FOV $fov mas" >> param.txt
echo "npix $npix" >> param.txt
echo "cost $costFunc" >> param.txt
echo "reg $regFunc" >> param.txt
echo "weightpower $weightPower" >> param.txt
echo "orad $oradiusStart mas / $stepSize mas / $oradiusNumber" >> param.txt
echo "mu $muStart/$muFactor/$muNumber" >> param.txt
echo "startmode $startmode" >> param.txt
echo "startparam $startparam mas" >> param.txt
echo "superres $convscale" >> param.txt
echo "$objname" >> param.txt

rm -f results.txt
set chi2bis00 = `echo $chi2bis | awk '{printf "%12.3f", $1;}'`
set rresbis00 = `echo $rresbis | awk '{printf "%12.3f", $1;}'`
set chi2vis200 = `echo $chi2vis2 | awk '{printf "%12.3f", $1;}'`
set rresvis200 = `echo $rresvis2 | awk '{printf "%12.3f", $1;}'`
set chivis2a00 = `echo $chivis2a | awk '{printf "%12.3f", $1;}'`
set resratioa00 = `echo $resratioa | awk '{printf "%12.3f", $1;}'`
set chi2cp00   = `echo $chi2cp   | awk '{printf "%12.3f", $1;}'`
set rrescp00   = `echo $rrescp   | awk '{printf "%12.3f", $1;}'`
set chicpa00   = `echo $chicpa   | awk '{printf "%12.3f", $1;}'`
set cpresa00   = `echo $cpresa   | awk '{printf "%12.3f", $1;}'`
set khh00      = `echo $khh      | awk '{printf "%12.3f", $1;}'`
set qrec00     = `echo $qrec     | awk '{printf "%12.3f", $1;}'`
set cpqrec00   = `echo $cpqrec   | awk '{printf "%12.3f", $1;}'`
set khhm00     = `echo $khhm     | awk '{printf "%12.3f", $1;}'`
set qreca00    = `echo $qreca    | awk '{printf "%12.3f", $1;}'`
set cpqreca00  = `echo $cpqreca  | awk '{printf "%12.3f", $1;}'`
echo "BIS+POW $chi2bis00 $rresbis00" >> results.txt
echo "V2 $chi2vis200 $rresvis200 $chivis2a00 $resratioa00" >> results.txt
echo "CP $chi2cp00 $rrescp00 $chicpa00 $cpresa00" >> results.txt
echo "dist qrec cpqrec $khh00 $qrec00 $cpqrec00  $khhm00 $qreca00 $cpqreca00" >> results.txt


#    uv coverage plot:
     $SCRIPTS/uvplot.csh; rm -f t66.eps; mv uv.ps t66.eps

# *.eps-File fuer $SCRIPTS/plot6plus3text.csh
# --> t66.eps == uv.ps

        cp $SCRIPTS/plot6b.tex .; latex plot6b.tex; dvips plot6b.dvi; rm -f reks.$sc.ps; mv plot6b.ps reks.$sc.ps
	$SCRIPTS/plot6plus3text.csh; rm -f RR.konv.iterated.rek1.$sc.ps; mv plot6plus3text.ps RR.konv.iterated.rek1.$sc.ps
        rm -f plot6plus3text.* plot6b.*
	end

        ls -l RR.konv.iterated.rek1.sqrt.ps RR.konv.iterated.rek1.lin.ps RR.konv.iterated.rek1.log.ps
        ls -l results.1.reconstruction.ps results.2.reconstruction.ps results.3.reconstruction.ps

# Erzeugung des ASCII-Files *.vis2 (altes Format fuer Fortran-Code von IRBis):
# Spaltenbelegung von *.vis2:
set lam0 = `awk 'BEGIN{sum1=0.; sum2=0.;} { if($1!="#") {sum1=sum1+$2; sum2=sum2+1.;}; } END{print (sum1/sum2)*1000000.;}' $vis2`
#  ID     Vis^2   Vis^2Err   u[m]  v[m]

rm -f $vis2:r.vis2.0; awk '{ if($1!="#") {frad=sqrt($3*$3+$4*$4); fac=$5/frad; ux=$3*fac; uy=$4*fac; print $1, $6, $7, ux,uy;}; }' $vis2 > $vis2:r.vis2.0
rm -f head; echo "# uv-Vektoren zur Bezugswellenlaenge $lam0 mu" >> head
rm -f $vis2:r.vis2; cat head $vis2:r.vis2.0 > $vis2:r.vis2


endif

