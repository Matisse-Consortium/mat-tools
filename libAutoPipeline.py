import numpy as np
from astropy.io import fits


def matisseCalib(header,action,listCalibFile,calibPrevious):
    keyDetReadCurname=header['HIERARCH ESO DET READ CURNAME']
    keyDetChipName=header['HIERARCH ESO DET CHIP NAME']
    keyDetSeq1Dit=header['HIERARCH ESO DET SEQ1 DIT']
    keyDetSeq1Period=header['HIERARCH ESO DET SEQ1 PERIOD']
    keyInsPilId=header['HIERARCH ESO INS PIL ID']
    keyInsPinId=header['HIERARCH ESO INS PIN ID']
    keyInsDilId=header['HIERARCH ESO INS DIL ID']
    keyInsDinId=header['HIERARCH ESO INS DIN ID']
    keyInsPolId=header['HIERARCH ESO INS POL ID']
    keyInsFilId=header['HIERARCH ESO INS FIL ID']
    keyInsPonId=header['HIERARCH ESO INS PON ID']
    keyInsFinId=header['HIERARCH ESO INS FIN ID']

    res=calibPrevious
    if (action=="ACTION_MAT_CAL_DET_SLOW_SPEED" or 
        action=="ACTION_MAT_CAL_DET_FAST_SPEED" or
        action=="ACTION_MAT_CAL_DET_LOW_GAIN" or
        action=="ACTION_MAT_CAL_DET_HIGH_GAIN"):
        return [res,1]

    if (action=="ACTION_MAT_IM_BASIC" or action=="ACTION_MAT_IM_EXTENDED" or action=="ACTION_MAT_IM_REM"):
        nbCalib=0
        for elt in res:
            if (elt[1]=="BADPIX"):
                nbCalib+=1
        for elt in listCalibFile:
            hdu=fits.open(elt)
            tagCalib=matisseType(hdu[0].header)
            keyDetReadCurnameCalib=hdu[0].header['HIERARCH ESO DET READ CURNAME']
            keyTplStartCalib=hdu[0].header['HIERARCH ESO TPL START']
            keyDetChipNameCalib=hdu[0].header['HIERARCH ESO DET CHIP NAME']
            hdu.close()
            if (tagCalib=="BADPIX" and (keyDetReadCurnameCalib==keyDetReadCurname and keyDetChipNameCalib==keyDetChipName)):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
        if (nbCalib==1):
            status=1
        else:
            status=0
        return [res,status]

    if (action=="ACTION_MAT_EST_FLAT"):
        nbCalib=0
        for elt in res:
            if (elt[1]=="BADPIX" or 
                elt[1]=="FLATFIELD" or 
                elt[1]=="NONLINEARITY"):
                nbCalib+=1
        for elt in listCalibFile:
            hdu=fits.open(elt)
            tagCalib=matisseType(hdu[0].header)
            keyDetReadCurnameCalib=hdu[0].header['HIERARCH ESO DET READ CURNAME']
            keyDetChipNameCalib=hdu[0].header['HIERARCH ESO DET CHIP NAME']
            keyDetSeq1DitCalib=header['HIERARCH ESO DET SEQ1 DIT']
            keyTplStartCalib=hdu[0].header['HIERARCH ESO TPL START']
            hdu.close()
            if (tagCalib=="BADPIX" and (keyDetReadCurnameCalib==keyDetReadCurname and keyDetChipNameCalib==keyDetChipName)):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="FLATFIELD" and ((keyDetChipNameCalib=="AQUARIUS" and keyDetChipName=="AQUARIUS" and keyDetReadCurnameCalib==keyDetReadCurname and keyDetSeq1DitCalib==keyDetSeq1Dit) or (keyDetChipNameCalib=="HAWAII-2RG" and keyDetChipName=="HAWAII-2RG" and keyDetReadCurnameCalib==keyDetReadCurname and keyDetSeq1DitCalib==keyDetSeq1Dit))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="NONLINEARITY" and ((keyDetChipNameCalib=="AQUARIUS" and keyDetChipName=="AQUARIUS" and keyDetReadCurnameCalib==keyDetReadCurname and keyDetSeq1DitCalib==keyDetSeq1Dit) or (keyDetChipNameCalib=="HAWAII-2RG" and keyDetChipName=="HAWAII-2RG" and keyDetReadCurnameCalib==keyDetReadCurname and keyDetSeq1DitCalib==keyDetSeq1Dit))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
        if (nbCalib==3):
            status=1
        else:
            status=0
        return [res,status]


    if (action=="ACTION_MAT_RAW_ESTIMATES"):
        nbCalib=0
        for elt in res:
            if (elt[1]=="BADPIX" or 
                elt[1]=="OBS_FLATFIELD" or 
                elt[1]=="NONLINEARITY" or 
                elt[1]=="SHIFT_MAP" or
                elt[1]=="KAPPA_MATRIX"):
                nbCalib+=1

        for elt in listCalibFile:
            hdu=fits.open(elt)
            tagCalib=matisseType(hdu[0].header)
            keyTplStartCalib=hdu[0].header['HIERARCH ESO TPL START']
            keyDetReadCurnameCalib=hdu[0].header['HIERARCH ESO DET READ CURNAME']
            keyDetChipNameCalib=hdu[0].header['HIERARCH ESO DET CHIP NAME']
            keyDetSeq1DitCalib=hdu[0].header['HIERARCH ESO DET SEQ1 DIT']
            keyInsPilIdCalib=hdu[0].header['HIERARCH ESO INS PIL ID']
            keyInsPinIdCalib=hdu[0].header['HIERARCH ESO INS PIN ID']
            keyInsDilIdCalib=hdu[0].header['HIERARCH ESO INS DIL ID']
            keyInsDinIdCalib=hdu[0].header['HIERARCH ESO INS DIN ID']
            keyInsPolIdCalib=hdu[0].header['HIERARCH ESO INS POL ID']
            keyInsFilIdCalib=hdu[0].header['HIERARCH ESO INS FIL ID']
            keyInsPonIdCalib=hdu[0].header['HIERARCH ESO INS PON ID']
            keyInsFinIdCalib=hdu[0].header['HIERARCH ESO INS FIN ID']
            hdu.close()
            if (tagCalib=="BADPIX" and (keyDetReadCurnameCalib==keyDetReadCurname and keyDetChipNameCalib==keyDetChipName)):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="OBS_FLATFIELD" and 
                (keyDetChipNameCalib==keyDetChipName and keyDetReadCurnameCalib==keyDetReadCurname and 
                 (keyDetSeq1DitCalib==keyDetSeq1Dit or keyDetSeq1DitCalib==keyDetSeq1Period) and 
                 ((keyInsPilId==keyInsPilIdCalib and keyInsDilId==keyInsDilIdCalib and keyDetChipName=="HAWAII-2RG") or 
                  (keyInsPinId==keyInsPinIdCalib and keyInsDinId==keyInsDinIdCalib and keyDetChipName=="AQUARIUS")))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="NONLINEARITY" and 
                ((keyDetChipNameCalib=="AQUARIUS" and keyDetChipName=="AQUARIUS" and keyDetReadCurnameCalib==keyDetReadCurname and (keyDetSeq1DitCalib==keyDetSeq1Dit or keyDetSeq1DitCalib==keyDetSeq1Period)) or 
                 (keyDetChipNameCalib=="HAWAII-2RG" and keyDetChipName=="HAWAII-2RG" and keyDetReadCurnameCalib==keyDetReadCurname))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="SHIFT_MAP" and 
                (keyDetChipNameCalib==keyDetChipName and 
                 ((keyInsDilId==keyInsDilIdCalib and keyDetChipName=="HAWAII-2RG") or 
                  (keyInsDinId==keyInsDinIdCalib and keyDetChipName=="AQUARIUS")))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1           
            if (tagCalib=="KAPPA_MATRIX" and 
                (keyDetChipNameCalib==keyDetChipName and 
                 ((keyInsPolId==keyInsPolIdCalib and keyInsFilId!=keyInsFilIdCalib and keyInsDilId==keyInsDilIdCalib and keyDetChipName=="HAWAII-2RG") or 
                  (keyInsPonId==keyInsPonIdCalib and keyInsFinId==keyInsFinIdCalib and keyInsDinId==keyInsDinIdCalib and keyDetChipName=="AQUARIUS")))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="JSDC_CAT"):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
        if ((keyDetChipName=="AQUARIUS" and keyInsPinId=="PHOTO") or (keyDetChipName=="HAWAII-2RG" and keyInsPilId=="PHOTO")):
            if (nbCalib==5):
                status=1
            else:
                status=0
        if ((keyDetChipName=="AQUARIUS" and keyInsPinId!="PHOTO") or (keyDetChipName=="HAWAII-2RG" and keyInsPilId!="PHOTO")):
            if (nbCalib>=4):
                status=1
            else:
                status=0
        return [res,status]

    if (action=="ACTION_MAT_EST_KAPPA"):
        nbCalib=0
        for elt in res:
            if (elt[1]=="BADPIX" or 
                elt[1]=="OBS_FLATFIELD" or 
                elt[1]=="NONLINEARITY" or 
                elt[1]=="SHIFT_MAP"):
                nbCalib+=1
        for elt in listCalibFile:
            hdu=fits.open(elt)
            tagCalib=matisseType(hdu[0].header)
            keyDetReadCurnameCalib=hdu[0].header['HIERARCH ESO DET READ CURNAME']
            keyDetChipNameCalib=hdu[0].header['HIERARCH ESO DET CHIP NAME']
            keyDetSeq1DitCalib=hdu[0].header['HIERARCH ESO DET SEQ1 DIT']
            keyInsPilIdCalib=hdu[0].header['HIERARCH ESO INS PIL ID']
            keyInsPinIdCalib=hdu[0].header['HIERARCH ESO INS PIN ID']
            keyInsDilIdCalib=hdu[0].header['HIERARCH ESO INS DIL ID']
            keyInsDinIdCalib=hdu[0].header['HIERARCH ESO INS DIN ID']
            keyInsPolIdCalib=hdu[0].header['HIERARCH ESO INS POL ID']
            keyInsFilIdCalib=hdu[0].header['HIERARCH ESO INS FIL ID']
            keyInsPonIdCalib=hdu[0].header['HIERARCH ESO INS PON ID']
            keyInsFinIdCalib=hdu[0].header['HIERARCH ESO INS FIN ID']
            keyTplStartCalib=hdu[0].header['HIERARCH ESO TPL START']
            hdu.close()
            if (tagCalib=="BADPIX" and (keyDetReadCurnameCalib==keyDetReadCurname and keyDetChipNameCalib==keyDetChipName)):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="OBS_FLATFIELD" and 
                (keyDetChipNameCalib==keyDetChipName and keyDetReadCurnameCalib==keyDetReadCurname and 
                 keyDetSeq1DitCalib==keyDetSeq1Dit  and 
                 ((keyInsPilIdCalib=="PHOTO" and keyInsDilId==keyInsDilIdCalib and keyDetChipName=="HAWAII-2RG") or 
                  (keyInsPinIdCalib=="PHOTO" and keyInsDinId==keyInsDinIdCalib and keyDetChipName=="AQUARIUS")))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="NONLINEARITY" and 
                ((keyDetChipNameCalib=="AQUARIUS" and keyDetChipName=="AQUARIUS" and keyDetReadCurnameCalib==keyDetReadCurname and keyDetSeq1DitCalib==keyDetSeq1Dit) or 
                 (keyDetChipNameCalib=="HAWAII-2RG" and keyDetChipName=="HAWAII-2RG" and keyDetReadCurnameCalib==keyDetReadCurname))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="SHIFT_MAP" and 
                (keyDetChipNameCalib==keyDetChipName and 
                 ((keyInsDilId==keyInsDilIdCalib and keyDetChipName=="HAWAII-2RG") or 
                  (keyInsDinId==keyInsDinIdCalib and keyDetChipName=="AQUARIUS")))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
        if (nbCalib==4):
            status=1
        else:
            status=0
        return [res,status]

    if (action=="ACTION_MAT_EST_SHIFT"):
        nbCalib=0
        for elt in res:
            if (elt[1]=="BADPIX" or 
                elt[1]=="OBS_FLATFIELD" or 
                elt[1]=="NONLINEARITY"):
                nbCalib+=1
        for elt in listCalibFile:
            hdu=fits.open(elt)
            tagCalib=matisseType(hdu[0].header)
            keyDetReadCurnameCalib=hdu[0].header['HIERARCH ESO DET READ CURNAME']
            keyDetChipNameCalib=hdu[0].header['HIERARCH ESO DET CHIP NAME']
            keyDetSeq1DitCalib=hdu[0].header['HIERARCH ESO DET SEQ1 DIT']
            keyInsPilIdCalib=hdu[0].header['HIERARCH ESO INS PIL ID']
            keyInsPinIdCalib=hdu[0].header['HIERARCH ESO INS PIN ID']
            keyInsDilIdCalib=hdu[0].header['HIERARCH ESO INS DIL ID']
            keyInsDinIdCalib=hdu[0].header['HIERARCH ESO INS DIN ID']
            keyInsPolIdCalib=hdu[0].header['HIERARCH ESO INS POL ID']
            keyInsFilIdCalib=hdu[0].header['HIERARCH ESO INS FIL ID']
            keyInsPonIdCalib=hdu[0].header['HIERARCH ESO INS PON ID']
            keyInsFinIdCalib=hdu[0].header['HIERARCH ESO INS FIN ID']
            keyTplStartCalib=hdu[0].header['HIERARCH ESO TPL START']
            hdu.close()
            if (tagCalib=="BADPIX" and (keyDetReadCurnameCalib==keyDetReadCurname and keyDetChipNameCalib==keyDetChipName)):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="OBS_FLATFIELD" and 
                (keyDetChipNameCalib==keyDetChipName and keyDetReadCurnameCalib==keyDetReadCurname and 
                 keyDetSeq1DitCalib==keyDetSeq1Dit  and 
                 ((keyInsPilIdCalib=="PHOTO" and keyInsDilId==keyInsDilIdCalib and keyDetChipName=="HAWAII-2RG") or 
                  (keyInsPinIdCalib=="PHOTO" and keyInsDinId==keyInsDinIdCalib and keyDetChipName=="AQUARIUS")))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
            if (tagCalib=="NONLINEARITY" and 
                ((keyDetChipNameCalib=="AQUARIUS" and keyDetChipName=="AQUARIUS" and keyDetReadCurnameCalib==keyDetReadCurname and keyDetSeq1DitCalib==keyDetSeq1Dit) or 
                 (keyDetChipNameCalib=="HAWAII-2RG" and keyDetChipName=="HAWAII-2RG" and keyDetReadCurnameCalib==keyDetReadCurname))):
                idx=-1
                cpt=0
                for elt2 in res:
                    if (elt2[1]==tagCalib):
                        idx=cpt
                    cpt+=1
                if (idx > -1):
                    hdu=fits.open(res[idx][0])
                    keyTplStartPrevious=hdu[0].header['HIERARCH ESO TPL START']
                    hdu.close()
                    if (keyTplStartCalib >= keyTplStartPrevious):
                        del res[idx]
                        res.append([elt,tagCalib])
                else:
                    res.append([elt,tagCalib])
                    nbCalib+=1
        if (nbCalib==3):
            status=1
        else:
            status=0
        return [res,status]


    return [res,0]

def matisseRecipes(action):

    if (action=="ACTION_MAT_CAL_DET_SLOW_SPEED"):
        return ["mat_cal_det","--gain=2.73 --darklimit=100.0 --flatlimit=0.3 --max_nonlinear_range=36000.0 --max_abs_deviation=2000.0 -max_rel_deviation=0.01"]
    if (action=="ACTION_MAT_CAL_DET_FAST_SPEED"):
        return ["mat_cal_det","--gain=2.60 --darklimit=100.0 --flatlimit=0.3 --max_nonlinear_range=36000.0 --max_abs_deviation=2000.0 -max_rel_deviation=0.01"]
    if (action=="ACTION_MAT_CAL_DET_LOW_GAIN"):
        return ["mat_cal_det","--gain=190.0 --darklimit=100.0 --flatlimit=0.2 --max_nonlinear_range=36000.0 --max_abs_deviation=2000.0 -max_rel_deviation=0.02"]
    if (action=="ACTION_MAT_CAL_DET_HIGH_GAIN"):
        return ["mat_cal_det","--gain=20.0 --darklimit=200.0 --flatlimit=0.2 --max_nonlinear_range=36000.0 --max_abs_deviation=2000.0 -max_rel_deviation=0.01"]
    if (action=="ACTION_MAT_EST_FLAT"):
        return ["mat_est_flat","--obsflat_type=det"]
    if (action=="ACTION_MAT_EST_SHIFT"):
        return ["mat_est_shift",""]
    if (action=="ACTION_MAT_EST_KAPPA"):
        return ["mat_est_kappa",""]
    if (action=="ACTION_MAT_EST_KAPPA"):
        return ["mat_est_kappa",""]
    if (action=="ACTION_MAT_RAW_ESTIMATES"):
        return ["mat_raw_estimates",""]
    if (action=="ACTION_MAT_IM_BASIC"):
        return ["mat_im_basic",""]
    if (action=="ACTION_MAT_IM_EXTENDED"):
        return ["mat_im_extended",""]
    if (action=="ACTION_MAT_IM_REM"):
        return ["mat_im_rem",""]
    return ["",""]

def matisseAction(header,tag):

    keyDetName=header['HIERARCH ESO DET NAME']
    keyDetReadCurname=header['HIERARCH ESO DET READ CURNAME']

    if ((tag =="DARK" or tag=="FLAT") and keyDetName=="MATISSE-LM" and keyDetReadCurname=="SCI-SLOW-SPEED"):
        return "ACTION_MAT_CAL_DET_SLOW_SPEED"
    if ((tag =="DARK" or tag=="FLAT") and keyDetName=="MATISSE-LM" and keyDetReadCurname=="SCI-FAST-SPEED"):
        return "ACTION_MAT_CAL_DET_FAST_SPEED"
    if ((tag =="DARK" or tag=="FLAT") and keyDetName=="MATISSE-N" and keyDetReadCurname=="SCI-LOW-GAIN"):
        return "ACTION_MAT_CAL_DET_LOW_GAIN"
    if ((tag =="DARK" or tag=="FLAT") and keyDetName=="MATISSE-N" and keyDetReadCurname=="SCI-HIGH-GAIN"):
        return "ACTION_MAT_CAL_DET_HIGH_GAIN"
    if (tag =="OBSDARK" or tag=="OBSFLAT"):
        return "ACTION_MAT_EST_FLAT"
    if (tag =="DISTOR_HOTDARK" or tag=="DISTOR_IMAGES" or tag =="SPECTRA_HOTDARK" or tag=="SPECTRA_IMAGES" ):
        return "ACTION_MAT_EST_SHIFT"
    if (tag =="KAPPA_HOTDARK" or tag=="KAPPA_SRC" or tag =="KAPPA_SKY" or tag=="KAPPA_OBJ" ):
        return "ACTION_MAT_EST_KAPPA"
    if (tag =="TARGET_RAW" or tag=="CALIB_RAW" or tag =="HOT_DARK" or tag=="CALIB_SRC_RAW" ):
        return "ACTION_MAT_RAW_ESTIMATES"
    if (tag =="IM_COLD"):
        return "ACTION_MAT_IM_BASIC"
    if (tag =="IM_FLAT" or tag=="IM_DARK"):
        return "ACTION_MAT_IM_EXTENDED"
    if (tag =="IM_PERIODIC"):
        return "ACTION_MAT_IM_REM"
    return "NO-ACTION"

def matisseType(header):
    res=""
    catg=None
    typ=None
    tech=None
    try:
        catg=header['HIERARCH ESO PRO CATG']
    except:
        try:
            catg = header['HIERARCH ESO DPR CATG']
            typ  = header['HIERARCH ESO DPR TYPE']
            tech = header['HIERARCH ESO DPR TECH']
        except:
            pass
    if (catg  =="CALIB" and typ=="DARK,DETCAL" and tech=="IMAGE") or (catg == "CALIB" and typ == "DARK" and tech=="IMAGE,DETCHAR"):
        res="DARK"
    elif (catg=="CALIB" and typ=="FLAT,DETCAL" and tech=="IMAGE") or (catg == "CALIB" and typ == "FLAT" and tech=="IMAGE,DETCHAR"):
        res="FLAT"
    elif (catg=="CALIB" and (typ=="DARK" or typ=="FLAT,OFF") and tech=="SPECTRUM") :
        res="OBSDARK"
    elif (catg=="CALIB" and (typ=="FLAT" or typ=="FLAT,BLACKBODY") and tech=="SPECTRUM") :
        res="OBSFLAT"
    elif (catg=="CALIB" and typ=="DARK,WAVE" and tech=="IMAGE") or (catg == "CALIB" and typ == "DARK" and tech == "IMAGE"):
        res="DISTOR_HOTDARK"
    elif (catg=="CALIB" and typ=="SOURCE,WAVE" and tech=="IMAGE") or (catg == "CALIB" and typ == "WAVE,LAMP,PINHOLE" and tech == "SPECTRUM"):
        res="DISTOR_IMAGES"
    elif (catg=="CALIB" and typ=="SOURCE,LAMP" and tech=="SPECTRUM") or (catg == "CALIB" and typ == "WAVE,LAMP,SLIT" and tech == "SPECTRUM"):
        res="SPECTRA_HOTDARK"
    elif (catg=="CALIB" and typ=="SOURCE,WAVE" and tech=="SPECTRUM") or (catg == "CALIB" and typ == "WAVE,LAMP,FOIL" and tech == "SPECTRUM"):
        res="SPECTRA_IMAGES"
    elif (catg=="CALIB" and typ=="DARK,FLUX" and tech=="IMAGE") or (catg == "CALIB" and typ == "KAPPA,BACKGROUND" and tech == "SPECTRUM"):
        res="KAPPA_HOTDARK"
    elif (catg=="CALIB" and typ=="SOURCE,FLUX" and tech=="IMAGE") or (catg == "CALIB" and typ == "KAPPA,LAMP" and tech == "SPECTRUM"):
        res="KAPPA_SRC"
    elif (catg=="SCIENCE" and typ=="OBJECT" and tech=="IMAGE") :
        res="TARGET_RAW"
    elif (catg=="CALIB" and typ=="OBJECT" and tech=="IMAGE") :
        res="CALIB_RAW"
    elif (catg=="CALIB" and typ=="DARK,IMB" and tech=="IMAGE") or (catg=="CALIB" and typ=="DARK" and tech=="IMAGE,BASIC"):
        res="IM_COLD"
    elif (catg=="CALIB" and typ=="FLAT,IME" and tech=="IMAGE") or (catg=="CALIB" and typ=="FLAT" and tech=="IMAGE,EXTENDED"):
        res="IM_FLAT"
    elif (catg=="CALIB" and typ=="DARK,IME" and tech=="IMAGE") or (catg=="CALIB" and typ=="DARK" and tech=="IMAGE,EXTENDED"):
        res="IM_DARK"
    elif (catg=="CALIB" and typ=="DARK,FLAT" and tech=="IMAGE") or (catg=="CALIB" and typ=="FLAT,LAMP" and tech=="IMAGE,REMANENCE"):
        res="IM_PERIODIC"
    elif (catg=="CALIB" and typ=="DARK" and tech=="INTERFEROMETRY") :
        res="HOT_DARK"
    elif (catg=="CALIB" and (typ=="SOURCE" or typ=="SOURCE,FLUX") and tech=="INTERFEROMETRY") :
        res="CALIB_SRC_RAW"
    elif ((catg=="SCIENCE" or catg=="TEST") and typ=="OBJECT" and tech=="INTERFEROMETRY") :
        res="TARGET_RAW"
    elif (catg == "TEST" and typ == "STD" and tech == "INTERFEROMETRY") or (catg == "CALIB" and typ == "OBJECT" and tech == "INTERFEROMETRY") or (catg == "CALIB" and typ == "OBJECT,FLUX" and tech == "INTERFEROMETRY") : 
        res="CALIB_RAW"
    elif (catg == "TEST"  or catg=="CALIB") and typ == "SKY" and tech == "INTERFEROMETRY" : 
        res="SKY_RAW"
    else:
        res=catg
    return res



