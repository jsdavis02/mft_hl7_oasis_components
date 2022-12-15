# Function updates the MSH segment, control number
# for Endovault, to set a unique number, if message is RTF or PDF.

def update_ctrlnum_endo(rtf_json, pdf_json):

    jsons = (rtf_json, pdf_json)
    ctrl_num = 1
    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('MSH') and len(str(j[s]['10'])) > 0:
                j[s].update({'10': str(j[s]['10'])+"-"+str(ctrl_num)})
                ctrl_num += 1
                
    return rtf_json, pdf_json


