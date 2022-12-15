# Function updates the TXA segment, universal id
# for Endovault, if message is RTF or PDF.

def update_txa_12_endo(rtf_json, pdf_json):

    txa_seg = ()
    txa_12 = ""
    suffix = ""
    jsons = (rtf_json, pdf_json)

    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('TXA'):
                txa_seg = j[s]
                txa_12 = txa_seg['12']
                break
    
        for (s, value) in j.items():
            if s.startswith('OBR') and str(j[s]['12']) == "P":
                suffix = "PP"
            else:
                suffix = "FA"
                break
    
        for (s, value) in j.items():
            if s.startswith('OBX') and j[s]['2'] == "ED":
                string = txa_12.split("^")
                new_string = ("^^"+"Endosoft"+string[2])
                txa_seg.update({'12': new_string})
            else:
                string = txa_12.split("^")
                new_string = ("^^"+"Endosoft"+string[2]+suffix)
                txa_seg.update({'12': new_string})

    return rtf_json, pdf_json

