#function file filter to just return all files from list
from datetime import datetime, timedelta

def all_files(jdata):
    jdata_out = []
    for f in jdata:
        jdata_out.append({
            "filename": f["filename"],
            "last_access_time": f["last_access_time"],
            "last_write_time": f["last_write_time"],
            "file_size": f["file_size"]
        })
    return jdata_out


def vh_trackcore(jdata):
    filestohunt = [
        'VH'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def hb_update(jdata):
    filestohunt = [
        'HB_CBCS_update_',
        'HB_CBCS_LEGAL_update'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def cdm_files(jdata):
    filestohunt = [
        'HB_CDM_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def smart_files(jdata):
    filestohunt = [
        'upload.dat'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def smartb_files(jdata):
    filestohunt = [
        'uploadb.dat'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def cbord_demographics(jdata):
    filestohunt = [
        '_CBORD_Demographics.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def vh_impress(jdata):
    filestohunt = [
        'VH_Impress.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def eprescriptions(jdata):
    timestamp = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    filestohunt = [
        'DSH_electronic_prescription_'+timestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def ihms_daily_note(jdata):
    filestohunt = [
        'IHMSDailyNote.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def dawn_files(jdata):
    filestohunt = [
        'ED_Census_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def xclaims_835_files(jdata):
    filestohunt = [
        'EFT_835',
        'CHK_835'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if p in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def all_837_files(jdata):
    filestohunt = [
        'MEDASSETS_837I_',
        'MEDASSETS_837P_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def only_837I_files(jdata):
    filestohunt = [
        'MEDASSETS_837I_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def only_837P_files(jdata):
    filestohunt = [
        'MEDASSETS_837P_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def ach_files(jdata):
    filestohunt = [
        'ACH.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def ahcccs_270_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'AHCCCS'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('1.270'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
            })
    return jdata_out

def ahcccs_271_files(jdata):
    datestamp = (datetime.now() - timedelta(1)).strftime('%y%m%d')
    filestohunt = [
        'AZD271-020107-'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.TXT'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def ar_amclnica_files(jdata):
    datestamp = datetime.today().strftime('%y%m')
    filestohunt = [
        'AR'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('A.MCLNIC'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def apptrmdr_files(jdata):
    filestohunt = [
        'ApptRmdr_FMD'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def azd271_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'AZD271-020107-'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def c1000_files(jdata):
    filestohunt = [
        'PIM_EXP_ApptReminder_1000_Campaign_Gen_EngSpn_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def cardinal_files(jdata):
    filestohunt = [
        '0019.'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def interim_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'INTERIM'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def him_files(jdata):
    filestohunt = [
        'HIM'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def willow_files(jdata):
    filestohunt = [
        '_WC.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def gl_extract_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'EPIC_GL_Report'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.csv'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pbgl_extract_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PBGL'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('_Report.csv'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def hpm_provider_files(jdata):
    filestohunt = [
        'HPM_PROVIDER.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def hpm_har_pb_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HPM_HAR_PB_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def hpm_har_hb_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HPM_HAR_HB_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def mfm_hbven_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HBVENB'+datestamp,
        'HBVENP'+datestamp,
        'HBVEND'+datestamp,
        'HBINVREF'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def mfm_pbven_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PBVENB'+datestamp,
        'PBVENP'+datestamp,
        'PBVEND'+datestamp,
        'PBINVREF'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def mfm_hbgl_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HBGL'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def mfm_pbgl_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PBGL'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def hbimport_notes_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HB_EPIC_IMPORT_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('TXT'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def pbimport_notes_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PB_EPIC_IMPORT_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('TXT'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def medassets_reprice_files(jdata):
    datestamp = datetime.today().strftime('%y%m')
    skip_date = datetime.today().strftime('%y%m%d')
    skip_file = 'AR'+skip_date+'A.MCLNIC'
    filestohunt = [
        'RA.MCLNIC',
        'RB.MCLNIC',
        'RC.MCLNIC'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p) and datestamp in f["filename"] and skip_file not in f["filename"] or f["filename"].startswith('MEDASSETS_837'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def patchgpost_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PA'+datestamp,
        'MEDASSETSPATCHGPOST_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def mclnic_adjust_files(jdata):
    datestamp = datetime.today().strftime('%y%m%d')
    filestohunt = [
        'AR'+datestamp+'B.MCLNIC',
        'AR'+datestamp+'C.MCLNIC',
        'AR'+datestamp+'D.MCLNIC'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def reprice_files(jdata):
    filestohunt = [
        'reprice.txt',
        'repriceB.txt',
        'repriceC.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def medassets_notes_files(jdata):
    filestohunt = [
        '_MEDASSETS_EPIC_NOTES.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def era_hbload_files(jdata):
    filestohunt = [
        '.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p) and 'pb_' not in f["filename"] and 'error.txt' not in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def era_pbload_files(jdata):
    filestohunt = [
        '.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p) and 'pb_' in f["filename"] and 'error.txt' not in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def rwb_files(jdata):
    datestamp = datetime.today().strftime('%Y-%m')
    filestohunt = [
        'nThrive_HB_CDM_Revenue_Usage_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def eprescriptions_files(jdata):
    datestamp = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    filestohunt = [
        'DSH_electronic_prescription_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pbclaimrpt_files(jdata):
    filestohunt = [
        'pbclaimreport'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def idG_files(jdata):
    filestohunt = [
        'KRONOS-'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def claimrun_files(jdata):
    filestohunt = [
        'EPIC_ClaimRunReport'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def medassetspat_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'MEDASSETSPATDEMO_ICD_'+datestamp,
        'MEDASSETSPATHIM_'+datestamp,
        'MEDASSETSPATCHG_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) or 'CW.txt' in f["filename"] or 'MEDASSETSPATDEMO.txt' in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def velocity_files(jdata):
    filestohunt = [
        'velocityfull.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def rsli_files(jdata):
    filestohunt = [
        'VALLEYWISEHEALTH_VAI_VCI_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def matrixcos_files(jdata):
    filestohunt = [
        'Master_Valleywise_',
        'Sub_Valleywise_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def ccaexcept_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'CCA_EXCEPTIONS_'+datestamp+'_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def avaya_4000_files(jdata):
    filestohunt = [
        'PIM_EXP_Survey_4000_Campaign_EngSpn'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def colnote_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'colnote_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def delete_smart_files(jdata):
    fmt = "%Y-%m-%d %H:%M:%S"
    del_now = datetime.now() - timedelta(minutes=30)
    filestohunt = [
        'smart'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                if datetime.strptime(f["last_write_time"], fmt) < del_now:
                    jdata_out.append({
                        "filename": f["filename"],
                        "last_access_time": f["last_access_time"],
                        "last_write_time": f["last_write_time"],
                        "file_size": f["file_size"]
                    })
                else:
                    continue
    return jdata_out

def atb_files(jdata):
    filestohunt = [
        'ATB'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if p in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def delete_ccaimport_files(jdata):
    filestohunt = [
        'CCAimport.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def hb_report_files(jdata):
    filestohunt = [
        'HB_MONTHLY_GL_Report',
        'HB_Monthly_GL_Report'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pb_report_files(jdata):
    filestohunt = [
        'PB_Monthly_GL',
        'PB_MONTHLY_GL'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and 'Error' not in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def midas_cpt_files(jdata):
    filestohunt = [
        'MidasCPT.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def midas_ed_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'midas_ed_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def medassets_zerobal_files(jdata):
    filestohunt = [
        'MEDASSETS_EPIC_ZEROBALANCE_NOTES.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def delete_adjustB_files(jdata):
    filestohunt = [
        'medassetsB.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def delete_c1000_files(jdata):
    filestohunt = [
        'ApptRmdr_1000_Contact_Gen_EngSpn.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def delete_cold_files(jdata):
    filestohunt = [
        'ApptRmdr_FMD'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def kronos_export_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        datestamp+'_KRONOSUserExport.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def mrm_term_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'MIHS_MRM_Employee_Terms_'+datestamp+'.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def delete_IHMS_files(jdata):
    filestohunt = [
        'IHMSDailyNote.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hb_export_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HB_EPIC_EXPORT_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def hb_payer_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HB_EPIC_PAYER_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def hb_user_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HB_EPIC_USER_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pb_export_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PB_EPIC_EXPORT_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pb_payer_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PB_EPIC_PAYER_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pb_user_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'PB_EPIC_USER_NOTESPOSTING_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def uhc_apipa_files(jdata):
    filestohunt = [
        'APIPADAILY.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def uhc_vision_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'Benefits_UHC_Vision_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def umr_benefits_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'Benefits_UMR_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlife_benefits_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'Benefits_MetLife_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlaw_benefits_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'A9900050_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def nrc_daily_files(jdata):
    filestohunt = [
        'VH_DENTAL_',
        'VH_CLINICOP_',
        'VH_HOSPITAL_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def reprice_error_files(jdata):
    filestohunt = [
        'repriceerror',
        'repriceBerror',
        'repriceCerror'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def rt_vh_nrc_files(jdata):
    filestohunt = [
        'RT_VH_DENTAL_',
        'RT_VH_HOSPITAL_',
        'RT_VH_CLINICOP_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def ccc_payroll_files(jdata):
    filestohunt = [
        'TEST2676_',
        '2676_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def perceptyx_obs_files(jdata):
    filestohunt = [
        'mihs_onboard_',
        'valywi_onboard_term'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def perceptyx_exit_files(jdata):
    filestohunt = [
        'valleywise_exitfile_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def reimb_correct_files(jdata):
    filestohunt = [
        'reimbcorrecterror.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def delete_reimb_correct_files(jdata):
    filestohunt = [
        'reimbcorrect.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def masterfiles_files(jdata):
    filestohunt = [
        'DepartmentCodes_',
        'InsuranceCompanyCodes_',
        'PhysicianCodes_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def coe_claims_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'MCOEVHMC.'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def vwh_pub_web_bkups(jdata):
    datestamp = datetime.today().strftime('%Y-%m-%d')
    filestohunt = [
        'backup_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def medassets_hist_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'MEDASSETSNote'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def imprivata_ser_files(jdata):
    filestohunt = [
        'SER-'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.csv'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def send_medvoice_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'OE'+datestamp+'_',
        'OJ'+datestamp+'_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def hb_mds_update_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'HB_MDS_update_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hb_mds_withdraw_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'HB_MDS_withdraw_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hb_mds_inventory_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'HB_MDS_inventory_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hb_mds_assign_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'HB_MDS_assign_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def kronos_to_snow_files(jdata):
    filestohunt = [
        'kronos_active_cc_dept.csv',
        'kronos_active_jobs.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out


def sherloq_selfpay_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'sherloq'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def sherloq_notes_files(jdata):
    filestohunt = [
        'SHERLOQNote.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })

    return jdata_out

def avaya_gen_pom(jdata):
    filestohunt = [
        'Gen POM Incoming.err',
        'Gen POM Incoming.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def medassets_837i_files(jdata):
    filestohunt = [
        'MEDASSETS_837I_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def medassets_837p_files(jdata):
    filestohunt = [
        'MEDASSETS_837P_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pm11_files(jdata):
    filestohunt = [
        'pmjobexport.txt',
        'pmorientation.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def midas_emp_files(jdata):
    filestohunt = [
        'Midas_Employees.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def epicbpi_files(jdata):
    filestohunt = [
        'epicbpi.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def cbord_ded_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'CBORD_DED_OUT_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def sendhb_mds_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'HB_MDS_inventory_'+datestamp,
        'HB_MDS_update_'+datestamp,
        'HB_MDS_withdraw_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def wfan_payroll_files(jdata):
    filestohunt = [
        'payroll.txt',
        'Payroll.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hpm_payroll_files(jdata):
    filestohunt = [
        'HPM'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def demo_ad_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'Demographics_AD_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hciq_files(jdata):
    filestohunt = [
        'DepM.txt',
        'ITMI.txt',
        'PurH.txt',
        'ItmM.txt',
        'InvH.txt',
        'InvD.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def dsh_files(jdata):
    datestamp = datetime.today().strftime('%Y-%m')
    filestohunt = [
        'DSH_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def avaya_rts_8k(jdata):
    filestohunt = [
        'RTS_8000_Contacts_EngSpn.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def nhi_notes_files(jdata):
    datestamp = datetime.today().strftime('%m%d%Y')
    filestohunt = [
        'nhinotes_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def pharmhs_pap_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'PAP_'+datestamp,
        'MIHS_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlaw_ben_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'A9900050_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def bloodbank_files(jdata):
    filestohunt = [
        'PDBfile.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def ihms_files(jdata):
    datestamp = (datetime.now() - timedelta(1)).strftime('%Y%m%d')
    filestohunt = [
        'IHMSDailyNote_'+datestamp+'.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hartford_muw_files(jdata):
    filestohunt = [
        'Maricopa_County_Special_Healthcare_MUW_Report.txt'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def boe_lab_results_files(jdata):
    filestohunt = [
        '02_AZ_MARICOPACOUNTYSPECIALTYHEALTH_PROD_LABS_UHC_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def uhc_roster_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'UHC_FULL_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def vizientinc_files(jdata):
    # datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        '104193_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def vizient_test_files(jdata):
    # datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        '104193'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlife_dental_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'Benefits_Metlife_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlife_eligibility_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'valleyws_elig_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlife_grouplife_files(jdata):
    filestohunt = [
        'Valleywise_grplife'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def metlife_grouplife_test(jdata):
    filestohunt = [
        'ValleywiseTEST_grplife'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p) and f["filename"].endswith('.txt'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out


def medasets_fqhc_files(jdata):
    filestohunt = [
        'FQHCA.txt',
        'FQHCB.txt',
        'FQHCC.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def wellcare_discharge_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        '_care1stdailydischarge.xls'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p) and f["filename"].startswith(datestamp):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def wellcare_claims_files(jdata):
    filestohunt = [
        'MARICOPA'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def agility_cvh_files(jdata):
    filestohunt = [
        'CVHDEMOGRAPHIC'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out
def agility_bvh_files(jdata):
    filestohunt = [
        'BVHORGANIZATION'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def agility_avh_files(jdata):
    filestohunt = [
        'AVHMANAGER'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def volumes_files(jdata):
    filestohunt = [
        '.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def agility_tb_files(jdata):
    datestamp = datetime.today().strftime('%m%d%Y')
    filestohunt = [
        'Agility_TB_'+datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def walgreens_files(jdata):
    filestohunt = [
        '2693_FLATVER4_DELTA_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def avaya_rts_82k(jdata):
    filestohunt = [
        'RTS_8200_Contacts_EngSpn.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def avaya_covid_9k(jdata):
    filestohunt = [
        'COVID_Vaccine_9000_Contacts_EngSpn.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def hb_support_files(jdata):
    filestohunt = [
        '.ffl',
        '.log',
        '.err'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p) and f["filename"].startswith('HB'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def pb_support_files(jdata):
    filestohunt = [
        '.ffl',
        '.log',
        '.err'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p) and f["filename"].startswith('PB'):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def avaya_rts_81k(jdata):
    filestohunt = [
        'RTS_8100_Contacts_EngSpn.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out

def spreadsheet_files(jdata):
    filestohunt = [
        '.xls',
        '.xlsx',
        '.txt'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].endswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def delete_web_bkups(jdata):
    datestamp = (datetime.now() - timedelta(5)).strftime('%Y-%m-%d')
    filestohunt = [
        datestamp
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if p in f["filename"]:
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def managed_care_clm_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'VALLEYWISEAZ_'+datestamp+'_CLM'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def managed_care_mem_files(jdata):
    datestamp = datetime.today().strftime('%Y%m')
    filestohunt = [
        'VALLEYWISEAZ_'+datestamp+'_MEM'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def banner_roster_files(jdata):
    datestamp = datetime.today().strftime('%Y%m%d')
    filestohunt = [
        'BUHP_ROSTER_'
    ]
    jdata_out = []
    for f in jdata:
        for p in filestohunt:
            if f["filename"].startswith(p):
                jdata_out.append({
                    "filename": f["filename"],
                    "last_access_time": f["last_access_time"],
                    "last_write_time": f["last_write_time"],
                    "file_size": f["file_size"]
                })
    return jdata_out

def symplr_new_hires_files(jdata):
    filestohunt = [
        'ValleywiseNewHires.csv'
    ]
    jdata_out = []
    for f in jdata:
        if f["filename"] in filestohunt:
            jdata_out.append({
                "filename": f["filename"],
                "last_access_time": f["last_access_time"],
                "last_write_time": f["last_write_time"],
                "file_size": f["file_size"]
            })
    return jdata_out